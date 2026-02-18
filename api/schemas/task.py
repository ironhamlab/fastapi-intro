from pydantic import BaseModel, Field



class TaskBase(BaseModel):
    title: str | None = Field(None, example="세탁소에 맡긴 것을 찾으러 가기")


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    done: bool = Field(False, description="완료 플래그")


    class Config:
        orm_mode = True


class TaskCreateResponse(TaskCreate) :
    id: int

    class Config:
        orm_mode = True