import pytest
from unittest.mock import AsyncMock, Mock
from uuid import UUID
from datetime import datetime

from tus_datos_prueba.app.adapters.sessions import SessionQueries, SessionMutations
from tus_datos_prueba.app.services.sessions import SessionService
from tus_datos_prueba.app.services.events import EventService
from tus_datos_prueba.app.services.assistants import AssistantService
from tus_datos_prueba.utils.jwt import has_permission
from tus_datos_prueba.app.models.sessions import SessionResponse
from tus_datos_prueba.models.events import EventStatus, AssistantType


@pytest.fixture
def session_service():
    svc = Mock(spec=SessionService)
    return svc


@pytest.fixture
def event_service():
    svc = Mock(spec=EventService)
    return svc


@pytest.fixture
def assistant_service():
    svc = Mock(spec=AssistantService)
    return svc


@pytest.fixture
def info(session_service, event_service, assistant_service):
    return Mock(
        context={
            "session": {
                "perms": {
                    "assistants": ["list", "get", "create", "update", "delete"]
                }
            },
            "session_service": session_service,
            "event_service": event_service,
            "assistant_service": assistant_service
        }
    )


@pytest.mark.asyncio
async def test_session_list(info):
    """
    Test listing sessions via SessionQueries.session_list
    """
    has_permission(info.context["session"], "assistants", "list")

    session1 = Mock()
    session2 = Mock()
    info.context["session_service"].list_sessions = AsyncMock(return_value=[session1, session2])

    query = SessionQueries()
    result = await query.session_list(info, event_id=UUID("12345678-1234-5678-1234-567812345678"), limit=10, offset=0)

    assert len(result) == 2
    info.context["session_service"].list_sessions.assert_awaited_once_with(
        UUID("12345678-1234-5678-1234-567812345678"), 10, 0
    )
    assert all(isinstance(s, SessionResponse) for s in result)


@pytest.mark.asyncio
async def test_session_get_by_id(info):
    """
    Test retrieving a session by ID
    """
    has_permission(info.context["session"], "assistants", "get")
    session_id = UUID("12345678-1234-5678-1234-567812345678")

    session_obj = Mock()
    info.context["session_service"].get_by_id = AsyncMock(return_value=session_obj)

    query = SessionQueries()
    result = await query.session_get_by_id(info, id=session_id)

    assert result is not None
    info.context["session_service"].get_by_id.assert_awaited_once_with(session_id)
    assert isinstance(result, SessionResponse)


@pytest.mark.asyncio
async def test_session_create(info):
    """
    Test creating a session via SessionMutations.session_create
    """
    has_permission(info.context["session"], "assistants", "create")

    event_mock = Mock()
    event_mock.active = True
    event_mock.status = EventStatus.IN_PROGRESS
    event_mock.start_date = datetime(2025, 1, 1, 8, 0)
    event_mock.end_date = datetime(2025, 1, 1, 18, 0)

    speaker_mock = Mock()
    speaker_mock.type = AssistantType.SPEAKER

    info.context["event_service"].get_by_id = AsyncMock(return_value=event_mock)
    info.context["assistant_service"].get_by_id = AsyncMock(return_value=speaker_mock)
    info.context["session_service"].sessions_conflict = AsyncMock(return_value=False)
    info.context["session_service"].create_session = AsyncMock()

    mutation = SessionMutations()
    result = await mutation.session_create(
        info,
        event_id=UUID("12345678-1234-5678-1234-567812345678"),
        title="New Session",
        description="A detailed session",
        start_date="2025-01-01T09:00:00",
        end_date="2025-01-01T10:00:00",
        meta={"key": "value"},
        speaker_id=UUID("87654321-4321-8765-4321-876543218765")
    )

    assert result == "Session created successfully."
    info.context["session_service"].create_session.assert_awaited_once()


@pytest.mark.asyncio
async def test_session_update(info):
    """
    Test updating a session via SessionMutations.session_update
    """
    has_permission(info.context["session"], "assistants", "update")

    session_mock = Mock()
    session_mock.event.active = True
    session_mock.event.status = EventStatus.IN_PROGRESS
    session_mock.event.start_date = datetime(2025, 1, 1, 8, 0)
    session_mock.event.end_date = datetime(2025, 1, 1, 18, 0)

    info.context["session_service"].get_by_id = AsyncMock(return_value=session_mock)
    info.context["session_service"].update_session = AsyncMock()

    mutation = SessionMutations()
    await mutation.session_update(
        info,
        id=UUID("12345678-1234-5678-1234-567812345678"),
        title="Updated Session",
        description="Updated description"
    )

    info.context["session_service"].update_session.assert_awaited_once()


@pytest.mark.asyncio
async def test_session_delete(info):
    """
    Test deleting a session via SessionMutations.session_delete
    """
    has_permission(info.context["session"], "assistants", "delete")

    session_mock = Mock()
    session_mock.event.active = True
    session_mock.event.status = EventStatus.IN_PROGRESS

    info.context["session_service"].get_by_id = AsyncMock(return_value=session_mock)
    info.context["session_service"].delete_session = AsyncMock()

    mutation = SessionMutations()
    result = await mutation.session_delete(info, id=UUID("12345678-1234-5678-1234-567812345678"))

    assert result == "Session deleted successfully."
    info.context["session_service"].delete_session.assert_awaited_once()
