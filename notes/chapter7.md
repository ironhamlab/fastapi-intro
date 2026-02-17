## Chapter 7. 애플리케이션 개요와 디렉터리
<br />

### 01. ToDo 앱 개요

이 책에서 만드는 것은 간단한 ToDo 앱으로, 다음과 같은 모습임

```
내일 할 일

[x] 재활용 쓰레기 버리기
[ ] 간장 사기
[ ] 세탁소에 맡긴 것을 찾으러 가기
```


<br />
<br />

---

### 02. REST API

REST API에서는 HTTP로 정보를 주고받을 떄 URL로 모든 '리소스'를 정의함. 리소스를 나타내는 엔드포인트와 HTTP 메서드(GET/POST/PUT/DELETE 등)를 조합하여 API 전체를 구성함.

REST에 따라 위의 ToDo 앱을 구현하기 위해 필요한 기능을 정리해 보면 다음과 같음.
* ToDo 리스트 표시하기
* ToDo에 작업 추가하기
* ToDo 작업 설명문을 변경하기
* ToDo 작업 자체를 삭제하기
* ToDo 작업에 '완료' 플래그 달기
* ToDo 작업에서 '완료' 플래그 제거하기

이 외에도 날짜순으로 정렬하거나, 수동으로 순서를 바꾸거나, 중첩된 ToDo 작업을 정의할 수 있도록 하는 등, 다양한 기능을 추가한 앱을 만들 수 있음. 이 책에서는 위의 기본적인 기능을 만들기로 함.

<br />

이 기능들을 REST API에서,

* HTTP메서드 엔드포인트({} 내부는 파라미터)

의 형식으로 적으면 다음처럼 정의 가능

* GET /tasks
* POST /tasks
* PUT /tasks/{task_id}
* DELETE /tasks/{task_id}
* PUT /tasks/{task_id}/done
* DELETE /tasks/{task_id}/done

<br />

물론 이것이 유일한 정답은 아님. PATCH를 사용하거나, '완료' 플래그의 ON/OFF를 동일한 HTTP 메서드로 전환되는 토글로 만들거나, UI나 DB의 사양에 따라 별도의 인터페이스로 정의할 수도 있음.


<br />
<br />

---

### 03. 디렉터리 구조에 대해서

FastAPI에서는 디렉터리 구조나 파일 분할 방법을 엄격하게 정하고 있지 않음. FastAPI의 공식 문서에 권장되는 디렉터리 구조는 나와 있지만, 프로젝트가 커져서 해당 구조를 변경할 경우 대규모 리펙토링을 해야 하는 상황이 발생함.

| https://fastapi.tiangolo.com/ko/tutorial/sql-databases/#file-structure

이 책에서는 미리 디렉터리를 어느 정도 세세하게 나눠놓음. 이를 통해 애플리케이션의 규모가 커져도 견딜 수 있는 코드 베이스를 가진 실용적인 API를 목표로 함.


<br />

다음과 같이 api 디렉터리 아래에 schemas, routers, models, cruds의 네 개의 디렉터리를 준비함.

```
api/
├── __init__.py
├── main.py
├── schemas
│   └── __init__.py
├── routers
│   └── __init__.py
├── models
│   └── __init__.py
└── cruds
    └── __init__.py
```
※ __ init __.py 는 앞 장에서 설명한 것처럼 파이썬 모듈임을 나타내는 빈 파일임.