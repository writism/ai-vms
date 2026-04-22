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
    face_quality_threshold: float = 0.4
    embedding_dimension: int = 512
    use_adaface_fallback: bool = True

    mqtt_broker_url: str = "mqtt://localhost:1883"
    mqtt_topic_prefix: str = "ai-vms"

    openai_api_key: str = ""
    langgraph_model: str = "gpt-4.1-mini"

    use_vlm: bool = False
    vlm_model: str = "Qwen/Qwen2.5-VL-7B-Instruct"

    go2rtc_mode: str = "embedded"
    go2rtc_url: str = "http://localhost:1984"
    go2rtc_direct_url: str = "http://localhost:1984"

    motion_gate_enabled: bool = True
    process_interval_active: float = 0.01
    process_interval_idle: float = 0.2
    frame_skip: int = 3

    danger_detection_enabled: bool = True
    danger_model_path: str = "./models/yolo11-danger.pt"
    action_recognition_enabled: bool = True
    pose_model: str = "mediapipe"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
