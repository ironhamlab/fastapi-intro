## Chapter 12. DB 조작(CRUDs)
<br />

### 01. C: Create

처음에는 데이터가 존재하지 않으므로 POST /tasks 부터 작성

<br />
<br />

> ### CRUDs

라우터는 MVC(Model View Controller) 의 컨트롤러에 해당함. 컨트롤러는 모델이나 뷰를 연결하기 때문에 비대해지기 쉬움(Fat Controller). 이를 피하기 위해 DB 의 CRUD 조작 처리는 **api/cruds/task.py** 에 작성함.

<br />

**api/cruds/task.py**

```python
from sqlalchemy.orm import Session


import api.models.task as task_model
import api.schemas.task as task_schema



def create_task(db: Session, task_create:task_schema.TaskCreate) -> task_model.Task:  # 1
    task = task_model.Task(**task_create.dict())  # 2
    db.add(task)
    db.commit()  # 3
    db.refresh(task)  # 4
    return task  # 5
```
<br />
작업의 흐름을 차례대로 적어보자면, 다음이 대략적인 흐름임.

1. 스키마 task_create: task_schema.TaskCreate 를 인수로 받는다.
2. 이를 DB 모델인 task_model.Task 로 변환한다.
3. DB 에 커밋한다.
4. DB 의 데이터를 바탕으로 Task 인스턴스인 task 를 업데이트한다(작성된 레코드의 ID 를 가져옴).
5. 생성한 DB 모델을 반환한다.



<br />
<br />

> ### 라우터

앞에서 소개한 CRUD 정의를 이용하는 라우터는 다음처럼 다시 작성 가능

**api/routers/task.py**
```python

-from fastapi import APIRouter
+from fastapi import APIRouter, Depends
+from sqlalchemy.orm import Session


+import api.cruds.task as task_crud
+from api.db import get_db

```

<br />

**api/routers/task.py**
```python
@router.post("/tasks", response_model=task_schema.TaskCreateResponse)
-async def create_task(task_body: task_schema.TaskCreate):
+async def create_task(task_body: task_schema.TaskCreate, db: Session = Depends(get_db)):
-    return task_schema.TaskCreateResponse(id=1, **task_body.dict())
+    return task_crud.create_task(db, task_body)
```

<br />

#### DB 모델과 응답 스키마 변환하기

요청 본문의 task_schema.TaskCreate 와 응답 모델의 task_schema.TaskCreateResponse 에 대해서는 9 장에서 설명한 것과 같이, 요청에 대해 id 만 부여하여 반환해야 함.

```python
# api/schemas/task.py

class TaskBase(BaseModel):
    title: str | None = Field(None, example="세탁소에 맡긴 것을 찾으러 가기")


class TaskCreate(TaskBase):
    pass


class TaskCreateResponse(TaskCreate) :
    id: int

    class Config:
        orm_mode = True
```

<br />

여기서 orm_mode = True 는 응답 스키마 TaskCreate Response 가 암묵적ㅇ로 ORM 에서 DB 모델의 객체를 받아들여, 응답 스키마로 변환한다는 것을 의미함.

그 증거로, **api/routers/task.py** 에서 task_crud.create_task(db, task_body) 는 DB 모델의 task_model.Task 를 반환하고 있지만, 동작 결과가 변하지 않는 것으로 보아 API 가 올바르게 TaskCreateResponse 로 변환하고 있음을 알 수 있음. 이는 내부적으로 TaskCreateResponse 를 task_model.Task 의 각 필드를 사용하여 초기화하여 구현하고 있음.


<br />

#### 의존성 주입(DI)

**api/routers/task.py** 에서 등장하는 생소한 db: Session = Depends(get_db) 코드에 주목.

Depends 는 함수를 인수로 받아 의존성 주입(Dependency Injection, DI) 을 수행하는 메커니즘임. 의존성 주입은 객체가 직접 서비스를 찾거나 생성하는 대신, 외부로부터 필요한 서비스를 받아와 사용하는 소프트웨어 디자인 기법임. 객체는 해당 서비스를 외부에서 주입받아 사용하며, 이는 유연하고 재사용 가능한 코드를 작성하는 데 도움을 줌. 또한 get_db 는 11 장에서 정의한 DB 세션을 가져오는 함수임.

DB 접속 부분에 의존성 주입을 이용하여 비즈니스 로직과 DB 가 밀접하게 결합되어 버리는 것을 방지할 수 있음. 또한 의존성 주입을 통해 db 인스턴스의 내용을 외부에서 오버라이드할 수 있으므로, 테스트 수행 시 get_db 와 다른 연결 대상으로 교체하는 등의 작업이 프로덕션 코드를 수정하지 않아도 가능해짐.


<br />
<br />

> ### 동작 확인

Swagger UI 에서 POST /tasks 엔드포인트에 접속해 봄. 'Execute' 를 클릭할 때마다 id 값이 증가한 결과를 반환하는 것을 확인할 수 있음.


<br />
<br />

---

### 02. R: Read


<br />
<br />

---

### 03. U: Update


<br />
<br />

---

### 04. D: Delete


<br />
<br />

---

### 05. Done 리소스



<br />
<br />

---

### 06. 최종 디렉터리 구성