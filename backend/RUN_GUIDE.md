# 백엔드 서버 실행 가이드

이 프로젝트의 백엔드 서버를 실행하는 두 가지 방법입니다.

## 방법 1: 자동 스크립트 실행 (Windows 전용)

프로젝트 최상위 폴더(`vibe_coding`)에서 `setup_backend.bat` 파일을 실행하면 가상환경 설정, 패키지 설치, 서버 실행이 한 번에 처리 됩니다. (Mac 사용자는 방법 2를 이용해 주세요)

**PowerShell 또는 CMD에서 실행 시:**

```powershell
# 프로젝트 루트 경로에서 실행
.\setup_backend.bat
```

_(참고: `backend` 폴더가 아니라 그 상위 폴더인 프로젝트 루트에서 실행해야 합니다.)_

---

## 방법 2: 수동으로 실행

직접 단계별로 실행하려면 다음 명령어를 순서대로 입력하세요.

### 1. 백엔드 폴더로 이동

```powershell
cd backend
```

### 2. 가상환경 활성화 (Windows)

```powershell
.\venv\Scripts\Activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

_(가상환경이 활성화되면 프롬프트 앞에 `(venv)`가 표시됩니다.)_

### 3. 패키지 설치 (필요한 경우)

```powershell
pip install -r requirements.txt
```

### 4. 서버 실행

```powershell
python app.py
```

---

## 서버 접속

서버가 정상적으로 실행되면 다음 주소로 접속할 수 있습니다:

- URL: `http://127.0.0.1:5001`

---

## 문제 해결 (Troubleshooting)

### "source: no such file or directory: venv/bin/activate" 오류가 발생할 때

이 오류는 `venv` 폴더가 Windows 환경에서 생성되어(혹은 복사되어) Mac/Linux용 `bin` 폴더 대신 Windows용 `Scripts` 폴더만 있을 때 발생합니다.

해결 방법: 기존 `venv`를 삭제하고 다시 만드세요.

```bash
# 1. 기존 venv 삭제
rm -rf venv

# 2. 새 venv 생성
python3 -m venv venv

# 3. 활성화
source venv/bin/activate

# 4. 패키지 설치
pip install -r requirements.txt
```
