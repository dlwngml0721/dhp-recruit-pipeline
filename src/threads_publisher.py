"""
Threads API를 통한 게시 모듈.

필요 조건:
- Threads 계정 (Instagram Business 계정과 연동)
- Meta Developer App (threads_basic, threads_content_publish 권한)
- Threads Access Token
"""
import os
import time
from typing import Optional
import requests
from dotenv import load_dotenv

load_dotenv()

GRAPH_API_BASE = "https://graph.threads.net/v1.0"


def _get_credentials():
    token = os.getenv("THREADS_ACCESS_TOKEN")
    user_id = os.getenv("THREADS_USER_ID")
    if not token or not user_id:
        raise ValueError(
            "THREADS_ACCESS_TOKEN과 THREADS_USER_ID를 .env에 설정해주세요."
        )
    return token, user_id


def publish_to_threads(
    main_text: str,
    reply_text: str,
    image_path: Optional[str] = None,
    gif_url: Optional[str] = None,
) -> dict:
    """
    Threads에 메인 포스트 + 댓글을 게시합니다.

    Args:
        main_text: 메인 포스트 텍스트
        reply_text: 댓글 텍스트
        image_path: 첨부 이미지 경로 (선택)
        gif_url: GIF URL (선택)
    """
    token, user_id = _get_credentials()

    # Step 1: 메인 포스트 컨테이너 생성
    print("  📦 Threads 메인 포스트 생성 중...")
    create_data = {
        "text": main_text,
        "media_type": "TEXT",
        "access_token": token,
    }

    # 이미지가 있으면 이미지 포스트로
    if image_path:
        from src.instagram_publisher import upload_image_to_hosting
        image_url = upload_image_to_hosting(image_path)
        create_data["media_type"] = "IMAGE"
        create_data["image_url"] = image_url

    create_resp = requests.post(
        f"{GRAPH_API_BASE}/{user_id}/threads",
        data=create_data,
    )
    create_resp.raise_for_status()
    main_container_id = create_resp.json()["id"]

    # Step 2: 메인 포스트 발행
    print("  ⏳ 처리 대기 중...")
    time.sleep(3)

    publish_resp = requests.post(
        f"{GRAPH_API_BASE}/{user_id}/threads_publish",
        data={
            "creation_id": main_container_id,
            "access_token": token,
        },
    )
    publish_resp.raise_for_status()
    main_post_id = publish_resp.json()["id"]
    print(f"  ✅ Threads 메인 포스트 완료! ID: {main_post_id}")

    # Step 3: 댓글 컨테이너 생성
    print("  💬 댓글 작성 중...")
    time.sleep(2)

    reply_data = {
        "text": reply_text,
        "media_type": "TEXT",
        "reply_to_id": main_post_id,
        "access_token": token,
    }

    reply_resp = requests.post(
        f"{GRAPH_API_BASE}/{user_id}/threads",
        data=reply_data,
    )
    reply_resp.raise_for_status()
    reply_container_id = reply_resp.json()["id"]

    # Step 4: 댓글 발행
    time.sleep(2)
    reply_publish = requests.post(
        f"{GRAPH_API_BASE}/{user_id}/threads_publish",
        data={
            "creation_id": reply_container_id,
            "access_token": token,
        },
    )
    reply_publish.raise_for_status()
    reply_id = reply_publish.json()["id"]
    print(f"  ✅ Threads 댓글 완료! ID: {reply_id}")

    return {"main_post_id": main_post_id, "reply_id": reply_id}
