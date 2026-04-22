from app.domains.event.adapter.outbound.persistence.in_memory_event_repository import InMemoryEventRepository
from app.domains.event.application.usecase.event_usecase import CreateEventUseCase, ListEventsUseCase

_event_repo = InMemoryEventRepository()


def get_create_event_usecase() -> CreateEventUseCase:
    return CreateEventUseCase(_event_repo)


def get_list_events_usecase() -> ListEventsUseCase:
    return ListEventsUseCase(_event_repo)
