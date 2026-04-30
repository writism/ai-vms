from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from app.infrastructure.config.settings import settings

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DetectedFace:
    bbox: tuple[int, int, int, int]
    confidence: float
    embedding: list[float]
    quality_score: float


def _detect_gpu() -> tuple[bool, str]:
    try:
        import numpy as _np
        import onnxruntime as ort
        from onnx import TensorProto, helper, numpy_helper

        if "CUDAExecutionProvider" not in ort.get_available_providers():
            return False, "CPUExecutionProvider"

        # Build a minimal Conv graph to verify cuDNN actually works on this GPU
        X = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, 1, 3, 3])
        Y = helper.make_tensor_value_info("Y", TensorProto.FLOAT, None)
        W = numpy_helper.from_array(
            _np.ones((1, 1, 1, 1), dtype=_np.float32), name="W"
        )
        conv = helper.make_node("Conv", ["X", "W"], ["Y"])
        graph = helper.make_graph([conv], "gpu_test", [X], [Y], [W])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
        model.ir_version = 10

        sess = ort.InferenceSession(
            model.SerializeToString(),
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
        )
        if "CUDAExecutionProvider" not in sess.get_providers():
            return False, "CPUExecutionProvider"

        sess.run(None, {"X": _np.ones((1, 1, 3, 3), dtype=_np.float32)})
        return True, "CUDAExecutionProvider"
    except Exception as e:
        logger.info("GPU Conv test failed, using CPU: %s", e)
        return False, "CPUExecutionProvider"


class InsightFaceService:
    def __init__(self) -> None:
        self._app: Any = None
        self._loaded = False
        self._use_gpu = False
        self._provider = "CPUExecutionProvider"

    async def load_models(self) -> bool:
        try:
            from insightface.app import FaceAnalysis

            loop = asyncio.get_event_loop()
            self._use_gpu, self._provider = await loop.run_in_executor(None, _detect_gpu)

            if self._use_gpu:
                providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            else:
                providers = ["CPUExecutionProvider"]

            det_size = (settings.face_det_size, settings.face_det_size)

            self._app = FaceAnalysis(
                name=settings.face_model_name,
                providers=providers,
            )
            self._app.prepare(ctx_id=0 if self._use_gpu else -1, det_size=det_size)
            self._loaded = True
            logger.info(
                "InsightFace loaded: model=%s, provider=%s, det_size=%s",
                settings.face_model_name,
                self._provider,
                det_size,
            )
            return True
        except Exception as e:
            logger.warning("InsightFace models not available: %s", e)
            self._loaded = False
            return False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def use_gpu(self) -> bool:
        return self._use_gpu

    async def detect_and_embed(self, frame: np.ndarray) -> list[DetectedFace]:
        if not self._loaded:
            return []

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._detect_two_pass, frame)

    async def detect_and_embed_for_registration(self, frame: np.ndarray) -> list[DetectedFace]:
        """등록 전용: 일반 검출 실패 시 패딩 추가 후 재시도 (크롭 이미지 대응)."""
        results = await self.detect_and_embed(frame)
        if results:
            return results
        if not self._loaded:
            return []
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._detect_padded_fallback, frame)

    def _detect_padded_fallback(self, frame: np.ndarray) -> list[DetectedFace]:
        """이미 잘린 얼굴 크롭에 50% 패딩을 추가해 InsightFace 컨텍스트 확보."""
        import cv2

        h, w = frame.shape[:2]
        pad_h = max(h // 2, 80)
        pad_w = max(w // 2, 80)
        padded = cv2.copyMakeBorder(
            frame, pad_h, pad_h, pad_w, pad_w,
            cv2.BORDER_CONSTANT, value=(128, 128, 128),
        )
        raw = self._app.get(padded)
        if not raw:
            return []
        # offset=(-pad_w, -pad_h) 로 원본 좌표계로 변환
        results = self._build_results(padded, raw, offset=(-pad_w, -pad_h))
        if results:
            logger.debug(
                "padded-fallback detection hit faces=%d pad=(%d,%d)",
                len(results), pad_w, pad_h,
            )
        return results

    def _detect_two_pass(self, frame: np.ndarray) -> list[DetectedFace]:
        h, w = frame.shape[:2]
        results = self._build_results(frame, self._app.get(frame), offset=(0, 0))

        # 작은 얼굴(원거리/광각 PTZ) → 중앙 ROI를 큰 입력으로 다시 한 번
        if not results:
            roi_size = settings.face_det_roi_size
            ratio = settings.face_det_roi_ratio
            if roi_size > 0 and 0 < ratio <= 1.0 and min(w, h) > 0:
                rw = int(w * ratio)
                rh = int(h * ratio)
                ox = (w - rw) // 2
                oy = (h - rh) // 2
                roi = frame[oy : oy + rh, ox : ox + rw]
                if roi.size > 0:
                    roi_results = self._build_results(
                        roi, self._app.get(roi), offset=(ox, oy)
                    )
                    if roi_results:
                        logger.debug(
                            "2-pass ROI detection hit faces=%d roi=%dx%d",
                            len(roi_results), rw, rh,
                        )
                    results = roi_results

        return results

    def _build_results(
        self, frame: np.ndarray, faces: list[Any], offset: tuple[int, int]
    ) -> list[DetectedFace]:
        import cv2

        h, w = frame.shape[:2]
        ox, oy = offset
        size_norm = max(1.0, settings.face_quality_size_norm)
        size_norm_sq = size_norm * size_norm
        det_score_min = settings.face_det_score_threshold

        results: list[DetectedFace] = []
        for face in faces:
            if face.det_score < det_score_min:
                continue

            bbox = tuple(int(v) for v in face.bbox)
            x1, y1, x2, y2 = bbox
            bw = max(1, x2 - x1)
            bh = max(1, y2 - y1)

            cx1 = max(0, x1)
            cy1 = max(0, y1)
            cx2 = min(w, x2)
            cy2 = min(h, y2)
            face_crop = frame[cy1:cy2, cx1:cx2]
            if face_crop.size > 0:
                gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
                sharpness_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
            else:
                sharpness_var = 0.0

            confidence = float(face.det_score)
            sharpness_score = min(sharpness_var / 500.0, 1.0)
            size_score = min((bw * bh) / size_norm_sq, 1.0)
            quality = confidence * 0.4 + sharpness_score * 0.4 + size_score * 0.2

            embedding = face.normed_embedding.tolist()

            results.append(
                DetectedFace(
                    bbox=(x1 + ox, y1 + oy, x2 + ox, y2 + oy),
                    confidence=confidence,
                    embedding=embedding,
                    quality_score=round(quality, 3),
                )
            )

        return results


insightface_service = InsightFaceService()
