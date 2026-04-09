#!/bin/bash
set -e

echo "=== 디하 파트너즈 채용 파이프라인 초기 설정 ==="
echo ""

# Python 가상환경 생성
if [ ! -d "venv" ]; then
    echo "1. Python 가상환경 생성 중..."
    python3 -m venv venv
fi

echo "2. 가상환경 활성화..."
source venv/bin/activate

echo "3. 패키지 설치 중..."
pip install -r requirements.txt --quiet

# .env 파일 확인
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  .env 파일이 생성되었습니다. API 키를 입력해주세요:"
    echo "   - META_APP_ID / META_APP_SECRET"
    echo "   - INSTAGRAM_ACCESS_TOKEN / INSTAGRAM_BUSINESS_ACCOUNT_ID"
    echo "   - THREADS_ACCESS_TOKEN / THREADS_USER_ID"
    echo "   - ANTHROPIC_API_KEY"
    echo ""
    echo "   Meta Developer App 설정 가이드: README.md 참고"
fi

# 폰트 확인
if [ ! -f "assets/fonts/Pretendard-Bold.otf" ]; then
    echo ""
    echo "⚠️  폰트 파일이 필요합니다."
    echo "   assets/fonts/ 에 다음 파일을 넣어주세요:"
    echo "   - Pretendard-Bold.otf (variable 텍스트용)"
    echo "   - Pretendard-Medium.otf (설명 텍스트용)"
    echo ""
    echo "   다운로드: https://cactus.tistory.com/306"
fi

echo ""
echo "✅ 설정 완료! 사용법:"
echo '   source venv/bin/activate'
echo '   python pipeline.py --category "라이프스타일 브랜드" --position "브랜딩·그래픽 디자이너" --description "감도 있는 라이프스타일 브랜드의 비주얼 그래픽, 패키지 디자인 및 콘텐츠 디자인 전반을 담당할" --hours "매일 3시간 9:00-12:00" --start "ASAP"'
