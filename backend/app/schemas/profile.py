from pydantic import BaseModel, Field


class ProfileCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    occupation: str = Field(min_length=2, max_length=120)
    years_in_business: int = Field(ge=0, le=100)
    location: str = Field(min_length=2, max_length=200)
    language: str = Field(default="en", pattern="^(en|hi)$")
    consent_accepted: bool


class ProfileResponse(BaseModel):
    id: str
    auth_user_id: str
    full_name: str
    occupation: str
    years_in_business: int
    location: str
    language: str
    consent_accepted: bool