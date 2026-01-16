# MariaDB 설치 및 구축 가이드 (Mac + DBeaver)

이 문서는 Mac(macOS) 환경에서 MariaDB를 설치하고, DBeaver를 활용하여 현재 프로젝트의 데이터베이스 구조를 구축하는 과정을 상세히 설명합니다.

---

## 1. MariaDB 설치 (Mac 기준)

Mac에서는 **Homebrew**를 사용하여 설치하는 것이 가장 간편하고 표준적인 방법입니다.

### 1단계: Terminal(터미널) 열기

`Command` + `Space`를 눌러 Spotlight 검색창을 열고 `Terminal`을 입력해 실행합니다.

### 2단계: Homebrew 확인 및 설치

만약 Homebrew가 설치되어 있지 않다면(터미널에 `brew --version` 입력 시 에러), [Homebrew 홈페이지](https://brew.sh/)의 명령어를 복사해 설치하세요.

### 3단계: MariaDB 설치 및 실행

터미널에 다음 명령어들을 한 줄씩 입력하세요.

1. **MariaDB 설치**

   ```bash
   brew install mariadb
   ```

2. **서비스 시작**
   ```bash
   brew services start mariadb
   ```

### 4단계: 비밀번호 초기화 및 설정 (필수!)

설치 직후에는 비밀번호가 설정되어 있지 않거나 시스템 권한으로만 접속되므로, **반드시 한 번은 비밀번호를 초기화(설정)해줘야 우리가 원하는 비밀번호로 로그인할 수 있습니다.**

#### 방법 A: 공식 보안 스크립트 실행 (추천)

가장 표준적인 방법입니다. 터미널에 다음을 입력하세요.

```bash
sudo mysql_secure_installation
```

1. `Enter current password for root`: (처음엔 비어있으므로 그냥 **Enter** 키)
2. `Switch to unix_socket authentication ...?`: **N** (No)
3. `Change the root password?`: **Y** (Yes) -> **여기서 초기화가 진행됩니다.**
4. `New password`: **`1q2w3e4r`** 입력 (프로젝트 설정과 동일하게)
5. `Re-enter new password`: **`1q2w3e4r`** 재입력
6. 나머지 질문들(`Remove anonymous users?`, `Disallow root login remotely?` 등): 모두 **Y** 입력

#### 방법 B: 직접 명령어로 초기화하기 (만약 위 방법이 막힐 때)

터미널에서 관리자 권한(`sudo`)으로 접속하여 SQL 명령어로 직접 비밀번호를 강제 지정하는 방법입니다.

1. **관리자 권한으로 MariaDB 접속**

   ```bash
   sudo mariadb
   ```

   (이때 입력하는 비밀번호는 맥북 로그인 비밀번호입니다.)

2. **비밀번호 변경 SQL 실행**
   프롬프트(`MariaDB [(none)]>`)가 뜨면 아래 명령어를 한 줄씩 정확히 입력하세요.
   ```sql
   ALTER USER 'root'@'localhost' IDENTIFIED BY '1q2w3e4r';
   FLUSH PRIVILEGES;
   EXIT;
   ```
   이제 `root` 계정의 비밀번호가 `1q2w3e4r`로 초기화되었습니다.

---

## 2. DBeaver 설치 및 접속

### 1단계: DBeaver 설치

1. [DBeaver 다운로드 페이지](https://dbeaver.io/download/)에서 **Mac OS X (dmg)** 버전을 다운로드하여 설치합니다.
   _또는 터미널 사용: `brew install --cask dbeaver-community`_

### 2단계: 데이터베이스 연결

1. DBeaver 실행 -> 좌측 상단 '새 연결' 아이콘.
2. **MariaDB** 선택 -> 'Next'.
3. **Connection Settings**:
   - **Server Host**: `localhost`
   - **Port**: `3306`
   - **Username**: `root`
   - **Password**: `1q2w3e4r` (위에서 초기화한 비밀번호)
4. **Test Connection** 클릭 -> 성공 시 **Finish**.

---

## 3. 데이터베이스 구축 (SQL 실행)

DBeaver SQL 편집기(`Option` + `X`로 실행)에 아래 내용을 복사해서 실행하세요.

```sql
-- 1. mood_diary 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS mood_diary
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE mood_diary;

-- 2. Users 테이블 생성
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

-- 3. Diaries 테이블 생성
CREATE TABLE IF NOT EXISTS diaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event TEXT NOT NULL,
    emotion_desc TEXT NOT NULL,
    emotion_meaning TEXT NOT NULL,
    self_talk TEXT NOT NULL,
    mood_level INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 4. 데이터 이전 (선택 사항)

데이터를 옮겨야 할 경우에만 수행하세요.

1. **가져오기 (터미널)**:
   백업 파일(`mood_diary_backup.sql`)이 있는 곳으로 이동 후:
   ```bash
   mysql -u root -p mood_diary < mood_diary_backup.sql
   ```

---

## 5. 설정 확인

```python
# backend/config.py
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1q2w3e4r@127.0.0.1:3306/mood_diary'
```
