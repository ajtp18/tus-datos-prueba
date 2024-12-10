import re

from tus_datos_prueba.app.services.assistants import AssistantService
from tus_datos_prueba.app.models.assistants import AssistantResponse
from tus_datos_prueba.utils.mail.compose import compose_email
from tus_datos_prueba.app.services.events import EventService
from tus_datos_prueba.app.services.users import UserService
from tus_datos_prueba.models.events import AssistantType
from tus_datos_prueba.utils.jwt import has_permission
from strawberry import type, mutation, field, Info
from tus_datos_prueba.utils.mail import Mail
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
        svc_user: UserService = info.context["user_service"]
        mail: Mail = info.context["mail"]

        # Validations...
        user_id = await svc_user.get_id_by_email(email)
        if not NAME_REGEX.match(full_name):
            raise ValueError("Invalid full name format")
        assert contact_metadata.get("phone") is not None, "Phone number is required"
        if type == AssistantType.SPEAKER and (not isinstance(metadata, dict) or "theme" not in metadata):
            raise ValueError("Theme in metadata is required for type speaker")

        # Validate event capacity
        result = await svc_event.validate_if_event_is_full(event_id)
        if result:
            # Notify event creator
            event_title = await svc_event.get_event_title(event_id)
            event_creator_email = await svc_event.get_event_creator_email(event_id)
            warning_message = compose_email(
                "Event is Full",
                event_creator_email,
                f"The event '{event_title}' has reached its maximum capacity. No more assistants can be added."
            )
            await mail.send_message(warning_message)
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

        message = compose_email(
            "Welcome to the Service",
            email,
            f"Welcome {full_name}, you have been registered as an assistant."
        )
        await mail.send_message(message)

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
        svc_event: EventService = info.context["event_service"]
        mail: Mail = info.context["mail"]

        assistant = await svc.get_by_id(id)
        assert assistant is not None

        # Notify event creator
        event_creator_email = await svc_event.get_event_creator_email(assistant.event_id)
        creator_message = compose_email(
            "Assistant Removed",
            event_creator_email,
            f"The assistant {assistant.full_name} ({assistant.email}) has been removed from the event."
        )
        await mail.send_message(creator_message)

        # Notify the removed assistant
        assistant_message = compose_email(
            "You Have Been Removed",
            assistant.email,
            f"You have been removed from the event with ID {assistant.event_id}."
        )
        await mail.send_message(assistant_message)

        await svc.delete(assistant)
        return None