## Chapter 4. Docker 이미지 만들기

<br />


### 01. docker compose 관련 파일 생성

docker-compose.yml 과 Dockerfile 을 생성한 후,

두 파일과 동일한 디렉터리에 .dockervenv 디렉터리 생성 (Docker 내 .venv 디렉터리에 대응)

```shell
 $ mkdir .dockervenv
```

<br />
<br />

---

### 02. 이미지 빌드

docker-compose.yml 이 있는 디렉터리에서 다음 명령어로 Docker 이미지 생성

```shell
 $ docker compose build
```