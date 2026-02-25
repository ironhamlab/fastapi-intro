## Chapter 14. 유닛 테스트
<br />

### 01. 테스트 관련 라이브러리 설치

DB 를 중심으로 비동기 처리를 하므로, 테스트도 비동기 처리에 대응해야 함. 몇 가지 파이썬 라이브러리를 설치함.

이 책에서는 파이썬에서 유명한 유닛 테스트 프레임워크인 pytest 를 사용함. pytest 를 비동기용으로 확장하는 pytest-asyncio 를 설치함.

DB 의 경우, 앞 장의 프로덕션 코드에서는 MySQL 을 사용했음. 하지만 테스트할 때마다 MySQL에 데이터베이스를 작성하고 삭제하면 Docker 에 의해 환경이 제한되어 있다고는 해도 오버헤드가 큼. 따라서 여기서는 파일 기반의 SQLite 를 베이스로 한 SQLite 의 온메모리 모드를 사용할 것임.

MySQL 의 비동기 클라이언트로 aiomysql 을 설치한 것과 마찬가지로, SQLite 의 비동기 클라이언트로 aiosqlite 를 설치함.

이 장의 유닛 테스트에서는 정의한 FastAPI 의 함수를 직접 호출하지 않고 HTTP 인터페이스를 사용하여 실제 요청과 응답을 검증함. 이를 위해 필요한 비동기 HTTP 클라이언트 httpx 를 설치함.

docker compose up 을 실행해 demo-app 이 동작된 상태에서 다음 명령을 실행
```shell
$ docker compose exec demo-app poetry add -G dev pytest-asyncio aiosqlite httpx
```

<br />

여기서 -G 는 Poetry 의 의존 라이브러리를 그룹화하는 옵션임. 이번에는 -G dev 로 dev 그룹을 지정하여 프로덕션 환경의 일반적인 배포에서는 건너뛰는, 테스트나 개발 시 로컬 환경에서만 사용할 라이브러리를 설치함. 이를 통해 프로덕션 환경에서는 불필요한 라이브러리를 설치하지 않아도 되고, 컨테이너로 설치하는 경우에도 컨테이너의 이미지 크기를 줄이고 빌드 시간을 단축할 수 있음.

위 명령어로 각 라이브러리가 설치되어 pyproject.toml 과 poetry.lock 이 업데이트 됨.

[tool.poetry.group.dev.depencencies] 에 라이브러리가 추가됨.

<br />
<br />

---

### 02. DB 접속 및 테스트 클라이언트 준비

유닛 테스트를 위해 프로젝트 바로 아래에 tests 디렉터리를 작성함.
빈 파일인 __ init __.py 와 테스트 파일인 test_main.py 를 생성함. 결과적으로 다음과 같은 디렉터리 구성이 됨.

<br />

**tests 디렉터리를 포함한 프로젝트 디렉터리 구성**
```
(project root)
├──  Dockerfile
├── docker-compose.yml
├── poetry.lock
├── pyproject.toml
├── api/
│   ├── __init__.py
│   ├── db.py
│   ├── main.py
│   ├── migrate_db.py
│   ├── cruds/
│   ├── models/
│   ├── routers/
│   └── schemas/
└── tests
    ├── __init__.py
    └── test_main.py
```

<br />

먼저 pytest 의 픽스처(fixture)를 정의함. 픽스처는 테스트에서 반복적으로 사용되는 설정이나 데이터를 한 곳에 모아 관리하는 개념임.

픽스처는 테스트 함수의 전처리나 후처리를 정의하는 함수로, xUnit 계열의 유닛 테스트 도구에서 말하는 setup() 이나 teardown() 에 해당하는데, 파이썬에서는 yield 문이 있으므로, 이들을 하나의 함수로 묶어 정의할 수 있음. 여기서는 pytest-asyncio 를 사용하므로 픽스처 함수에는 @pytest_asyncio.fixture 데코레이터를 부여함.

테스트용으로 DB 연결을 모두 정의해야 하므로 조금 복잡함. 다음과 같은 작업을 수행함.

1. 비동기식 DB 접속용 engine 과 session 을 작성
2. 테스트용으로 온메모리 SQLite 테이블을 초기화 (함수별로 재설정)
3. DI 로 FastAPI 가 테스트용 DB 를 참조하도록 변경
4. 테스트용으로 비동기 HTTP 클라이언트를 반환

<br />

