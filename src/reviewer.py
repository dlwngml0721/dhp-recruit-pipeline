"""
검수 에이전트 모듈.
Claude API를 사용해 생성된 이미지와 텍스트를 검수합니다.
"""
import os
import base64
from dataclasses import dataclass
from typing import List
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ReviewResult:
    """검수 결과."""
    approved: bool
    feedback: str
    issues: List[str]


def review_content(
    image_path: str,
    instagram_caption: str,
    threads_main: str,
    threads_reply: str,
    category: str,
    position: str,
) -> ReviewResult:
    """
    생성된 콘텐츠를 검수합니다.

    체크 항목:
    - 이미지에 variable 텍스트가 올바르게 표시되는지
    - 본문 텍스트에 필수 정보가 빠지지 않았는지
    - 지원 분야 [카테고리/포지션]이 일관되는지
    - 해시태그가 적절한지
    - 오탈자 여부
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY 없음. 검수를 건너뜁니다.")
        return ReviewResult(approved=True, feedback="API 키 없어 검수 생략", issues=[])

    client = Anthropic(api_key=api_key)

    # 이미지를 base64로 인코딩
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    review_prompt = f"""당신은 디하 파트너즈의 채용 콘텐츠 검수 에이전트입니다.
아래 생성된 콘텐츠를 검수해주세요.

## 검수 대상
- 기업 종류: {category}
- 포지션: {position}

## 인스타그램 본문:
{instagram_caption}

## 스레드 메인 포스트:
{threads_main}

## 스레드 댓글:
{threads_reply}

## 검수 체크리스트:
1. 이미지에 "({category} / {position})" 텍스트가 올바르게 표시되는지
2. 인스타그램 본문에 업무 시간, 업무 시작일, 지원 분야가 정확한지
3. 스레드 본문과 댓글에 동일 정보가 일관되게 들어있는지
4. 지원 분야 [{category} / {position}] 표기가 인스타/스레드 모두 동일한지
5. 오탈자나 문법 오류가 없는지
6. 해시태그가 포지션과 관련 있는지

## 응답 형식 (정확히 이 형식으로):
APPROVED: true 또는 false
ISSUES:
- (이슈가 있으면 한 줄씩 나열, 없으면 "없음")
FEEDBACK:
(전체적인 피드백 한 줄)"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data,
                    },
                },
                {"type": "text", "text": review_prompt},
            ],
        }],
    )

    response_text = message.content[0].text.strip()
    return _parse_review(response_text)


def _parse_review(text: str) -> ReviewResult:
    """검수 응답을 파싱합니다."""
    approved = "APPROVED: true" in text.lower() or "approved: true" in text.lower()

    issues = []
    feedback = ""
    in_issues = False
    in_feedback = False

    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("ISSUES:"):
            in_issues = True
            in_feedback = False
            continue
        if line.startswith("FEEDBACK:"):
            in_issues = False
            in_feedback = True
            continue
        if in_issues and line.startswith("- ") and line != "- 없음":
            issues.append(line[2:])
        if in_feedback and line:
            feedback = line

    return ReviewResult(approved=approved, feedback=feedback, issues=issues)
