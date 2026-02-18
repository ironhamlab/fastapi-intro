## Chapter 11. 데이터베이스 연결과 DB 모델
<br />

### 01. MySQL 컨테이너 실행

docker compose 를 이용하면 MySQL 도 쉽게 설치 가능. 

로컬에 MySQL 이 설치되어 있다면 그쪽을 사용해도 상관없지만, ToDo 앱의 컨테이너와 연결하거나 로컬 MySQL 을 오염시키지 않고 사용할 수 있기 때문에 지금부터 설명할 단계에 따라 컨테이너를 만들어 실행하는 것을 추천함.

※ SQLite 의 경우는 기본적인 SQL 문은 지원하지만 데이터 타입의 종류가 적고, 애초에 파일 기반이라 확장(scalability)을 위한 분산 구성이 어려운 점 등, 향후 프로젝트가 커졌을 때 부딪히는 문제가 많으므로 현실적인 웹 애플리케이션의 데이터베이스로 채택된 사례는 많지 않음. 이 책에서도 14장 테스트 코드에서는 SQLite 를 사용하지만, 프로덕션 코드(테스트 코드가 아닌 코드)에서는 좀 더 실용적인 앱 개발을 목표로 하여, 그대로 실제 서비스로 확장할 수 있도록 MySQL 을 사용함.

<br />

docker-compose.yml 에 demo-app 과 함께 demo 라는 이름의 데이터베이스를 가진 db 서비스를 추가함.

이미 docker compose up 으로 FastAPI 가 실행된 상태라면, 중지하여 다시 docker compose up 을 실행하게 되면 ToDo 앱과 MySQL 이 동시에 실행됨.

<br />

컨테이너 내 MySQL 데이터베이스에 접근할 수 있는지 확인하기 위해,

docker compose up 이 실행된 상태에서 다른 터미널을 열고, 프로젝트 디렉터리에서 다음 명령어를 실행 시,

```shell
# "db" 컨테이너 안에서 "mysql demo" 명령어를 실행
$ docker compose exec db mysql demo
```

MySQL 클라이언트가 실행되고 DB 에 접속된 것을 볼 수 있음.



<br />
<br />

---

### 02. 앱에서 DB에 접속하기 위한 준비

<br />

> ### MySQL 클라이언트 설치
FastAPI 에서는 MySQL 과의 연결을 위해 **sqlalchemy** 라는 ORM(Object-Relational Mapper) 라이브러리를 사용함. ORM은 객체지향 프로그래밍과 데이터베이스 간의 연결을 쉽게 해 주는 기술임. 이를 통해 데이터베이스의 데이터를 객체로 다루고, 객체를 데이터베이스에 저장하거나 조회할 수 있음. **sqlalchemy** 는 파이썬에서는 상당히 대중적인 라이브러리로, Flask 등 다른 웹 프레임워크에서도 사용됨.

※ ORM 은 파이썬 객체를 MySQL 과 같은 관계형 데이터베이스(RDBMS)의 데이터 구조로 변환함. MySQL 의 경우 테이블 구조를 클래스로 정의하면 이를 읽거나 저장하는 SQL 문을 발행해줌.

<br />

**sqlalchemy** 는 백엔드에 다양한 데이터베이스를 이용할 수 있음. 이번에는 MySQL 클라이언트로 **pymysql** 도 함께 설치함. 5 장과 마찬가지로 demo-app 이 실행된 상태에서 poetry add 를 실행하여 두 의존성 패키지를 설치함.

```shell
# "demo-app" 컨테이너에서 "poetry add sqlalchemy pymysql" 을 실행
$ docker compose exec demo-app poetry add sqlalchemy pymysql
```

<br />

설치 시 pyproject.toml 과 poetry.lock 의 내용이 변경된 것을 확인할 수 있음.

<br />
<br />

> ### DB 연결 함수

프로젝트 루트에 다음과 같이 **api/db.py** 를 추가

```python
# api/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DB_URL = "mysql+pymysql://root@db:3306/demo?charset=utf8"


db_engine = create_engine(DB_URL, echo=True)
db_session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


Base = declarative_base()


def get_db():
    with db_session() as session:
        yield session
```

<br />

DB에 정의한 MySQL 의 Docker 컨테이너에 접속할 세션을 생성하고 있음.

라우터에서는 get_db() 함수로 이 세션을 가져와 DB 에 접근할 수 있도록 함.


<br />
<br />

---

