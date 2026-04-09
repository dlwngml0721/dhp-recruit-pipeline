"""
Figma에서 템플릿 베이스 이미지를 export하는 유틸리티.
최초 1회만 실행하면 됩니다. (variable 텍스트 영역은 Pillow로 덮어씁니다)
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

FIGMA_FILE_KEY = "byXx50MB9bSu1x6bqjWmla"
TEMPLATE_NODE_ID = "1:2"  # template 프레임
EXPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "template_base.png")


def export_template():
    token = os.getenv("FIGMA_ACCESS_TOKEN")
    if not token:
        print("❌ FIGMA_ACCESS_TOKEN이 .env에 설정되지 않았습니다.")
        print("   Figma > Settings > Personal Access Tokens 에서 발급하세요.")
        return False

    url = f"https://api.figma.com/v1/images/{FIGMA_FILE_KEY}"
    params = {"ids": TEMPLATE_NODE_ID, "format": "png", "scale": 2}
    headers = {"X-Figma-Token": token}

    print("Figma에서 템플릿 이미지 export 중...")
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()

    image_url = resp.json()["images"].get(TEMPLATE_NODE_ID)
    if not image_url:
        print("❌ 이미지 URL을 가져오지 못했습니다.")
        return False

    img_data = requests.get(image_url).content
    with open(EXPORT_PATH, "wb") as f:
        f.write(img_data)

    print(f"✅ 템플릿 이미지 저장 완료: {EXPORT_PATH}")
    return True


if __name__ == "__main__":
    export_template()
