## Chapter 13. 비동기화
<br />

### 01. 비동기화의 이유

11 장의 Models 와 12 장의 CRUDs 코드는 sqlalchemy 의 백엔드인 MySQL 을 이용하는 클라이언트로 pymysql 을 이용했음. 하지만 pymysql 은 파이썬의 비동기 처리 프레임워크인 asyncio 를 지원하지 않아 병렬 처리가 쉽지 않음. 

지금까지 작성한 코드도 충분히 빠르게 동작하지만, IO 바운드(IO bound) 가 발생하는 무거운 데이터베이스 처리가 늘어나는 경우에는 병렬 처리하는 것이 효과적임.

IO 바운드는 작업 중 I/O 대기 시간이 많은 프로세스를 의미하며, 파일 쓰기, 디스크 작업, 네트워크 통신과 같은 작업에서 발생하는데, 시스템과의 통신으로 인해 작업 속도가 결정됨.

<br />

성능 향상의 효과는 환경에 많이 좌우됨. 이 장에서 변경한 내용을 AWS 에 배포한 애플리케이션을 대상으로 간단한 부하 테스트를 진행한 결과, ASGI 서버나 운영체제 등에 대한 특별한 튜닝을 하지 않고서도 시간당 처리량(Throughput) 성능이 약 38% 정도 향상되었음.

<br />

---

※ SQLAlchemy 와 비동기 처리

기존 SQLAlchemy 의 ORM 은 비동기 처리를 지원하지 않아 FastAPI 의 async/await 에 의한 이벤트 루프를 활용한 빠른 DB 처리를 할 수 없었음. ORM 은 필요 시점까지 객체의 초기화를 연기하는 지연된 로딩(lazy loading) 을 많이 사용하기 때문에 비동기 처리를 지원하기 어려웠고, 원래 SQLAlchemy 의 하위 계층 구현인 SQLAlchemy Core 에 의한 SQLAlchemy ORM 보다 원시적인(primitive) 쓰기 방식(SQL 문을 직접 쓰는 것에 가까운 쿼리 표기법)으로만 비동기 처리가 가능했음.

SQLAlchemy 버전 1.4 부터 지원되는 버전 2.0 식의 새로운 작성 방식(2.0 Style)에 따라, ORM 으로 클래스를 정의한 경우에도 비동기 처리가 지원됨 이 책에서는 이 작성법에 따라 고속의 DB 접근을 가능하게 함.

---

<br />
<br />
<br />

---

### 02. aiomysql 설치

이 장에서는 비동기 처리를 지원하기 위해 aiomysql 을 설치하여 사용함. 참고로 aiomysql 은 pymysql 기반의 MySQL 용 비동기 IO 처리를 제공하는 라이브러리이며, pymysql 에 의존함.

11 장 2 절에서 설명한 MySQL 클라이언트 설치와 마찬가지로 demo-app 이 실행된 상태에서 poetry add 를 실행하여 aiomysql 을 설치함.

```shell
# "demo-app" 컨테이너에서 "poetry add aiomysql" 실행
$ docker compose exec demo-app poetry add aiomysql
```


<br />
<br />

---

### 03. 비동기 대응 DB 접속 함수

11 장에서 준비한 **api/db.py** 의 DB 접속 함수 get_db() 를 비동기 대응 함수로 수정

**api/db.py**
```python
- from sqlalchemy import create_engine
+ from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base


- DB_URL = "mysql+pymysql://root@db:3306/demo?charset=utf8"  # 1
+ ASYNC_DB_URL = "mysql+aiomysql://root@db:3306/demo?charset=utf8"  # 1

- db_engine = create_engine(DB_URL, echo=True)  # 2
- db_session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

+ async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
+ async_session = sessionmaker(
+   autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession  
+ )  # 2

Base = declarative_base()


- def get_db():  # 3
-     with db_session() as session:
+ async def get_db():
+   async with async_session() as session:  # 3
        yield session
```

<br />

