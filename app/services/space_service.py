from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.space_repository import SpaceRepository
from app.api.schemas.space import SpaceCreate, SpaceUpdate

class SpaceService:
    def __init__(self, db: Session):
        self.repository = SpaceRepository(db)

    def get_all_spaces(self):
        return self.repository.get_all()

    def get_space(self, space_id: int):
        space = self.repository.get_by_id(space_id)
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Space with id {space_id} not found"
            )
        return space

    def create_space(self, space_in: SpaceCreate):
        return self.repository.create(space_in)

    def update_space(self, space_id: int, space_in: SpaceUpdate):
        space = self.repository.update(space_id, space_in)
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Space with id {space_id} not found"
            )
        return space

    def delete_space(self, space_id: int):
        success = self.repository.delete(space_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Space with id {space_id} not found"
            )
        return {"message": "Successfully deleted"}
