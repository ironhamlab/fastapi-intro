## Chapter 5. FastAPI 설치

<br />

### 01. Poetry를 통한 파이썬 환경 구축

**Poetry**는 파이썬의 패키지 관리를 해 주는 도구이자, 패키지 간의 의존 관계를 해결해줌.

Python에서 가장 원시적인 패키지 관리 도구로 **pip** 가 유명하지만, Poetry는 pip가 하지 못하는 패키지 간 의존성 해결, lock 파일을 이용한 버전 고정, 파이썬의 가상 환경 관리 등 더욱 기능적이고 현대적인 버전 관리 가능

<br />

처음에는 Poetry가 의존성을 관리하기 위해 사용하는 pyproject.toml이 존재하지 않으므로, Poetry를 사용하여 FastAPI를 설치하기 위해 의존성을 설명하는 pyproject.toml을 작성

```shell
 $ docker compose run \
 --entrypoint "poetry init \
   --name demo-app \
   --dependency fastapi \
   --dependency uvicorn[standard]" \
 demo-app
```

=> 위 명령어는 조금 복잡하지만, 방금 만든 Docker 컨테이너(demo-app) 안에서 poetry init 명령어를 실행하고 있음. 인수로 fastapi와 ASGI 서버인 uvicorn을 설치할 의존 패키지로 지정하고 있음.

명령 실행 시 대화 상자가 시작되는데, 이 때 Author 부분에만 n을 입력하고, 그 외에는 모두 Return(Enter) 눌러 진행.

설치 완료 시 프로젝트 디렉터리 바로 아래에 **pyproject.toml** 생성 확인

<br />
<br />

---

### 02. FastAPI 설치

앞서 FastAPI를 종속 패키지로 포함하는 Poetry의 정의 파일을 만들었음.

다음 명령어로 FastAPI가 포함된 패키지 설치

```shell
 $ docker compose run --entrypoint "poetry install --no-root" demo-app
```

=> 의존 패키지 다운로드가 시작되고 설치가 완료됨. --no-root 옵션으로 앞으로 생성할 demo-app 패키지 자체를 Poetry의 설치 대상에서 제외.

설치 완료 시 프로젝트 디렉터리 바로 아래에 **poetry.lock** 파일 생성 확인


poetry.lock 은 poetry install 시 생성되며, 실제로 설치한 패키지의 정보가 기록되어 있음. 이것으로 다른 환경에서 새로 poetry install 을 실행했을 때에도 똑같은 패키지 버전 설치 가능!

<br />

poetry init과 poetry install 두 명령어로 **pyproject.toml** 과 **poetry.lock** 파일이 준비되었음. 이로써 Docker 이미지를 처음부터 만들 때, FastAPI를 포함한 파이썬 환경을 이미지에 포함시킬 수 있게 되었음. 새로운 파이썬 패키지를 추가한 경우, 이미지를 다시 빌드하면 **pyproject.toml** 이 포함된 모든 패키지 설치 가능!

<br />

```shell
 $ docker compose build --no-cache
```

=> --no-cache 옵션 추가 시 **pyproject.toml** 등에 변경이 있을 때 캐시를 이용하지 않고 다시 빌드 실행

<br />
<br />

---

### 03. 로컬 개발 환경 정비

로컬에서 개발할 경우 IDE를 사용하는 경우가 많은데, Docker 컨테이너 내의 파이썬 환경은 로컬 환경과 경로 정의가 다르기 때문에 그대로는 패키지 참조 불가. 오류를 나타내는 밑줄이 표시되어 버림.

* Pycharm : Professional 버전에서 docker compose 인터프리터 사용 가능

* VSCode : Dev Containers 의 구조를 사용하여 Docker 컨테이너 내의 파일을 직접 편집 가능.

<br />

IDE가 Docker 환경을 지원하지 않는 경우, Docker 컨테이너 내부뿐만 아니라 로컬 환경에서도 poetry install 을 실행하면 IDE가 파이썬 및 FastAPI 환경을 인식하여 구문 강조 등 편리한 기능 사용 가능. 이 경우에는 다른 구성원이나 다른 단말과 환경 차이 발생 가능!