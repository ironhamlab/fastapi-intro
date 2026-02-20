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
+ ASYNC_DB_URL = "mysql+pymysql://root@db:3306/demo?charset=utf8"  # 1

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

**api/db.py**
```python
```

**api/db.py**
```python
```

<br />
<br />

---

### 04. 비동기 대응 CRUDs

