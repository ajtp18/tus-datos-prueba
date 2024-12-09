import re

from tus_datos_prueba.app.services.assistants import AssistantService
from tus_datos_prueba.app.models.assistants import AssistantResponse
from tus_datos_prueba.app.services.events import EventService
from tus_datos_prueba.app.services.users import UserService
from tus_datos_prueba.models.events import AssistantType
from tus_datos_prueba.utils.jwt import has_permission
from strawberry import type, mutation, field, Info
from strawberry.scalars import JSON
from uuid import UUID

NAME_REGEX = re.compile(r'^[A-Za-zÀ-ÖØ-öø-ÿ]+(\s[A-Za-zÀ-ÖØ-öø-ÿ]+)+$')

@type
class AssistantQueries:
    @field
    async def assistant_list(self, info: Info, limit: int | None = None, offset: int | None = None) -> list[AssistantResponse]:
        has_permission(info.context["session"], "assistants", "list")

        svc: AssistantService = info.context["assistant_service"]

        assistants = await svc.list_assistants(limit, offset)
        
        return [AssistantResponse.from_db(assistant) for assistant in assistants]


    @field
    async def assistant_get_by_id(self, info: Info, id: UUID) -> AssistantResponse:
        has_permission(info.context["session"], "assistants", "get")

        svc: AssistantService = info.context["assistant_service"]

        assistant = await svc.get_by_id(id)
        assert assistant is not None

        return AssistantResponse.from_db(assistant)
    
@type
class AssistantMutations:
    @mutation
    async def assistant_create(
        self, 
        info: Info, 
        event_id: UUID, 
        email: str,
        full_name: str,
        type: int, 
        metadata: JSON, 
        contact_metadata: JSON
    ) -> str:
        has_permission(info.context["session"], "assistants", "create")

        svc: AssistantService = info.context["assistant_service"]
        svc_event: EventService = info.context["event_service"]
        svc_user:  UserService = info.context["user_service"]

        # validation of email exist
        user_id = await svc_user.get_id_by_email(email)

        # validate format of full name
        if not NAME_REGEX.match(full_name):
            raise ValueError("Invalid full name format")
        
        # contact metadata must have a phone number
        assert contact_metadata.get("phone") is not None, "Phone number is required"

        if type == AssistantType.SPEAKER:
            if not isinstance(metadata, dict) or "theme" not in metadata:
                raise ValueError("Theme in metadata is required for type speaker")
        
        # validate limit of assistants in events
        result = await svc_event.validate_if_event_is_full(event_id)
        if result:
            raise ValueError("Event is full")

        await svc.create_assistant(
            event_id=event_id,
            email=email,
            full_name=full_name,  
            user_id=user_id,
            type=type, 
            meta=metadata,
            contact_meta=contact_metadata
        )

        return "Assistant created successfully"

    @mutation
    async def assistant_update(
        self, 
        info: Info, 
        id: UUID, 
        email: str | None = None,
        full_name: str | None = None,
        type: int | None = None, 
        metadata: JSON | None = None, 
        contact_metadata: JSON | None = None
    ) -> None:
        has_permission(info.context["session"], "assistants", "update")

        svc: AssistantService = info.context["assistant_service"]
        await svc.update(
            id,
            type=type,
            email = email,
            full_name = full_name,
            meta = metadata,
            contact_meta = contact_metadata
        )

    @mutation
    async def assistant_delete(self, info: Info, id: UUID) -> None:
        has_permission(info.context["session"], "assistants", "delete")

        svc: AssistantService = info.context["assistant_service"]
        assistant = await svc.get_by_id(id)
        assert assistant is not None

        await svc.delete(assistant)
        return None