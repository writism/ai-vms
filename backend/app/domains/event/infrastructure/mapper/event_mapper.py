from app.domains.event.domain.entity.event import Event, EventType
from app.domains.event.infrastructure.orm.event_orm import EventORM


class EventMapper:
    @staticmethod
    def to_entity(orm: EventORM) -> Event:
        return Event(
            id=orm.id,
            event_type=EventType(orm.event_type),
            camera_id=orm.camera_id,
            identity_id=orm.identity_id,
            danger_event_id=orm.danger_event_id,
            description=orm.description,
            metadata=orm.metadata_json,
            snapshot_path=orm.snapshot_path,
            created_at=orm.created_at,
        )

    @staticmethod
    def to_orm(entity: Event) -> EventORM:
        return EventORM(
            id=entity.id,
            event_type=entity.event_type.value,
            camera_id=entity.camera_id,
            identity_id=entity.identity_id,
            danger_event_id=entity.danger_event_id,
            description=entity.description,
            metadata_json=entity.metadata,
            snapshot_path=entity.snapshot_path,
            created_at=entity.created_at,
        )
