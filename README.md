# 디하 파트너즈 채용 공고 자동 게시 파이프라인

디자이너 채용 공고를 인스타그램 + 스레드에 자동 게시하는 파이프라인입니다.

## 파이프라인 흐름

```
1. [Claude Code + Figma MCP] 이미지 생성 → Figma에 프레임 생성
2. [사용자] Figma 데스크톱에서 JPG Export
3. [Python] 텍스트 생성 (인스타그램 + 스레드)
4. [Python] 검수 에이전트 (Claude API)
5. [Python] Instagram/Threads 자동 게시
```

## 빠른 시작

```bash
git clone <repo-url>
cd dhp-recruit-pipeline
bash setup.sh
```

## 사용법

### Step 1: Claude Code에서 이미지 생성 요청

Claude Code에 채용 정보를 전달하면 Figma MCP로 이미지를 생성합니다.

예시:
```
탑헬스, 건강기능식품 브랜드, 웹 콘텐츠 디자이너, 매일 4시간 11:00-16:00, 4월 14일 시작
```

→ Claude Code가 Figma 템플릿을 복제하고 variable 텍스트를 변경합니다.
→ 프레임 이름은 기업명으로 설정됩니다.

### Step 2: Figma에서 Export

1. Figma 데스크톱에서 생성된 프레임 선택
2. 우측 패널 하단 Export > JPG 선택
3. Export 클릭 → `output/` 폴더에 저장

### Step 3: 텍스트 생성 + 게시

```bash
source venv/bin/activate

# 미리보기 (실제 게시 안 함)
python pipeline.py \
  --image "output/탑헬스.jpg" \
  --company "탑헬스" \
  --category "건강기능식품 브랜드" \
  --position "웹 콘텐츠 디자이너" \
  --description "건강기능식품 브랜드의 SNS 콘텐츠, 웹/프로모션 배너, 상세페이지 디자인 전반을 담당할" \
  --hours "매일 4시간 11:00-16:00" \
  --start "4월 14일(화)" \
  --dry-run

# 실제 게시
python pipeline.py \
  --image "output/탑헬스.jpg" \
  --company "탑헬스" \
  --category "건강기능식품 브랜드" \
  --position "웹 콘텐츠 디자이너" \
  --description "건강기능식품 브랜드의 SNS 콘텐츠, 웹/프로모션 배너, 상세페이지 디자인 전반을 담당할" \
  --hours "매일 4시간 11:00-16:00" \
  --start "4월 14일(화)"
```

### 옵션

| 플래그 | 설명 |
|--------|------|
| `--dry-run` | 텍스트만 생성, 게시 안 함 |
| `--skip-review` | 검수 에이전트 건너뛰기 |
| `--no-threads` | Threads 게시 안 함 |
| `--no-instagram` | Instagram 게시 안 함 |

## 사전 준비

### 1. Figma MCP 설정

Claude Code에서 Figma MCP가 연결되어 있어야 합니다.
Figma 데스크톱 앱이 실행 중이어야 합니다.

- 템플릿 파일: `byXx50MB9bSu1x6bqjWmla`
- variable 텍스트 레이어: `1:4`

### 2. Meta Developer App 설정 (Instagram/Threads 게시용)

#### Step 1: 앱 생성
1. https://developers.facebook.com/ 접속
2. "My Apps" → "Create App"
3. "Other" → "Business" 선택
4. 앱 이름 입력 (예: "DHP Recruit Pipeline")

#### Step 2: Instagram Graph API 설정
1. 앱 대시보드 → "Add Products" → "Instagram Graph API" 추가
2. Settings → Basic에서 App ID, App Secret 복사 → `.env`에 입력

#### Step 3: Access Token 발급
1. Graph API Explorer (https://developers.facebook.com/tools/explorer/)
2. 권한 추가: `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`
3. "Generate Access Token" → Long-lived Token으로 교환
4. `.env`의 `INSTAGRAM_ACCESS_TOKEN`에 입력

#### Step 4: Instagram Business Account ID 찾기
```
GET https://graph.facebook.com/v21.0/me/accounts?access_token={토큰}
→ 페이지 ID 확인 후:
GET https://graph.facebook.com/v21.0/{페이지ID}?fields=instagram_business_account&access_token={토큰}
```
→ `.env`의 `INSTAGRAM_BUSINESS_ACCOUNT_ID`에 입력

#### Step 5: Threads API 설정
1. 앱 대시보드 → "Add Products" → "Threads API" 추가
2. 권한: `threads_basic`, `threads_content_publish`
3. `.env`에 `THREADS_ACCESS_TOKEN`, `THREADS_USER_ID` 입력

### 3. 이미지 호스팅 (imgbb)

Instagram API는 이미지 URL을 요구합니다.
https://api.imgbb.com/ 에서 무료 API 키 발급 → `.env`의 `IMGBB_API_KEY`

### 4. Claude API 키 (검수 에이전트용)

https://console.anthropic.com/ 에서 발급 → `.env`의 `ANTHROPIC_API_KEY`

## 프로젝트 구조

```
dhp-recruit-pipeline/
├── pipeline.py                 # 메인 파이프라인 (텍스트 생성 + 검수 + 게시)
├── config/
│   └── templates.py            # 텍스트 템플릿
├── src/
│   ├── image_generator.py      # Figma MCP 코드 생성
│   ├── text_generator.py       # 본문 텍스트 생성
│   ├── reviewer.py             # 검수 에이전트 (Claude API)
│   ├── instagram_publisher.py  # Instagram 게시
│   └── threads_publisher.py    # Threads 게시
├── output/                     # Export된 이미지 + 결과 JSON
├── .env.example                # 환경변수 템플릿
├── requirements.txt
└── setup.sh                    # 초기 설정 스크립트
```
