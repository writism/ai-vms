import numpy as np


def compute_outlier_similarities(embeddings: list[list[float]]) -> list[float]:
    """각 임베딩의 centroid 대비 코사인 유사도를 반환한다."""
    arr = np.array(embeddings, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    normalized = arr / np.maximum(norms, 1e-8)
    mean_emb = normalized.mean(axis=0)
    mean_norm = np.linalg.norm(mean_emb)
    if mean_norm > 0:
        mean_emb = mean_emb / mean_norm
    return (normalized @ mean_emb).tolist()
