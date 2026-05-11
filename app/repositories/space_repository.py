from sqlalchemy.orm import Session
from app.models.models import Space
from app.api.schemas.space import SpaceCreate, SpaceUpdate

class SpaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Space).all()

    def get_by_id(self, space_id: int):
        return self.db.query(Space).filter(Space.id == space_id).first()

    def create(self, space_in: SpaceCreate):
        db_space = Space(
            name=space_in.name,
            description=space_in.description
        )
        self.db.add(db_space)
        self.db.commit()
        self.db.refresh(db_space)
        return db_space

    def update(self, space_id: int, space_in: SpaceUpdate):
        db_space = self.get_by_id(space_id)
        if db_space:
            update_data = space_in.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_space, key, value)
            self.db.commit()
            self.db.refresh(db_space)
        return db_space

    def delete(self, space_id: int):
        db_space = self.get_by_id(space_id)
        if db_space:
            self.db.delete(db_space)
            self.db.commit()
            return True
        return False
