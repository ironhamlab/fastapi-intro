## Chapter 6. Hello World!

<br />

### 01. Hello World! 표시를 위한 파일 작성

프로젝트 디렉터리 바로 아래에 API 디렉터리를 생성하고, **api/__init__.py** (빈 파일), **api/main.py** 파일을 추가

※ **__init__.py** 는 이 api 디렉터리가 파이썬 모듈임을 나타내는 빈 파일임. (init의 앞뒤로 _가 2개씩 붙어있어야 함!!)

**main.py** 에는 FastAPI의 코드를 적음.

```python
from fastapi import FastAPI


app = FastAPI()


@app.get("/hello")
async def hello():
    return {"message": "hello world!"}
```

<br />
<br />

결과적으로 다음과 같은 디렉터리 구조가 됨.
```
./
├── api/
│   ├── __init__.py
│   └── main.py
├── Dockerfile
├── docker-compose.yml
├── poetry.lock
└── pyproject.toml
```


<br />
<br />

---
### 02. API 실행

프로젝트 디렉터리에서 다음 명령어를 실행하여 API 실행

```shell
 $ docker compose up
```

<br />
<br />

이 상태에서 브라우저에서 아래 URL에 접속

> http://localhost:8000/docs

접속 시 Swagger UI 에  **GET /hello**  라는 엔드포인트 나타남.

1. GUI의 /hello 가 표시된 부분을 클릭
2. 확대된 영역의 오른쪽 'Try it out' 버튼을 클릭
3. 'Execute' 버튼이 나타나면 클릭
4. Responses 에 실행된 파라미터와 그에 대한 응답이 표시됨!

* Code : 200

* Responses body :

  ```JSON
  {
    "message": "hello world!"
  }
  ```


  ※ 기본적으로 응답은 JSON 형식으로 반환됨. 이 외에도 FastAPI는 HTMLResponse, FileResponse 등 다양한 응답 형식을 지원함.


<br />
<br />

이것은 Request URL 에 표시된 바와 같이 실제로는,
> http://localhost:8000/hello

의 API 를 호출했을 때 얻은 응답임.

FastAPI 서버는 포그라운드에서 동작하고 있는 상태로, 필요에 따라 **Ctrl + C** 명령으로 멈출 수 있음.


<br />
<br />

---
### 03. 코드의 의미

앞서 작성한 **main.py** 의 내용을 살펴보자.

```python
app = FastAPI()
```
app은 FastAPI의 인스턴스임. **main.py** 에는 **if __ name __ == "__ main __":** 이라는 문구가 없지만, 실제로는 uvicorn 이라는 ASGI 서버를 통해 이 파일의 app 인스턴스가 참조됨.

<br />

```python
@app.get("/hello")
```
@ 로 시작하는 부분을 파이썬에서는 데코레이터라고 함. 자바의 애너테이션이나 C#의 속성(Attribute)과 비슷한 형식이지만, 파이썬의 데코레이터는 함수를 변형하고 함수에 새로운 기능을 추가함.

FastAPI 인스턴스에 대해서 데코레이터로 수정된 함수를 FastAPI 에서는 경로 동작 함수(path operation function)라고 부름

경로 동작 함수를 구성하는 데코레이터는 다음 두 부분으로 나뉨
* 경로(path)
* 동작(operation)

'경로'는 "/hello" 부분을 가리킴. (엔드포인트)

'오퍼레이션'은 get 부분을 말함. 이 곳은 REST의 HTTP 메서드 부분으로, GET/POST/PUT/DELETE로 대표되는 HTTP 메서드를 정의함.

<br />
<br />

**api/main.py** 의 이 부분에서, def 앞에는 async가 붙어 있음.
```python
@app.get("/hello")
async def hello():
    return {"message": "hello world!"}
```
이는 비동기임을 알려주는 접근제어자(Access Modifier)임.

접근제어자란 클래스의 멤버(변수, 메서드 등)에 대한 접근 권한을 제어하는 데 사용되는 키워드임. 이를 통해 정보 은닉의 개념을 실현하고, 클래스 외부에서의 직접적인 접근을 제어할 수 있음.
