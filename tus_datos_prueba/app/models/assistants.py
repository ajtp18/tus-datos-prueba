from strawberry import type
from strawberry.scalars import JSON
from tus_datos_prueba.models import Assistant 
from uuid import UUID


@type
class AssistantResponse:
    id: UUID
    event_id: UUID
    user_id: UUID
    status: int
    metadata: JSON
    contact_metadata: JSON

    @staticmethod
    def from_db(assistant: Assistant):
        return AssistantResponse(
            id=assistant.id,
            event_id=assistant.event_id,
            user_id=assistant.user_id,
            status=assistant.status,
            metadata=assistant.meta,
            contact_metadata=assistant.contact_meta
        )