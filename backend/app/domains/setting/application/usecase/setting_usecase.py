from typing import Any

from app.domains.setting.application.port.setting_repository_port import SettingRepositoryPort
from app.domains.setting.application.request.setting_request import UpdateSettingsRequest
from app.domains.setting.application.response.setting_response import SettingItemResponse, SettingsGroupResponse
from app.domains.setting.domain.entity.setting import SystemSetting
from app.infrastructure.config.settings import settings as runtime_settings

# key → (type_name, label, group)
_SCHEMA: dict[str, tuple[str, str, str]] = {
    "recognition_threshold":               ("float", "얼굴 인식 임계값 (0~1)",           "recognition"),
    "identity_recognition_cooldown_sec":   ("float", "등록 인물 재인식 쿨다운 (초)",     "recognition"),
    "unregistered_recognition_cooldown_sec": ("float", "미등록 인물 재인식 쿨다운 (초)", "recognition"),
    "face_quality_threshold":              ("float", "얼굴 품질 임계값 (0~1)",           "recognition"),
    "multishot_enabled":               ("bool",  "멀티샷 임베딩 학습 활성화",      "recognition"),
    "multishot_min_score":             ("float", "멀티샷 최소 유사도 점수",         "recognition"),
    "cluster_similarity_threshold":    ("float", "미식별 클러스터 유사도 임계값",   "clustering"),
    "cluster_merge_threshold":         ("float", "클러스터 병합 임계값",            "clustering"),
    "cluster_active_window_days":      ("int",   "활성 클러스터 탐색 기간 (일)",    "clustering"),
    "cluster_max_size":                ("int",   "클러스터 최대 멤버 수",           "clustering"),
    "face_recognition_pipeline_enabled": ("bool", "얼굴인식 파이프라인 활성화",     "pipeline"),
    "danger_detection_enabled":        ("bool",  "위험감지 파이프라인 활성화",      "pipeline"),
    "frame_skip":                      ("int",   "프레임 스킵 (1~30)",              "pipeline"),
    "pipeline_capture_interval":       ("float", "파이프라인 캡처 간격 (초)",       "pipeline"),
}


def _cast(type_name: str, raw: str) -> Any:
    if type_name == "float":
        return float(raw)
    if type_name == "int":
        return int(raw)
    if type_name == "bool":
        return raw.lower() in ("true", "1", "yes")
    return raw


def _get_current(key: str) -> str:
    val = getattr(runtime_settings, key, None)
    return str(val) if val is not None else ""


class GetSettingsUseCase:
    def __init__(self, repo: SettingRepositoryPort):
        self._repo = repo

    async def execute(self) -> SettingsGroupResponse:
        saved = {s.key: s.value for s in await self._repo.find_all()}

        recognition, clustering, pipeline = [], [], []
        for key, (type_name, label, group) in _SCHEMA.items():
            value = saved.get(key, _get_current(key))
            item = SettingItemResponse(key=key, value=value, type=type_name, label=label)
            if group == "recognition":
                recognition.append(item)
            elif group == "clustering":
                clustering.append(item)
            else:
                pipeline.append(item)

        return SettingsGroupResponse(
            recognition=recognition,
            clustering=clustering,
            pipeline=pipeline,
        )


class UpdateSettingsUseCase:
    def __init__(self, repo: SettingRepositoryPort):
        self._repo = repo

    async def execute(self, request: UpdateSettingsRequest) -> SettingsGroupResponse:
        for item in request.updates:
            if item.key not in _SCHEMA:
                continue
            type_name, _, _ = _SCHEMA[item.key]
            setting = SystemSetting(key=item.key, value=item.value)
            await self._repo.save(setting)
            casted = _cast(type_name, item.value)
            object.__setattr__(runtime_settings, item.key, casted)

        get_uc = GetSettingsUseCase(self._repo)
        return await get_uc.execute()


class LoadRuntimeSettingsUseCase:
    """앱 시작 시 DB 저장된 설정을 runtime_settings에 반영한다."""

    def __init__(self, repo: SettingRepositoryPort):
        self._repo = repo

    async def execute(self) -> None:
        saved = await self._repo.find_all()
        for s in saved:
            if s.key not in _SCHEMA:
                continue
            type_name, _, _ = _SCHEMA[s.key]
            try:
                casted = _cast(type_name, s.value)
                object.__setattr__(runtime_settings, s.key, casted)
            except Exception:
                pass
