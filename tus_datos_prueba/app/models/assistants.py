from strawberry import type
from strawberry.scalars import JSON
from tus_datos_prueba.models import Assistant 
from uuid import UUID


@type
class AssistantResponse:
    id: UUID
    event_id: UUID
    user_id: UUID | None
    full_name: str | None
    email: str | None
    metadata: JSON
    contact_metadata: JSON

    @staticmethod
    def from_db(assistant: Assistant):
        return AssistantResponse(
            id=assistant.id,
            event_id=assistant.event_id,
            email=assistant.email,
            full_name=assistant.full_name,
            user_id=assistant.user_id,
            metadata=assistant.meta,
            contact_metadata=assistant.contact_meta
        )