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
        faces = await loop.run_in_executor(None, self._app.get, frame)
        results: list[DetectedFace] = []

        for face in faces:
            if face.det_score < settings.face_quality_threshold:
                continue

            bbox = tuple(int(v) for v in face.bbox)
            embedding = face.normed_embedding.tolist()

            h, w = frame.shape[:2]
            bw = bbox[2] - bbox[0]
            bh = bbox[3] - bbox[1]
            quality = min(1.0, (bw * bh) / (w * h) * 50)

            results.append(
                DetectedFace(
                    bbox=(bbox[0], bbox[1], bbox[2], bbox[3]),
                    confidence=float(face.det_score),
                    embedding=embedding,
                    quality_score=quality,
                )
            )

        return results


insightface_service = InsightFaceService()
