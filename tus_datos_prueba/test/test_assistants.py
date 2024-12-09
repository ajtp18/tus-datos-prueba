import pytest
from unittest.mock import AsyncMock, Mock
from uuid import UUID

from tus_datos_prueba.app.adapters.assistants import AssistantQueries, AssistantMutations
from tus_datos_prueba.app.services.assistants import AssistantService
from tus_datos_prueba.app.services.events import EventService
from tus_datos_prueba.app.services.users import UserService
from tus_datos_prueba.utils.jwt import has_permission
from tus_datos_prueba.app.models.assistants import AssistantResponse
from tus_datos_prueba.models.events import AssistantType

@pytest.fixture
def assistant_service():
    svc = Mock(spec=AssistantService)
    return svc

@pytest.fixture
def event_service():
    svc = Mock(spec=EventService)
    return svc

@pytest.fixture
def user_service():
    svc = Mock(spec=UserService)
    return svc

@pytest.fixture
def info(assistant_service, event_service, user_service):
    return Mock(
        context={
            "session": {
                "perms": {
                    "assistants": ["list", "get", "create", "update", "delete"]
                }
            },
            "assistant_service": assistant_service,
            "event_service": event_service,
            "user_service": user_service
        }
    )

@pytest.mark.asyncio
async def test_assistant_list(info):
    """
    Test listing assistants via AssistantQueries.assistant_list
    """
    has_permission(info.context["session"], "assistants", "list")

    assistant1 = Mock()
    assistant2 = Mock()
    info.context["assistant_service"].list_assistants = AsyncMock(return_value=[assistant1, assistant2])

    query = AssistantQueries()
    result = await query.assistant_list(info, limit=10, offset=0)

    assert len(result) == 2
    info.context["assistant_service"].list_assistants.assert_awaited_once_with(10, 0)
    assert all(isinstance(a, AssistantResponse) for a in result)

@pytest.mark.asyncio
async def test_assistant_get_by_id(info):
    """
    Test retrieving an assistant by ID
    """
    has_permission(info.context["session"], "assistants", "get")
    assistant_id = UUID("12345678-1234-5678-1234-567812345678")

    assistant_obj = Mock()
    info.context["assistant_service"].get_by_id = AsyncMock(return_value=assistant_obj)

    query = AssistantQueries()
    result = await query.assistant_get_by_id(info, id=assistant_id)

    assert result is not None
    info.context["assistant_service"].get_by_id.assert_awaited_once_with(assistant_id)
    assert isinstance(result, AssistantResponse)

@pytest.mark.asyncio
async def test_assistant_create(info):
    """
    Test creating an assistant via AssistantMutations.assistant_create
    """
    has_permission(info.context["session"], "assistants", "create")

    info.context["user_service"].get_id_by_email = AsyncMock(return_value=UUID("12345678-1234-5678-1234-567812345678"))
    info.context["event_service"].validate_if_event_is_full = AsyncMock(return_value=False)
    info.context["assistant_service"].create_assistant = AsyncMock()

    mutation = AssistantMutations()
    result = await mutation.assistant_create(
        info,
        event_id=UUID("12345678-1234-5678-1234-567812345678"),
        email="assistant@example.com",
        full_name="John Doe",
        type=AssistantType.SPEAKER,
        metadata={"theme": "Tech Talk"},
        contact_metadata={"phone": "1234567890"}
    )

    assert result == "Assistant created successfully"
    info.context["assistant_service"].create_assistant.assert_awaited_once()

@pytest.mark.asyncio
async def test_assistant_update(info):
    """
    Test updating an assistant via AssistantMutations.assistant_update
    """
    has_permission(info.context["session"], "assistants", "update")
    assistant_id = UUID("12345678-1234-5678-1234-567812345678")

    info.context["assistant_service"].update = AsyncMock()

    mutation = AssistantMutations()
    await mutation.assistant_update(
        info,
        id=assistant_id,
        email="updated@example.com",
        full_name="Jane Doe",
        type=AssistantType.SPEAKER,
        metadata={"theme": "New Theme"},
        contact_metadata={"phone": "9876543210"}
    )

    info.context["assistant_service"].update.assert_awaited_once()

@pytest.mark.asyncio
async def test_assistant_delete(info):
    """
    Test deleting an assistant via AssistantMutations.assistant_delete
    """
    has_permission(info.context["session"], "assistants", "delete")
    assistant_id = UUID("12345678-1234-5678-1234-567812345678")

    assistant_obj = Mock()
    info.context["assistant_service"].get_by_id = AsyncMock(return_value=assistant_obj)
    info.context["assistant_service"].delete = AsyncMock()

    mutation = AssistantMutations()
    await mutation.assistant_delete(info, id=assistant_id)

    info.context["assistant_service"].get_by_id.assert_awaited_once_with(assistant_id)
    info.context["assistant_service"].delete.assert_awaited_once_with(assistant_obj)