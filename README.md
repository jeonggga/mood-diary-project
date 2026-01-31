# Mood Diary Project

이 프로젝트는 Vue.js와 Python Flask를 사용하여 개발된 감정 일기장(Mood Diary) 애플리케이션입니다. 사용자는 자신의 감정과 하루 일과를 기록하고 관리할 수 있습니다.

## 📂 프로젝트 구조 (Project Structure)

이 프로젝트는 크게 프론트엔드와 백엔드로 나뉘어 있습니다.

### 1. Frontend (`frontend/`)

- **Framework**: Vue.js 3
- **Build Tool**: Vite
- **Styling**: Tailwind CSS (v4), PostCSS
- **State Management**: Pinia
- **Routing**: Vue Router
- **Key Files**:
  - `src/views/DiaryPage.vue`: 일기 작성 및 조회 페이지 (메인 기능)
  - `src/views/AuthPage.vue`: 로그인 및 회원가입 페이지

### 2. Backend (`backend/`)

- **Framework**: Flask (Python)
- **Database**: MariaDB
- **ORM**: SQLAlchemy
- **Authentication**: JWT (JSON Web Token)
- **Key Files**:
  - `app.py`: 메인 애플리케이션 파일, API 라우트 정의
  - `models.py`: 데이터베이스 모델 정의 (User, Diary)
  - `config.py`: 환경 설정 파일
  - `schema.sql`: 데이터베이스 스키마 정의

## ✨ 주요 기능 (Features)

- **회원가입 및 로그인 (Authentication)**: JWT를 이용한 사용자 인증 시스템.
- **일기 작성 (Create Diary)**:
  - 감정 단계(Mood Level) 선택
  - 있었던 일(Event), 감정 상세(Emotion), 속마음(Self-talk) 등 단계별 입력
- **일기 조회 (View Diary)**: 작성한 일기를 최신순으로 조회.
- **일기 수정 (Edit Diary)**: 작성한 내용 수정 가능.

## 🚀 실행 방법 (How to Run)

### Backend

1. `backend` 폴더로 이동합니다.
2. 가상 환경을 활성화하고 의존성을 설치합니다.
3. 데이터베이스를 설정합니다 (`check_tables.py` 또는 `init_db.py` 사용).
4. 서버를 실행합니다:
   ```bash
   python app.py
   ```
   (서버는 기본적으로 `http://127.0.0.1:5001`에서 실행됩니다.)

### Frontend

1. `frontend` 폴더로 이동합니다.
2. 의존성을 설치합니다:
   ```bash
   npm install
   ```
3. 개발 서버를 실행합니다:
   ```bash
   npm run dev
   ```

## 📝 작업 내역 (Worklog)

- **UI 개선**: `DiaryPage.vue`에서 아코디언 스타일의 입력 폼 구현 및 수정 모드/읽기 모드 전환 기능 개선.
- **DB 마이그레이션**: MariaDB 구조 설정 및 `DB_STRUCTURE.md` 문서화.
- **API 개발**: Flask를 이용한 RESTful API 구현 (일기 CRUD, 인증).
