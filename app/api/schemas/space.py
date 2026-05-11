from pydantic import BaseModel, ConfigDict
from typing import Optional

class SpaceBase(BaseModel):
    name: str
    description: Optional[str] = None

class SpaceCreate(SpaceBase):
    pass

class SpaceUpdate(SpaceBase):
    name: Optional[str] = None

class Space(SpaceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
