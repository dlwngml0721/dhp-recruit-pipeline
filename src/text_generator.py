"""
채용 공고 본문 텍스트 생성 모듈.
인스타그램 + 스레드 본문을 각각 생성합니다.
"""
import os
from dataclasses import dataclass
from typing import List
from anthropic import Anthropic
from dotenv import load_dotenv

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.templates import (
    INSTAGRAM_TEMPLATE,
    THREADS_MAIN_TEMPLATE,
    THREADS_REPLY_TEMPLATE,
    DEFAULT_HASHTAGS,
)

load_dotenv()


@dataclass
class JobPosting:
    """채용 공고 입력 데이터."""
    category: str        # 기업 종류 (예: "라이프스타일 브랜드")
    position: str        # 포지션 종류 (예: "브랜딩·그래픽 디자이너")
    description: str     # 업무 상세 (예: "감도 있는 라이프스타일 브랜드의 비주얼 그래픽...")
    work_hours: str      # 업무 시간 (예: "매일 3시간 9:00-12:00")
    start_date: str      # 업무 시작일 (예: "ASAP")


@dataclass
class GeneratedTexts:
    """생성된 텍스트 결과."""
    instagram_caption: str
    threads_main: str
    threads_reply: str
    hashtags: List[str]


def generate_hashtags(posting: JobPosting) -> List[str]:
    """Claude API를 사용해 포지션에 맞는 해시태그를 생성합니다."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY 없음. 기본 해시태그를 사용합니다.")
        return DEFAULT_HASHTAGS + [f"#{posting.position.replace(' ', '')}모집"]

    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": (
                f"다음 디자이너 채용 공고에 어울리는 인스타그램 해시태그 6개를 생성해줘.\n"
                f"기업 종류: {posting.category}\n"
                f"포지션: {posting.position}\n"
                f"업무: {posting.description}\n\n"
                f"기본 해시태그: {' '.join(DEFAULT_HASHTAGS)}\n"
                f"기본 해시태그는 반드시 포함하고, 추가로 이 포지션에 맞는 해시태그 2-3개를 더 넣어줘.\n"
                f"해시태그만 공백으로 구분해서 출력해. 다른 설명 없이."
            ),
        }],
    )
    tags = message.content[0].text.strip().split()
    return [t for t in tags if t.startswith("#")]


def _generate_apply_url() -> str:
    """오늘 날짜 기반 UTM이 포함된 지원 URL을 생성합니다."""
    from datetime import datetime
    today = datetime.now().strftime("%y%m%d")
    return (
        "https://partners.designer-hire.com/apply-urgent/"
        "?utm_source=owned&utm_medium=threads"
        "&utm_campaign=dhp_now"
        f"&utm_content={today}"
    )


def generate_texts(posting: JobPosting) -> GeneratedTexts:
    """인스타그램 + 스레드 본문 텍스트를 생성합니다."""
    hashtags = generate_hashtags(posting)
    hashtag_str = " ".join(hashtags)
    apply_url = _generate_apply_url()

    instagram_caption = INSTAGRAM_TEMPLATE.format(
        description=posting.description,
        work_hours=posting.work_hours,
        start_date=posting.start_date,
        category=posting.category,
        position=posting.position,
        hashtags=hashtag_str,
    )

    threads_main = THREADS_MAIN_TEMPLATE.format(
        description=posting.description,
        work_hours=posting.work_hours,
        start_date=posting.start_date,
    )

    threads_reply = THREADS_REPLY_TEMPLATE.format(
        category=posting.category,
        position=posting.position,
        apply_url=apply_url,
    )

    return GeneratedTexts(
        instagram_caption=instagram_caption,
        threads_main=threads_main,
        threads_reply=threads_reply,
        hashtags=hashtags,
    )
