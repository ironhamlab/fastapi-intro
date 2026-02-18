## Chapter 9. 스키마 - 응답
<br />

### 01. 타입 힌트

파이썬은 동적 타입 언어(Dynamic Typed Language)로, 변수에 할당되는 값에 따라 데이터 타입이 동적으로 결정되는 언어임.

파이썬에서도 타입 힌트 기능이 도입되었음. 타입 힌트를 사용하면, 코드를 작성하는 시점에서는 아직까지 동적으로 타입이 결정되지만, 코드 내에 명시된 타입 힌트를 통해 함수의 시그니처(signature)를 더 명확하게 나타낼 수 있음.

함수의 시그니처는 해당 함수를 유일하게 식별할 수 있는 정보를 담고 있는 개념임. 주로 함수의 이름과 파라미터의 개수, 타입, 반환 값의 타입을 포함함. 함수 시그니처는 함수를 호출할 때 필요한 정보를 제공하며, 이를 통해 컴파일러나 인터프리터가 올바른 함수를 찾아 실행할 수 있음.

<br />

보통 타입 힌트는 실행 시(runtime)에는 영향을 주지 않고(코드의 내용에는 아무런 영향을 주지 않고), IDE 등에 타입 정보를 제공하는 역할을 함. 하지만 FastAPI가 의존하는 Pydantic이라는 강력한 라이브러리를 통해 타입 힌트를 적극적으로 활용하여 API 입출력의 유효성 검사를 수행함.

Pydantic은 파이썬에서 데이터 모델을 정의하고, 데이터 유효성을 검사하는 라이브러리임. 데이터의 형식을 정하고 이를 확인하여 안정성을 높이며, 사용자가 이해하기 쉬운 오류 메시지를 제공하여 문제를 해결하는 데 도움을 줌.

<br />
<br />

'실행 시 영향을 미치지 않는다'는 것은 무엇을 의미할까?

예를 들어, int 타입일 것으로 예상하고 변수 num을 다음과 같이 정의했는데,
```python
# 파이썬 인터프리터
 >>> num: int = 1
```

<br />

여기에 실수로 문자열 타입인 "string"을 대입하려고 함.
```python
# 파이썬 인터프리터
 >>> num = "string"
```

<br />

=> 이 때 파이썬은 오류를 발생시키지 않음.

처음 제시한 **: int*** 는 타입 힌트일 뿐, 정적 타입 언어(Statically Typed Language)처럼 변수의 타입을 제한하는 것은 아님. 여기서 정적 타입 언어란 프로그램을 컴파일할 때 변수의 타입을 결정하고 이를 명시적으로 선언해야 하는 언어를 의미함.

다음 결과를 보면 변수의 타입이 str 인 것을 알 수 있음.
```python
# 파이썬 인터프리터
 >>> num
 "string"
 >>> type(num)
 <class 'str'>
```

<br />
<br />

---

### 02. 응답 타입 정의

앞서 설명한 경로 동작 함수에 응답 타입을 정의.

**api/schemas/task.py** 작성
```python
from pydantic import BaseModel, Field


class Task(BaseModel):
    id: int
    title: str | None = Field(None, example="세탁소에 맡긴 것을 찾으러 가기")
    done: bool = Field(False, description="완료 플래그")
```

이 파일은 FastAPI의 스키마를 나타냄.

API의 스키마는 API 요청과 응답의 타입을 정의하기 위한 것으로, 데이터베이스의 스키마와는 다름.

먼저 이 스키마를 이용하여 실제로 API 응답을 반환할 수 있는지 확인해 볼 것임. 앞 장에서 작성한 **api/routers/task.py** 의 list_tasks() 함수를 다시 작성

<br />

**api/routers/task.py** 의 **list_tasks() 함수** 재작성
```python
from fastapi import APIRouter

import api.schemas.task as task_schema


router = APIRouter()


@router.get("/tasks", response_model=list[task_schema.Task])
async def list_tasks():
    return [task_schema.Task(id=1, title="첫 번째 ToDo 작업")]

```
여기서는 **api.schemas.Task** 를 **task_schema** 로 이름을 바꾸어 임포트하고 있음. 나중에 11장에서 DB와 연결해 모델(models)을 정의할 때, 같은 이름의 파일 **api/models/task.py**를 정의하여 이를 task_model 로 바꾸어 구분하기 위해서임.

이제 Swagger UI에 접속하면 API에 응답(Response body)이 추가된 것을 확인할 수 있음.

<br />

> **GET /tasks** 응답 확인
* Code : 200
* Response body :
  ```json
  [
    {
      "id": 1,
      "title": "첫 번째 ToDo 작업",
      "done": false
    }
  ]
  ```


<br />
<br />