**tests/test_main.py**
```python
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


from api.db import get_db, Base
from api.main import app


ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"



@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    # 비동기식 DB 접속을 위한 엔진과 세션을 작성
    async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
    async_session = sessionmaker(
        autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
    )


    # 테스트용으로 온메모리 SQLite 테이블을 초기화 (함수별로 재설정)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    

    # 의존성 주입으로 FastAPI 가 테스트용 DB 를 참조하도록 변경
    async def get_test_db():
        async with async_session() as session:
            yield session
    

    app.dependency_overrides[get_db] = get_test_db  # 1


    # 테스트용으로 비동기 HTTP 클라이언트를 반환
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

<br />

여기서 중요한 것은 12장에서 설명한 get_db 의 오버라이드임.

<br />

라우터는 다음과 같이 정의했음.

**api/routers/task.py**
```python
@router.post("/tasks", response_model=task_schema.TaskCreateResponse)
async def create_task(
    task_body: task_schema.TaskCreate, db: AsyncSession = Depends(get_db)
    ):
```

get_db 함수는 일반적으로 api/db.py 에서 가져오는 함수임.

하지만 픽스처에서 app.dependency_overrides[get_db] = get_test_db 로 정의함으로써, 위의 API 가 호출될 때 get_db 대신 get_test_db 를 사용하도록 오버라이드 하고 있음 (#1)

덕분에 유닛 테스트를 위해 프로덕션 코드인 router 의 내용을 다시 작성할 필요가 없음. 이것이 바로 의존성 주입의 힘임!!


<br />
<br />

---

### 03. 테스트 작성하기(1)

이제 실제로 테스트 코드를 작성함.

비동기 pytest 함수로, @pytest.mark.asyncio 데코레이터를 가진 async def 로 시작하는 코루틴을 작성함.

**tests/test_main.py**
```python
import starlette.status



@pytest.mark.asyncio
async def test_creat_and_read(async_client):
    response = await async_client.post("/tasks", json={"title": "테스트 작업"})  # 1
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert response_obj["title"] == "테스트 작업"


    response = await async_client.get("/tasks")  # 2
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert len(response_obj) == 1
    assert response_obj[0]["title"] == "테스트 작업"
    assert response_obj[0]["done"] is False
