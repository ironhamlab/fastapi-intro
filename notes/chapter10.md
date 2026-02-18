## Chapter 10. 스키마 - 요청
<br />

### 01. 요청의 정의

앞 장에서는 요청 파라미터를 받지 않는 GET함수를 정의했음. 이번 장에서는 **GET /tasks** 와 짝을 이루는, **POST /tasks** 에 대응하는 **create_task()** 함수를 정의해볼 예정임.

POST 함수에서는 요청 본문(response body)을 받아 데이터를 저장함

<br />

> ### 스키마

앞 장에서 정의한 GET 함수는 id를 가진 Task 인스턴스를 반환했음. 하지만 일반적으로 POST 함수에서는 id 를 지정하지 않고 DB 에서 자동으로 id 를 매기는 경우가 많음.

또한 done 필드에 대해서도 Task 작성 시에는 항상 false 이므로 POST /tasks 의 엔드포인트에서 제외함.

따라서 POST 함수는 요청 본문으로 title 필드만 받도록 함. POST 용으로 id, done 필드가 없는 TaskCreate 클래스를 새로 정의함.

<br />

**api/schemas/task.py**
```python
class TaskCreate(BaseModel):
    title: str | None = Field(None, example="세탁소에 맡긴 것을 찾으러 가기")
```

<br />

그러면 Task 와 TaskCreate 의 공통 필드는 title 뿐이므로, 양쪽에 title 만 가진 베이스 클래스로 TaskBase 를 정의하고 Task 와 TaskCreate 는 이를 이용하도록 고쳐 씀.

<br />

**api/schemas/task.py**
```python
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
```

=> 여기서 orm_mode 는 12장에서 DB에 접속할 때 사용함.

그리고 TaskCreate 의 응답으로, TaskCreate 에 id 만 추가한 TaskCreateResponse 도 정의함.

<br />

**api/schemas/task.py**
```python
class TaskCreateResponse(TaskCreate) :
    id: int

    class Config:
        orm_mode = True
```

<br />
<br />

> ### 라우터

라우터에 POST 의 경로 동작 함수 create_task() 를 정의함.


**api/routers/task.py**
```python
@router.post("/tasks", response_model=task_schema.TaskCreateResponse)
async def create_task(task_body: task_schema.TaskCreate):
    return task_schema.TaskCreateResponse(id=1, **task_body.dict())
```

<br />

요청 파라미터에 따라 DB 에 저장하고 싶지만, 여기서는 우선 API 로 올바른 타입의 데이터를 넘겨받아, 적합한 타입의 응답을 반환하도록 함. 수신한 요청 본문에 id 를 부여하여 응답 데이터를 반환하도록 함.

create_task() 함수의 인수로 지정한 것이 요청 본문 **task_body: task_schema.TaskCreate** 임.

앞서 설명한 바와 같이, 요청에 대한 응답 데이터는 id 를 가짐. 요청 본문의 task_schema.TaskCreate 클래스를 일단 dict 로 변환하고, key/value 와 id=1 을 가진 **task_schema.TaskCreateResponse** 인스턴스를 생성하는 것이 task_schema.TaskCreate Response(id=1, **task_body.dict()) 임.

dict 인스턴스 앞에 **를 붙여 dict 를 키워드 인수로 확장하고, task_schema.TaskCreateResponse 클래스의 생성자에 dict 의 key/value 를 전달함.

즉, task_schema.TaskCreateResponse(id=1, title=task_body.title, done=task_body.done) 라고 작성하는 것과 동일함.

<br />
<br />

> ### 동작 확인

앞에서 정의한 POST 엔드포인트를 호출할 경우,

요청을 전송하면 요청 본문(Request body) 에 id가 부여되어 그대로 응답(Responses)으로 돌아오는 것 확인 가능.

요청 본문을 변경하면, 동적으로 응답이 달라짐을 확인 가능.



<br />
<br />

---

### 02. 나머지 요청과 응답을 모두 정의하기

라우터에는 경로 동작 함수가 6개 밖에 없으므로, 다른 함수도 요청과 응답을 모두 채울 예정. 최종적으로 다음과 같이 정의

