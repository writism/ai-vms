import logging

import numpy as np

from app.infrastructure.ai.insightface_service import insightface_service
from app.infrastructure.ai.yolo_service import yolo_service
from app.infrastructure.langgraph.state import AgentState, DetectionResult

logger = logging.getLogger(__name__)


async def detector_node(state: AgentState) -> AgentState:
    frame_data = state.get("frame_data")
    if frame_data is None:
        return {**state, "error": "No frame data available"}

    frame = np.frombuffer(frame_data, dtype=np.uint8)
    import cv2
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    if frame is None:
        return {**state, "error": "Failed to decode frame"}

    results: list[DetectionResult] = []

    if insightface_service.is_loaded:
        faces = await insightface_service.detect_and_embed(frame)
        for face in faces:
            results.append(
                DetectionResult(
                    type="face",
                    label="face_detected",
                    confidence=face.confidence,
                    bbox=face.bbox,
                    embedding=face.embedding,
                )
            )
        logger.info("Detector: found %d faces", len(faces))

    if yolo_service.is_loaded:
        dangers = await yolo_service.detect(frame)
        for d in dangers:
            results.append(
                DetectionResult(
                    type="danger",
                    label=d.class_name,
                    confidence=d.confidence,
                    bbox=d.bbox,
                )
            )
        logger.info("Detector: found %d danger objects", len(dangers))

    return {**state, "detection_results": results}
