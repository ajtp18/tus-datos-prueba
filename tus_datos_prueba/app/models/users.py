from pydantic import BaseModel


class LoginClaim(BaseModel):
    # TODO: enhance validations
    email: str
    password: str