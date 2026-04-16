# 디하파트너즈 채용 공고 파이프라인

디자이너 채용 공고를 인스타그램 + 스레드에 올리기 위한 **이미지/텍스트를 자동 생성**하는 Claude Code 워크플로우.

## 작동 방식

Claude Code가 `CLAUDE.md`의 규칙에 따라:
1. Figma MCP로 템플릿 복제 + `(기업종류 / 포지션)` 텍스트 교체 (이미지)
2. `output/기업명.txt`에 인스타/스레드 메인/스레드 댓글/어드민 업로드 4개 섹션 자동 작성 (텍스트)

이후 이미지 Export와 실제 게시는 사용자가 수동으로 처리합니다.

## 사전 준비

1. [Claude Code](https://claude.com/claude-code) 설치
2. Claude Code에 Figma MCP 연결 (설정 필요 시 Figma MCP 공식 문서 참고)
3. Figma 데스크톱 앱 실행 (이미지 Export용)

## 빠른 시작

```bash
git clone https://github.com/dlwngml0721/dhp-recruit-pipeline.git
cd dhp-recruit-pipeline
claude
```

Claude Code 안에서 아래 양식으로 채용 정보를 보내면 바로 실행됩니다.

```
기업명
-업무 시간 : 매일 X시간 / 시작시간~끝시간
-업무 시작일 : ASAP 또는 구체적 날짜
-특이사항
```

예시:
```
탑헬스
-업무 시간 : 매일 4시간 / 11:00~16:00
-업무 시작일 : 4월 14일(화)
-건강기능식품 브랜드
-웹 콘텐츠 디자인
```

## 출력물

- Figma: 기업명으로 새 프레임 생성 (뷰포트 자동 이동됨) → Figma 데스크톱에서 JPG Export
- 텍스트: `output/기업명.txt`에 4개 섹션 자동 저장

## 파일 구조

```
dhp-recruit-pipeline/
├── CLAUDE.md      # Claude Code가 따를 워크플로우 규칙 (핵심)
├── README.md
└── output/        # 생성된 txt 파일이 저장되는 폴더 (gitignored)
```

자세한 규칙(업무시간 표기법, 템플릿 문구, 템플릿 노드 ID 등)은 `CLAUDE.md` 참고.
