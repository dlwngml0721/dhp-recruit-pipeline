"""
Instagram Graph API를 통한 게시 모듈.

필요 조건:
- Instagram Business 계정 + Facebook Page 연동
- Meta Developer App (Graph API 권한: instagram_basic, instagram_content_publish)
- Long-lived Access Token
"""
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


def _get_credentials():
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    if not token or not account_id:
        raise ValueError(
            "INSTAGRAM_ACCESS_TOKEN과 INSTAGRAM_BUSINESS_ACCOUNT_ID를 .env에 설정해주세요."
        )
    return token, account_id


def upload_image_to_hosting(image_path: str) -> str:
    """
    Instagram API는 이미지 URL이 필요합니다.
    이미지를 임시 호스팅에 업로드합니다.

    옵션 1: imgbb (무료, API 키 필요)
    옵션 2: 자체 서버
    옵션 3: Cloudinary 등

    여기서는 imgbb를 기본으로 사용합니다.
    IMGBB_API_KEY를 .env에 추가하거나, 다른 호스팅으로 교체하세요.
    """
    imgbb_key = os.getenv("IMGBB_API_KEY")
    if not imgbb_key:
        raise ValueError(
            "이미지 호스팅이 필요합니다. IMGBB_API_KEY를 .env에 설정하거나,\n"
            "upload_image_to_hosting()을 다른 호스팅 서비스로 교체하세요.\n"
            "imgbb 무료 API 키: https://api.imgbb.com/"
        )

    with open(image_path, "rb") as f:
        resp = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": imgbb_key},
            files={"image": f},
        )
    resp.raise_for_status()
    return resp.json()["data"]["url"]


def publish_to_instagram(image_path: str, caption: str) -> dict:
    """
    Instagram에 이미지 + 캡션을 게시합니다.

    Flow:
    1. 이미지를 호스팅에 업로드 → URL 획득
    2. Media Container 생성 (POST /{ig-user-id}/media)
    3. 게시 (POST /{ig-user-id}/media_publish)
    """
    token, account_id = _get_credentials()

    # Step 1: 이미지 호스팅
    print("  📤 이미지 업로드 중...")
    image_url = upload_image_to_hosting(image_path)

    # Step 2: Media Container 생성
    print("  📦 미디어 컨테이너 생성 중...")
    create_resp = requests.post(
        f"{GRAPH_API_BASE}/{account_id}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": token,
        },
    )
    create_resp.raise_for_status()
    creation_id = create_resp.json()["id"]

    # Step 3: 컨테이너 상태 확인 (처리에 시간 소요될 수 있음)
    print("  ⏳ 처리 대기 중...")
    for _ in range(10):
        status_resp = requests.get(
            f"{GRAPH_API_BASE}/{creation_id}",
            params={"fields": "status_code", "access_token": token},
        )
        status = status_resp.json().get("status_code")
        if status == "FINISHED":
            break
        time.sleep(2)

    # Step 4: 게시
    print("  🚀 게시 중...")
    publish_resp = requests.post(
        f"{GRAPH_API_BASE}/{account_id}/media_publish",
        data={
            "creation_id": creation_id,
            "access_token": token,
        },
    )
    publish_resp.raise_for_status()
    result = publish_resp.json()

    print(f"  ✅ Instagram 게시 완료! Media ID: {result['id']}")
    return result