```

<br />

함수의 인수에 test_create_and_read(async_client)로 방금 정의한 async_client 픽스처를 정의함. 그러면 픽스처의 반환값이 들어간 상태에서 함수가 실행되므로 async_client.post() 와 같이 클라이언트를 이용할 수 있음.

이 함수에서는 먼저 POST 호출을 통해 ToDo 작업을 생성하고 (#1), 이어서 GET 호출을 통해 생성한 ToDo 작업을 확인함 (#2)

각각 처음에 json={"title": "test Task"} 로 전달한 작업(Task)이 반환되는 것을 확인할 수 있음.


<br />
<br />

---

### 04. 테스트 작성하기(2)

다음으로 완료 플래그를 이용한 테스트로 추가해 봄.

12 장에서 설명한 것처럼 완료 플래그의 ON/OFF 를 여러 번 호출했을 때 올바른 상태 코드가 반환되는지 시나리오를 만들어 테스트해 볼 것임.

<br />

**tests/test_main.py**
```python
@pytest.mark.asyncio
async def test_done_flag(async_client):
    response = await async_client.post("/tasks", json={"title": "테스트 작업2"})
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert response_obj["title"] == "테스트 작업2"


    # 완료 플래그 설정
    response = await async_client.put("/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_200_OK


    # 이미 완료 플래그가 설정되어 있으므로 400 을 반환
    response = await async_client.put("/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_400_BAD_REQUEST


    # 완료 플래그 해제
    response = await async_client.delete("/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_200_OK


    # 이미 완료 플래그가 해제되었으므로 404 를 반환
    response = await async_client.delete("/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_404_NOT_FOUND
```

<br />

이 테스트는 비동기 HTTP 클라이언트(async_client)를 사용하여 Tasks 엔드포인트에 대한 다양한 동작을 확인하고 있음.

테스트가 시작될 때, /tasks 엔드포인트에 POST 요청을 보내 "테스트 작업2" 라는 제목을 갖는 작업을 생성함. 그 후, 생성된 작업에 대한 응답이 200 OK 이며, 제목이 "테스트 작업2" 인지 확인함.

다음으로 /tasks/1/done 엔드포인트에 PUT 요청을 보내 완료 플래그를 설정함. 이때 응답이 200 OK 인지 확인함. 그리고 다시 같은 엔드포인트에 PUT 요청을 보내 완료 플래그가 이미 설정되어 있으므로 400 BAD REQUEST 를 예상하고 있음.

그 후 /tasks/1/done 엔드포인트에 DELETE 요청을 보내 완료 플래그를 해제함. 이때 응답이 200 OK 인지 확인함. 그리고 다시 같은 엔드포인트에 DELETE 요청을 보내 완료 플래그가 이미 해제되어 있으므로 404 NOT FOUND 를 예상하고 있음.

<br />
<br />

---

### 05. 테스트 실행하기

마지막으로 지금까지 작성한 테스트를 실행함.

프로젝트의 루트 디렉터리에서 다음 명령어를 실행함.

```shell
$ docker compose run --entrypoint "poetry run pytest" demo-app
```

테스트가 성공하면 {테스트 수} passed 라고 표시되며 종료됨.

실패하면 {실패한 테스트 수} failed, {성공한 테스트 수} passed 가 동시에 표시됨.

<br />
<br />

# => 잠깐 ; 책이랑 달라진 부분 생김

<br />

**tests/test_main.py**
```python
AsyncClient(app=app, base_url="http://test")
```

-> 이거 지금 에러남 ;;;; 이건 httpx 0.24 이전 문법이라고 함....


<br />

**에러메시지**
```
TypeError: AsyncClient.__init__() got an unexpected keyword argument 'app'
```
=> httpx 최신 버전에서는 **AsyncClient(app=app)** 문법이 삭제됨 ..!!!!!

<br />

지금 환경에서는 **ASGITransport 를 직접 써야함**


❌ 기존 코드
```python
async with AsyncClient(app=app, base_url="http://test") as client:
    yield client
```

<br />

✅ 수정 코드 (정식 방법)
```python
from httpx import AsyncClient, ASGITransport

transport = ASGITransport(app=app)

async with AsyncClient(
    transport=transport,
    base_url="http://test"
) as client:
    yield client
```

<br />
<br />

📌 왜 이렇게 바뀌었나

* httpx에서 FastAPI 직접 의존 제거

* httpx에서
  * HTTP 클라이언트 역할
  * ASGI 앱 실행 책임

    을 명확히 분리

* ASGI 앱은 transport로 명시해야 함

* 그래서:
  * 앱 → ASGITransport
  * 요청 → AsyncClient

  <br />

  아래처럼 역할이 나뉨:

  ```
  FastAPI app
    ↓
  ASGITransport
    ↓
  AsyncClient
  ```

* 테스트 구조가 더 명확해짐

---

<br />

코드 고친 후 재실행 시, **2 passed, 8 warnings** 뜸

Pydantic v1 → v2 변경사항 때문에 마이그레이션 경고 뜸.

지금 당장 고칠 필요는 없지만, 2026년 기준 FastAPI + Pydantic v2 환경에서는

* Config 방식
* .dict()

곧 제거될 수 있으므로 언젠가는 고쳐야 함.

<br />

## 🧠 무엇을 고쳐야 하나?

### 1️⃣ orm_mode 제거

❌ 기존

```python
class Config:
    orm_mode = True
```

✅ 수정
```python
from pydantic import ConfigDict

model_config = ConfigDict(from_attributes=True)
```

<br />

### 2️⃣ .dict() → model_dump()

❌ 기존

```python
task_create.dict()
```

✅ 수정
```python
task_create.model_dump()
```

<br />

### 3️⃣ Field(example=...) 변경

❌ 기존

```python
Field(None, example="세탁소에 맡긴 것을 찾으러 가기")
```

✅ 수정
```python
Field(
    None,
    json_schema_extra={"example": "세탁소에 맡긴 것을 찾으러 가기"}
)
```


<br />
<br />
<br />

---

### 06. parametrize 테스트

지금까지 작성한 유닛테스트의 응용으로, 마지막으로 parametrize 테스트에 대해 소개.

parametrize 테스트는 동일한 테스트를 여러 입력 값 또는 조건에 대해 반복하여 실행할 수 있도록 도와줌.

parametrize 테스트는 여러 개의 테스트 케이스를 하나의 함수로 다루고 싶을 때 힘을 발휘함. 처음에는 parametrize 를 사용하지 않고 테스트를 작성하고, parametrize 로 다시 작성해 볼 것임.



--------ROI를 고려해 parametrize 테스트의 경우 추후 필요시 다시 진행하기로 결정함---------