### 03. SQLAlchemy의 DB 모델 정의

ToDo 앱을 위해 두 개의 테이블을 정의

<br />

**표 1. tasks 테이블 정의**
| 컬럼명 | Type | 비고 |
| --- | --- | --- |
| id | INT | primary, auto increment |
| title | VARCHAR(1024) |

<br />

**표 2. tasks 테이블 정의**
| 컬럼명 | Type | 비고 |
| --- | --- | --- |
| id | INT | primary, auto increment, foreign key(task.id) |

<br />

Tasks 의 레코드는 작업 하나하나에 대응하며, dones 는 Tasks 중 완료도니 작업만 해당 Task 와 동일한 id 의 레코드를 가짐.

여기서 Tasks 의 id 와 dones 의 id 는 1:1 매핑(mapping)(1:1 대응)으로 설정되어 있음.

보통 1:1 매핑의 경우 정규화 측면에서 하나의 테이블로 하는 경우가 많지만, 이 책에서는 Task 와 done 의 리소스를 명확하게 분리하여 이해하기 쉽도록 별도의 테이블로 정의함.

<br />
<br />

다음과 같이 **api/models/task.py** 를 작성함
```python
# api/models/task.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


from api.db import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(1024))


    done = relationship("Done", back_populates="task", cascade="delete")



class Done(Base):
    __tablename__ = "dones"

    id = Column(Integer, ForeignKey("tasks.id"), primary_key=True)


    task = relationship("Task", back_populates="done")
```

<br />

Column 은 테이블의 각 컬럼을 나타냄. 첫 번째 인수에는 컬럼의 타입을 전달함. 그리고 두 번째 인수 이후에 컬럼의 설정을 작성함. 위의 primary_key=True 나 ForeignKey("tasks.id") 외에도, Null 제약 조건(nullable=False), Unique 제약 조건(unique=True) 등을 지원함.

relationship 은 테이블(모델 클래스) 간의 관계를 정의함. 이를 통해 Task 객체에서 Done 객체를 참조하거나 그 반대도 가능해짐.

cascade="delete" 를 지정하면 12 장에서 구현하는 DELETE /tasks/{task_id} 인터페이스에서 Task 를 삭제할 때, 외부 키에 지정된 동일한 id 의 done 이 있으면 자동으로 삭제됨.


<br />
<br />

> ### DB 마이그레이션

작성한 ORM 모델을 바탕으로 DB에 테이블을 생성하고, DB 마이그레이션(이관)용 스크립트를 작성함.

**api/migrate_db.py**
```python
from sqlalchemy import create_engine


from api.models.task import Base


DB_URL = "mysql+pymysql://root@db:3306/demo?charset=utf8"
engine = create_engine(DB_URL, echo=True)



def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)



if __name__ == "__main__":
    reset_database()
```

<br />
<br />

다음처럼 스크립트를 실행하여 Docker 컨테이너의 MySQL에 테이블을 작성. 이미 같은 이름의 테이블이 있는 경우 삭제한 후 재작성됨.

```shell
# api 모듈의 migrate_db 스크립트를 실행
$ docker compose exec demo-app poetry run python -m api.migrate_db
```


=> DB 에 테이블 생성 완료!


<br />
<br />

> ### 확인

실제로 테이블이 생성되었는지 확인할 차례.

docker compose up 으로 컨테이너가 실생된 상태에서 MySQL 클라이언트 실행

```shell
$ docker compose exec db mysql demo
```

<br />

다음처럼 SQL 문을 입력하여 DB 의 내용을 확인

```mysql
mysql> SHOW TABLES;
+----------------+
| Tables_in_demo |
+----------------+
| dones          |
| tasks          |
+----------------+
2 rows in set (0.00 sec)

mysql> DESCRIBE tasks;
+-------+---------------+------+-----+---------+----------------+
| Field | Type          | Null | Key | Default | Extra          |
+-------+---------------+------+-----+---------+----------------+
| id    | int           | NO   | PRI | NULL    | auto_increment |
| title | varchar(1024) | YES  |     | NULL    |                |
+-------+---------------+------+-----+---------+----------------+
2 rows in set (0.01 sec)

mysql> DESCRIBE dones;
+-------+------+------+-----+---------+-------+
| Field | Type | Null | Key | Default | Extra |
+-------+------+------+-----+---------+-------+
| id    | int  | NO   | PRI | NULL    |       |
+-------+------+------+-----+---------+-------+
1 row in set (0.00 sec)

```

