import pytest
from unittest.mock import AsyncMock, Mock, call, patch
from uuid import UUID

from tus_datos_prueba.app.adapters.users import UserQueries, UserMutations
from tus_datos_prueba.app.services.users import UserService
from tus_datos_prueba.app.services.roles import RoleService
from tus_datos_prueba.utils.jwt import has_permission

@pytest.fixture
def user_service():
    svc = Mock(spec=UserService)
    return svc

@pytest.fixture
def role_service():
    svc = Mock(spec=RoleService)
    return svc

@pytest.fixture
def info(user_service, role_service):
    return Mock(
        context={
            "session": {
                "perms": {
                    "user": ["list", "get", "create"]
                }
            },
            "user_service": user_service,
            "role_service": role_service
        }
    )

@pytest.mark.asyncio
async def test_user_list(info):
    # Mock de permisos
    has_permission.return_value = True

    # Mock del servicio de usuarios
    user1 = Mock()
    user2 = Mock()
    info.context["user_service"].list_users = AsyncMock(return_value=[user1, user2])

    query = UserQueries()
    users = await query.user_list(info, limit=10, offset=0)

    assert len(users) == 2
    info.context["user_service"].list_users.assert_awaited_once_with(10, 0)

@pytest.mark.asyncio
async def test_user_get_by_id(info):
    # Mock de permisos
    has_permission.return_value = True

    # Mock del servicio de usuarios
    user = Mock()
    user_id = UUID("12345678-1234-5678-1234-567812345678")
    info.context["user_service"].get_by_id = AsyncMock(return_value=user)

    query = UserQueries()
    result = await query.user_get_by_id(info, id=user_id)

    assert result is not None
    info.context["user_service"].get_by_id.assert_awaited_once_with(user_id)

@pytest.mark.asyncio
@patch('tus_datos_prueba.utils.jwt.has_permission')
async def test_user_create(mock_has_permission, info):
    # Mock de permisos
    mock_has_permission.return_value = True

    # Mock del servicio de roles
    admin_role_id = 1
    claim_role_id = 2
    info.context["role_service"].get_id_by_slug = AsyncMock(side_effect=[claim_role_id, admin_role_id])

    # Mock del método create_user
    info.context["user_service"].create_user = AsyncMock(return_value="user_id")

    # Mock del método get_id_by_email
    info.context["user_service"].get_id_by_email = AsyncMock(return_value="user_id")

    # Datos de prueba
    email = "test@example.com"
    password = "Password1."
    role = "user"
    metadata = {"full_name": "mock de nombre", "job": "mock de trabajo"}

    mutation = UserMutations()
    result = await mutation.user_create(info, email, password, role, metadata)

    assert result == "user_id"

    # Verificar que get_id_by_slug fue llamado con 'user' y luego con 'administrator'
    expected_calls = [call(role), call('administrator')]
    info.context["role_service"].get_id_by_slug.assert_has_awaits(expected_calls)