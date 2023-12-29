from pydantic import BaseModel


class TodoUserBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class TodoUserCreate(TodoUserBase):
    name: str


class TodoUserRetrieve(TodoUserBase):
    pass


class TodoItemBase(BaseModel):
    id: int
    label: str
    is_done: bool
    user_id: int

    class Config:
        orm_mode = True


class TodoItemCreate(TodoItemBase):
    label: str


class TodoItemRetrieve(TodoItemBase):
    pass