---

### 03. 응답 타입 정의에 대한 설명

**api/schemas/task.py**
```python
class Task(BaseModel):
    id: int
    title: str | None = Field(None, example="세탁소에 맡긴 것을 찾으러 가기")
    done: bool = Field(False, description="완료 플래그")
```

<br />

FastAPI의 스키마 모델임을 나타내는 BaseModel 클래스를 상속받아 Task 클래스를 만들고 있음.

Task 클래스는 id, title, done 의 3가지 필드를 가짐. 각 필드에는 int, str | None, bool 의 타입 힌트가 추가되어 있음.

※ **str | None** 의 경우 파이썬 3.9 이전에는 Optional[str] 이라고 사용했음. ( | 연산자가 존재하지 않았기 때문) 또한 Optional 을 사용하려면 typing 모듈을 이용하는 **from typing import Optional** 이라는 문장이 필요했음. 파이썬 3.10 이후에도 Optional 표기 사용 가능!

<br />

또한 오른쪽의 Field 는 필드에 대한 부가적인 정보를 기술함. 첫 번째 변수는 필드의 기본값을 나타냄. title 은 None, done 은 False 를 기본값으로 설정하고 있음.

example 은 필드의 값을 예를 들어 설명함. title 은 각 ToDo 작업의 제목임.

done 은 완료 플래그를 나타냄. description 은 인수에 대해 설명함. 이런 스키마 정의는 Swagger UI 하단에서도 확인 가능.


<br />


※ 추가로 파이썬 3.9 이후에서는 str 의 list 는 list[str] 로 표기하며, 마찬가지로 int 를 key, str 을 value 로 취하는 dict 도 dict[int, str] 과 같이 표기 가능. 하지만 파이썬 3.8 이전에는 Optional과 마찬가지로 typing 모듈을 이용하여 **from typing import List, Dict** 를 미리 임포트한 뒤, List[str] 이나 Dict[int, str] 로 표기해야 했음



<br />
<br />

---

### 04. 라우터에 정의한 응답에 대한 설명

**api/routers/task.py**
```python
@router.get("/tasks", response_model=list[task_schema.Task])
async def list_tasks():
    return [task_schema.Task(id=1, title="첫 번째 ToDo 작업")]

```

<br />

라우터에서는 앞서 정의한 스키마를 이용해 API 요청과 응답을 정의함. **GET /tasks** 에서는 요청 파라미터나 요청 본문을 받지 않으므로 응답만 정의함.

응답의 스키마로 경로 동작 함수의 데코레이터에 response_model 을 설정함. **GET /tasks** 는 스키마에 정의한 Task 클래스를 여러 개 반환하므로 리스트로 정의함. **response_model=list[task_schema.Task]** 가 됨.

현 시점에서는 아직 DB 등과의 연결은 없으며, Task 데이터 저장은 고려되지 않은 상태임. 일단 더미 데이터를 항상 반환하는 함수로 정의해 둠.

id 와 title 을 임의의 내용으로 지정하고, done 은 기본적으로 False 이므로 여기서는 지정하지 않음. 더미데이터로 **[task_schema.Task(id=1, title="첫 번째 ToDo 작업")]** 을 반환함.


<br />
<br />

---

### 05. 타입 정의의 강력함

이번 장에서 스키마를 정의해 보았고, 스키마를 나타내는 클래스의 각 필드에는 엄격하게 타입 힌트를 부여하였음.

FastAPI 에서 타입 힌트는 단순히 IDE의 타입 검사에만 사용되는 것이 아니라 런타임(runtime) 평가에도 사용된다고 설명했음. 

만약 title 의 타입 정의를 **str | None(Optional[str])** 에서 **bool | None(Optional[bool])** 으로 변경하고 Swagger UI 에서 **Get /tasks** 의 API 를 호출해 보면, 응답이 Internal Server Error 로 바뀌게 됨. 또한, 터미널 확인 시 응답의 유효성 검사에 실패한 것을 확인할 수 있음.

<br />

파이썬을 포함한 동적 타입 지정 언어에서는 일반적으로 타입을 의식하지 않기 때문에, 타입 힌트가 없으면 API 가 예상치 못한 타입으로 값을 반환하게 되어 프론트엔드에서 오류가 발생할 수 있음. 타입 불일치를 방지하기 위해서는 유효성 검사가 필요하며, 일반적으로는 title 의 내용이 str 이라는 유효성 검사(validation)를 자체적으로 준비하게 됨.

하지만 지금까지 우리는 유효성 검사 구현을 전혀 하지 않았음! '타입 힌트를 이용해 자동으로 유효성 검사를 해주는 것'이 바로 FastAPI 가 타입 안전하다는 것의 핵심임.

