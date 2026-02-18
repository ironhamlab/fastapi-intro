## Chapter 8. 라우터
<br />

### 01. 경로 동작 함수에 대하여

라우터에는 6장에 등장한 경로 동작 함수(path operation function)를 정의함.

경로 동작 함수는 경로(path)와 동작(operation)의 조합으로 정의된다고 설명했음. 앞 장에서 설명한 REST API의 엔드포인트와 HTTP 메서드에 각각 대응됨.

<br />

ToDo 앱을 만들기 위해 라우터에 다음과 같은 6가지 경로 동작 함수를 정의하게 됨.

* GET /tasks
* POST /tasks
* PUT /tasks/{task_id}
* DELETE /tasks/{task_id}
* PUT /tasks/{task_id}/done
* DELETE /tasks/{task_id}/done


<br />
<br />

---

### 02. 경로 동작 함수 만들기

6개의 함수를 하나의 파일에 담게 되면, 구현 상태에 따라서는 파일 크기가 커져 보기 좋지 않을 수 있음. 함수에 기능을 추가할 때마다 파일 크기가 커지므로 미리 명확하게 분할해 놓아야 더욱 실용적인 설계가 될 수 있음.

분할은 **리소스 단위**로 하는 것을 추천!!

이번 ToDo 앱의 경우 크게 
* **/tasks**
* **/tasks/{task_id}/done**

두 개의 리소스로 나눌 수 있으므로, 각각을
* **api/routers/task.py**
* **api/routers/done.py**

에 작성함.


<br />

**api/routers/task.py**
```python
from fastapi import APIRouter


router = APIRouter()


@router.get("/tasks")
async def list_tasks():
    pass


@router.post("/tasks")
async def create_task():
    pass


@router.put("/tasks/{task_id}")
async def update_task():
    pass


@router.delete("/tasks/{task_id}")
async def delete_task():
    pass
```

<br />

**api/routers/done.py**
```python
from fastapi import APIRouter


router = APIRouter()


@router.put("/tasks/{task_id}/done")
async def mark_task_as_done():
    pass


@router.delete("/tasks/{task_id}/done")
async def unmark_task_as_done():
    pass
```


※ 작성 시, pass 는 '아무것도 하지 않는 문장'을 의미함. 일반적으로 함수는 return 문으로 값을 반환한 뒤 종료하지만, 아무것도 반환하지 않는 함수의 경우 return을 쓸 필요는 없음. 하지만 파이썬은 들여쓰기에 엄격하므로, 아무것도 처리하지 않는 함수를 그대로 두면 함수의 내용을 찾을 수 없어 들여쓰기 오류가 발생함. 그래서 이후에 내용을 구현할 예정임을 쉽게 알 수 있도록 pass 라고 써 두고 넘어가는 것임.

<br />
<br />

**task.py** 와 **done.py** 1차 작성으로, routers의 플레이스홀더(Placeholder) 준비는 끝났음. 

※ 플레이스홀더 : 문자나 이미지 등의 요소가 들어갈 자리를 임시로 채워놓은 내용물

<br />

하지만 이것만으로는 Swagger UI에 나타나지 않음. 위의 두 파일로 작성한 router 인스턴스를 FastAPI 인스턴스로 가져와야 함. **api/main.py**를 다시 작성함.

```python
from fastapi import FastAPI


from api.routers import task, done


app = FastAPI()
app.include_router(task.router)
app.include_router(done.router)
```



<br />
<br />

---

### 03. 동작 확인

지금까지의 작업을 통해 Swagger UI에 6개의 경로 동작 함수에 해당하는 엔드포인트가 추가되었음.

Docker에 FastAPI 환경을 구축할 때 변경 사항을 즉시 반영하는 핫 리로드(hot reload) 옵션(--reload)을 추가했으므로, 파일을 저장하면 Swagger UI를 열었을 때 최신 상태가 반영되어 있을 것임. (환경에 따라 최대 20초 정도 걸릴 수 있음)

Swagger UI의 각 함수에는 함수명을 바탕으로 자동 생성된 설명이 덧붙여짐. 가능한 한 이해하기 쉽고 본문을 잘 표현하는 함수 이름을 붙이는 게 좋음.

지금까지의 구현은 단지 플레이스홀더를 준비한 것에 불과하므로, Response body 에는 null 만 반환됨.

다음장에서 스키마(scheme)를 사용해 정형화된 값을 채워 응답을 반환하도록 정의할 예정.