<br />

**api/routers/task.py**
```python
@router.get("/tasks", response_model=list[task_schema.Task])
async def list_tasks():
    return [task_schema.Task(id=1, title="첫 번째 ToDo 작업")]


@router.post("/tasks", response_model=task_schema.TaskCreateResponse)
async def create_task(task_body: task_schema.TaskCreate):
    return task_schema.TaskCreateResponse(id=1, **task_body.dict())


@router.put("/tasks/{task_id}", response_model=task_schema.TaskCreateResponse)
async def update_task(task_id: int, task_body: task_schema.TaskCreate):
    return task_schema.TaskCreateResponse(id=task_id, **task_body.dict())


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    return
```

<br />

**api/routers/done.py**
```python
@router.put("/tasks/{task_id}/done", response_model=None)
async def mark_task_as_done(task_id: int):
    return


@router.delete("/tasks/{task_id}/done", response_model=None)
async def unmark_task_as_done(task_id: int):
    return
```
=> done 관련 함수는 체크박스를 ON/OFF할 뿐이므로 요청 본문과 응답이 없어 단순함.

<br />
<br />

---

### 03. 스키마 기반 개발

9-10 장에서는 8 장에서 정의한 라우터의 플레이스 홀더에 대해 요청과 응답을 정의했음. 하지만 핵심적인 데이터 저장과 데이터 읽기가 아직 구현되어 있지 않아 API로서는 그다지 도움이 되지 않음.

라우터로서는 각 경로 연산에 3줄의 코드만 작성했을 뿐이지만, API Mock (모의 객체) 역할을 수행함. 여기까지 준비된 단계에서 프론트엔드와 백엔드 통합을 시작할 수 있음. 이후의 구현에서는 이러한 요청과 응답의 정의에 대해 언급하지 않음.

물론 조건에 따라 요청과 응답의 형태가 달라지거나 비정상적인 경우를 모두 처리하지 못할 수도 있음. 하지만 적어도 정상 케이스의 한 패턴에 대해 모든 엔드포인트를 커버하고 있다는 것은 API 개발과 분리된 SPA 개발 등에서 프론트엔드 개발자에게 강력한 무기가 될 것임.

<br />
<br />

> ### 개발 초기에 미치는 영향

많은 Web API 프레임워크는 Swagger UI 의 통합을 지원하지 않음. 그렇기 때문에 보통은 다음과 같이 세 단계로 스키마 개발을 실현함.

1. 스키마를 OpenAPI 형식(일반적으로 YAML)으로 정의한다.
2. Swagger UI 를 제공하여 프론트엔드 개발자에게 전달한다.
3. API 개발에 착수한다.

<br />

그러나 FastAPI 에서는 다음과 같이 훨씬 간단한 단계로 스키마 기반 개발을 실현할 수 있음.

1. API 개발 과정으로 라우터와 스키마를 정의하고, 자동 생성된 Swagger UI 를 프론트엔드 개발자에게 전달한다.
2. 위 라우터와 스키마에 살을 붙이는 형태로 API 의 기능을 구현한다.

<br />
<br />

> ### 기능 수정 시 미치는 영향

보통 다른 프레임워크에서는 다음과 같이 개발함.

1. 먼저 OpenAPI 로 정의한 스키마를 변경한다.
2. 변경된 Swagger UI 를 제공하여 프론트엔드 개발자에게 전달한다.
3. API 를 수정한다.

<br />

반면 FastAPI라면 동작 중인 API 의 요청과 응답을 직접 변경하고, 동시에 자동 생성된 Swagger UI 를 프론트엔드 개발자에게 전달하는 것으로 끝임.

한 번 API 를 개발해 놓으면 OpenAPI 의 스키마 정의는 유지관리되지 않게 되며, Swagger UI 를 제공하는 모의 서버를 구동하는 방법을 잊어버리거나 아예 망가져 버리는 경우가 발생하기도 함. 하지만 FastAPI 는 API 인터페이스의 정의(문서)와 구현이 함께 제공되므로 그런 걱정이 없음!

