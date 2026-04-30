from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI-VMS"
    debug: bool = False

    use_database: bool = False
    database_url: str = "postgresql+asyncpg://aivms:aivms@localhost:5432/aivms"
    redis_url: str = "redis://localhost:6379"
    qdrant_url: str = "http://localhost:6333"

    secret_key: str = "change-me-in-production-min-32-chars"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:3000"

    recognition_threshold: float = 0.68
    face_quality_threshold: float = 0.35
    embedding_dimension: int = 512
    use_adaface_fallback: bool = True
    face_model_name: str = "buffalo_l"
    face_det_size: int = 640
    face_det_score_threshold: float = 0.35
    face_det_roi_size: int = 1600
    face_det_roi_ratio: float = 0.6
    face_quality_size_norm: float = 96.0

    mqtt_broker_url: str = "mqtt://localhost:1883"
    mqtt_topic_prefix: str = "ai-vms"

    openai_api_key: str = ""
    langgraph_model: str = "gpt-4.1-mini"

    use_vlm: bool = False
    vlm_model: str = "Qwen/Qwen2.5-VL-7B-Instruct"

    go2rtc_mode: str = "embedded"
    go2rtc_url: str = "http://localhost:1984"
    go2rtc_direct_url: str = "http://localhost:1984"

    face_recognition_pipeline_enabled: bool = True
    motion_gate_enabled: bool = True
    process_interval_active: float = 0.01
    process_interval_idle: float = 0.2
    frame_skip: int = 3

    danger_detection_enabled: bool = True
    danger_model_path: str = "./models/yolo11-danger.pt"
    action_recognition_enabled: bool = True
    pose_model: str = "mediapipe"

    frame_capture_use_relay: bool = True
    go2rtc_rtsp_host: str = "localhost"
    go2rtc_rtsp_port: int = 8554

    cluster_similarity_threshold: float = 0.50
    cluster_merge_threshold: float = 0.60      # 기존 클러스터 간 병합 임계값
    cluster_recommend_threshold: int = 5
    cluster_window_hours: int = 24
    cluster_active_window_days: int = 7        # find_active_pending 탐색 기간
    cluster_max_size: int = 100
    cluster_topk_anchor: int = 3
    cluster_recent_member_anchor: int = 5

    face_snapshot_padding: float = 0.30
    face_snapshot_min_sharpness: float = 60.0   # Laplacian variance 하한 — 이하면 스냅샷 저장 안 함
    face_snapshot_max_face_ratio: float = 0.65  # 얼굴 bbox가 프레임 대비 이 비율 초과 시 저장 안 함 (너무 가까운 얼굴)
    face_snapshot_min_output_size: int = 200    # 크롭 후 최소 픽셀 — 작으면 Lanczos 업스케일

    multishot_enabled: bool = True
    multishot_min_score: float = 0.88
    multishot_sim_low: float = 0.72
    multishot_sim_high: float = 0.92
    multishot_per_identity_max: int = 20
    multishot_identity_cooldown_sec: float = 60.0
    identity_recognition_cooldown_sec: float = 30.0
    pipeline_queue_maxsize: int = 2
    pipeline_capture_interval: float = 0.05
    pipeline_best_frame_window: float = 1.0  # 이 시간(초) 내 캡처된 프레임 중 최고화질 1장만 처리

    model_config = {"env_file": ("../.env", ".env"), "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