데이터베이스 연결에 사용하는 라이브러리가 pymysql 에서 aiomysql 로 변경되었음 (#1)

비동기 대응 AsyncEngine 을 생성하는 create_async_engine 과 비동기 세션 클래스인 AsyncSession 을 이용한 sessionmaker 로 재작성함 (#2)

마지막으로 get_db 함수 자체를 async 에 대응시킴 (#3)

<br />

참고로 migrate_db.py 에서도 동일하게 create_engine 을 호출하고 있음. 하지만 마이그레이션 작업은 자주 수행하거나 빠른 속도를 요구하는 작업은 아니기 때문에 비동기화할 필요는 없을 것임.


<br />
<br />

---

### 04. 비동기 대응 CRUDs

앞 장에서 준비한 CRUDs 를 재작성함. api/cruds, api/routers 모두 다시 작성해야 함.

<br />

> ### C: Create

**api/cruds/task.py**
```python
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import Session
+ from sqlalchemy.ext.asyncio import AsyncSession

...


- def create_task(db: Session, task_create:task_schema.TaskCreate) -> task_model.Task:
+ async def create_task(
+     db: AsyncSession, task_create: task_schema.TaskCreate
+ ) -> task_model.Task:
    task = task_model.Task(**task_create.dict())
    db.add(task)
-   db.commit()
-   db.refresh(task)
+   await db.commit()
+   await db.refresh(task)
    return task
```

<br />

변경된 사항은 함수 정의가 async def 로 변경된 점, db.commit() 과 db.refresh(Task) 에 await 가 붙은 점임. async def 는 함수가 비동기 처리를 할 수 있는 코루틴(coroutine) 함수(이하 코루틴)임을 나타냄.

여기서 await 는 DB 접속(IO 처리)이 발생하므로, '대기 시간이 발생하는 처리를 할게요'라고 비동기 처리를 알리는 역할을 함. 이를 통해 파이썬은 이 코루틴의 처리에서 일단 벗어나, 이벤트 루프 내에서 다른 코루틴의 처리를 수행할 수 있게 됨. 이것이 비동기/병렬 처리의 핵심임.

<br />

---

※ 코루틴이란?

코루틴은 서브루틴(코루틴이 아닌 일반 함수)의 일반형임. def 에 대해 async def 이므로 오히려 특수형이라고 생각할 수 있음. 일반 함수는 동기 처리만 가능하지만, 코루틴은 동기 처리와 비동기 처리를 모두 할 수 있으므로 일반형임.

---

<br />

앞에서 준비한 CRUD 정의 create_task 를 이용하는 라우터는 다음처럼 다시 작성할 수 있음.

<br />

**api/routers/task.py**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
+ from sqlalchemy.ext.asyncio import AsyncSession

...


- async def create_task(task_body: task_schema.TaskCreate, db: Session = Depends(get_db)):
-     return task_crud.create_task(db, task_body)
+ async def create_task(
+     task_body: task_schema.TaskCreate, db: AsyncSession = Depends(get_db)
+     ):
+     return await task_crud.create_task(db, task_body)
```

<br />

라우터의 경로 동작 함수는 원래부터 코루틴으로 정의되어 있었음. task_crud.create_task() 가 await 를 포함하는 코루틴이므로, create_task() 의 반환값도 await 를 사용하여 돌려줌.

여기서 await 를 지정하는 것을 잊어버리면 어떻게 될까?

async def 로 정의된 코루틴은 동기 처리도 가능하다고 설명했음. 따라서 파이썬은 문법 오류가 발생하지 않음. 하지만 POST /tasks 엔드포인트에서 'Execute'를 하면 task_model.Task 대신 coroutine 자체를 응답으로 반환하려고 하므로, response 에 id 필드가 없어서 응답 스키마의 결함으로 다음과 같은 오류가 발생함

```
pydantic.error_wrappers.ValidationError: 1 validation error for TaskCreateResponse
response -> id
  field required(type=value_error.missing)
```

<br />

마찬가지로 이 router 정의에서 await 를 넣었더라도, 반대로 task_crud.create_task(db, task_body) 에서 db.commit() 과 db.refresh() 에 await 를 붙이지 않으면, DB 의 반환을 기다리지 않고 task_class.model.Task 클래스를 반환하려고 함. 그때 DB 호출 시 발급받아야 할 id 가 아직 할당되지 않아 오류가 발생하므로 주의해야 함.

<br />
<br />

> ### R: Read

Create 이외의 CRUDs 에 대해서도 동일하게 cruds 와 routers 의 각 파일을 변경함.

**api/cruds/task.py**
```python
- def get_tasks_with_done(db: Session) -> list[tuple[int, str, bool]]:
+ async def get_tasks_with_done(db: AsyncSession) -> list[tuple[int, str, bool]]:
-     result: Result = db.execute(
+     result: Result = await db.execute(
```

get_tasks_with_done() 함수 역시 create_task() 함수와 마찬가지로 코루틴이므로 async def 로 정의하고, await 를 사용하여 Result 를 가져옴.


**api/routers/task.py**
```python
@router.get("/tasks", response_model=list[task_schema.Task])
- async def list_tasks(db: Session = Depends(get_db)):
+ async def list_tasks(db: AsyncSession = Depends(get_db)):
-     return task_crud.get_tasks_with_done(db)
+     return await task_crud.get_tasks_with_done(db)
```

<br />
<br />

> ### U: Update

**api/cruds/task.py**
```python
- def get_task(db: Session, task_id: int) -> task_model.Task | None:
+ async def get_task(db: AsyncSession, task_id: int) -> task_model.Task | None:
-     result: Result = db.execute(
+     result: Result = await db.execute(

...


- def update_task(
-     db: Session, task_create: task_schema.TaskCreate, original:task_model.Task
+ async def update_task(
+     db: AsyncSession, task_create: task_schema.TaskCreate, original:task_model.Task
) -> task_model.Task:
    original.title = task_create.title
    db.add(original)
-   db.commit()
-   db.refresh(original)
+   await db.commit()
+   await db.refresh(original)
    return original
```

<br />

**api/routers/task.py**
```python
@router.put("/tasks/{task_id}", response_model=task_schema.TaskCreateResponse)
async def update_task(
-   task_id: int, task_body: task_schema.TaskCreate, db: Session = Depends(get_db)
+   task_id: int, task_body: task_schema.TaskCreate, db: AsyncSession = Depends(get_db)
    ):
-   task = task_crud.get_task(db, task_id=task_id)
+   task = await task_crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
-   return task_crud.update_task(db, task_body, original=task)
+   return await task_crud.update_task(db, task_body, original=task)
```

<br />
<br />

> ### D: Delete

**api/cruds/task.py**
```python
- from sqlalchemy.orm import Session

...


- def delete_task(db: Session, original: task_model.Task) -> None:
-     db.delete(original)
-     db.commit()
+ async def delete_task(db: AsyncSession, original: task_model.Task) -> None:
+     await db.delete(original)
+     await db.commit()
```

<br />

**api/routers/task.py**
```python
- from sqlalchemy.orm import Session


@router.delete("/tasks/{task_id}", response_model=None)
- async def delete_task(task_id: int, db: Session = Depends(get_db)):
-   task = task_crud.get_task(db, task_id=task_id)
+ async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
-   task = await task_crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
-   return task_crud.delete_task(db, original=task)
+   return await task_crud.delete_task(db, original=task)
```

<br />
<br />

> ### Done 리소스

**api/cruds/done.py** 와 **api/routers/done.py** 도 다시 작성함.


<br />
<br />

마지막으로, 변경한 모든 엔드포인트에 대해 오류 없이 변경 전의 응답을 얻을 수 있는지 Swagger UI 로 동작을 확인해 둠.

다음 장에서는 이 장에서 비동기화한 코드를 기반으로 유닛 테스트를 작성함.

<br />
<br />