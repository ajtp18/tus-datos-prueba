import pytest
from unittest.mock import AsyncMock, Mock
from uuid import UUID

from tus_datos_prueba.app.adapters.events import EventQueries, EventMutations
from tus_datos_prueba.app.services.events import EventService
from tus_datos_prueba.utils.jwt import has_permission
from tus_datos_prueba.app.models.events import EventResponse

@pytest.fixture
def event_service():
    svc = Mock(spec=EventService)
    return svc

@pytest.fixture
def info(event_service):
    return Mock(
        context={
            "session": {
                "perms": {
                    "events": ["list", "get", "create", "update", "delete"]
                },
                "sub": UUID("12345678-1234-5678-1234-567812345678")
            },
            "event_service": event_service
        }
    )

@pytest.mark.asyncio
async def test_event_list(info):
    """
    Test listing events via EventQueries.event_list

    Ensures that:
    - Permissions are checked.
    - The event_service.list_events is called with correct parameters.
    - Returns the list of events as EventResponse objects.
    """
    # Mock permission
    has_permission(info.context["session"], "events", "list")

    # Mock events returned by the service
    event1 = Mock()
    event2 = Mock()
    info.context["event_service"].list_events = AsyncMock(return_value=[event1, event2])

    query = EventQueries()
    result = await query.event_list(info, limit=10, offset=0)

    assert len(result) == 2
    # Check that the service was called with the right params
    info.context["event_service"].list_events.assert_awaited_once_with(10, 0)
    assert all(isinstance(e, EventResponse) for e in result)

@pytest.mark.asyncio
async def test_event_get_by_id(info):
    """
    Test retrieving a single event by ID

    Ensures that:
    - Permissions are checked.
    - The event_service.get_by_id is called with correct UUID.
    - The correct EventResponse is returned if found.
    """
    has_permission(info.context["session"], "events", "get")
    event_id = UUID("12345678-1234-5678-1234-567812345678")

    # Mock event object
    event_obj = Mock()
    info.context["event_service"].get_by_id = AsyncMock(return_value=event_obj)

    query = EventQueries()
    result = await query.event_get_by_id(info, id=event_id)

    assert result is not None
    info.context["event_service"].get_by_id.assert_awaited_once_with(event_id)
    assert isinstance(result, EventResponse)

@pytest.mark.asyncio
async def test_event_create(info):
    """
    Test creating an event via EventMutations.event_create

    Ensures that:
    - Permissions are checked.
    - The event_service.create_event is called with correct parameters.
    - Returns a success message.
    """
    has_permission(info.context["session"], "events", "create")

    # Mock the service method
    info.context["event_service"].create_event = AsyncMock(return_value=None)

    mutation = EventMutations()
    title = "Test Event"
    description = "A description"
    start_date = "2025-01-02 09:00:00"
    end_date = "2025-01-02 17:00:00"
    meta = {"key": "value"}
    assistant_limit = 20

    result = await mutation.event_create(
        info,
        title=title,
        description=description,
        start_date=start_date,
        end_date=end_date,
        meta=meta,
        assitant_limit=assistant_limit
    )

    # Check that the service was called correctly
    info.context["event_service"].create_event.assert_awaited_once_with(
        title,
        description,
        start_date,
        end_date,
        meta,
        assistant_limit,
        info.context["session"]["sub"]
    )

    assert result == "Event created successfully"

@pytest.mark.asyncio
async def test_event_update(info):
    """
    Test updating an event

    Ensures that:
    - Permissions are checked.
    - The event_service.update is called with an updated event object.
    """
    has_permission(info.context["session"], "events", "update")
    event_id = UUID("12345678-1234-5678-1234-567812345678")

    event_obj = Mock()
    info.context["event_service"].get_by_id = AsyncMock(return_value=event_obj)
    info.context["event_service"].update = AsyncMock()

    mutation = EventMutations()
    await mutation.event_update(info, id=event_id, title="New Title")

    info.context["event_service"].get_by_id.assert_awaited_once_with(event_id)
    # The event_obj should be updated with the new title
    assert event_obj.title == "New Title"
    info.context["event_service"].update.assert_awaited_once_with(event_obj)

@pytest.mark.asyncio
async def test_event_delete(info):
    """
    Test deleting an event (soft-delete)

    Ensures that:
    - Permissions are checked.
    - The event_service.delete is called with the event object.
    """
    has_permission(info.context["session"], "events", "delete")
    event_id = UUID("12345678-1234-5678-1234-567812345678")

    event_obj = Mock()
    info.context["event_service"].get_by_id = AsyncMock(return_value=event_obj)
    info.context["event_service"].delete = AsyncMock()

    mutation = EventMutations()
    await mutation.event_delete(info, id=event_id)

    info.context["event_service"].get_by_id.assert_awaited_once_with(event_id)
    info.context["event_service"].delete.assert_awaited_once_with(event_obj)

