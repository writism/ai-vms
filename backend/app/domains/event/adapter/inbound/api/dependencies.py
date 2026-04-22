from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.event.adapter.outbound.persistence.in_memory_event_repository import InMemoryEventRepository
from app.domains.event.application.port.event_repository_port import EventRepositoryPort
from app.domains.event.application.usecase.event_usecase import CreateEventUseCase, ListEventsUseCase
from app.infrastructure.config.settings import settings

_in_memory_event_repo = InMemoryEventRepository()


def _get_event_repo(session: AsyncSession | None = None) -> EventRepositoryPort:
    if settings.use_database and session:
        from app.domains.event.adapter.outbound.persistence.sqlalchemy_event_repository import SqlAlchemyEventRepository
        return SqlAlchemyEventRepository(session)
    return _in_memory_event_repo


def get_create_event_usecase() -> CreateEventUseCase:
    return CreateEventUseCase(_get_event_repo())


def get_list_events_usecase() -> ListEventsUseCase:
    return ListEventsUseCase(_get_event_repo())
