"""SQLAlchemy 메타데이터 등록을 보장하기 위한 ORM 모듈 일괄 import.

각 도메인 ORM은 모듈이 import되어야만 ``Base.metadata``에 등록된다.
별도 sub-session(예: 백그라운드 파이프라인)이 일부 ORM만 직접 import할 때,
다른 도메인의 ForeignKey 정의가 있는데 해당 테이블이 메타데이터에 없으면
``Foreign key associated with column ... could not find table ...`` 오류가
발생한다. 이 모듈은 한 번만 import하면 모든 ORM이 메타데이터에 등록되도록
하기 위한 단일 진입점이다.
"""

from app.domains.alert.infrastructure.orm import alert_orm as _alert_orm  # noqa: F401
from app.domains.auth.infrastructure.orm import user_orm as _user_orm  # noqa: F401
from app.domains.camera.infrastructure.orm import camera_orm as _camera_orm  # noqa: F401
from app.domains.event.infrastructure.orm import event_orm as _event_orm  # noqa: F401
from app.domains.face.infrastructure.orm import face_orm as _face_orm  # noqa: F401
