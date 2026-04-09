#!/usr/bin/env python3
"""
디하 파트너즈 채용 공고 자동 게시 파이프라인.

이 파이프라인은 Claude Code에서 실행합니다.

전체 흐름:
  1. [Figma MCP] 이미지 생성 → 사용자가 Figma에서 Export
  2. [Python] 텍스트 생성 (인스타그램 + 스레드)
  3. [Python] 검수 에이전트
  4. [Python] Instagram/Threads 게시

텍스트 생성/검수/게시 (이미지 Export 후):
    python pipeline.py \\
        --image "output/탑헬스.jpg" \\
        --company "탑헬스" \\
        --category "건강기능식품 브랜드" \\
        --position "웹 콘텐츠 디자이너" \\
        --description "건강기능식품 브랜드의 SNS 콘텐츠, 웹/프로모션 배너, 상세페이지 디자인 전반을 담당할" \\
        --hours "매일 4시간 11:00-16:00" \\
        --start "4월 14일(화)"
"""
import argparse
import json
import sys
from datetime import datetime

from src.text_generator import JobPosting, generate_texts
from src.reviewer import review_content
from src.instagram_publisher import publish_to_instagram
from src.threads_publisher import publish_to_threads


def main():
    parser = argparse.ArgumentParser(
        description="디하 파트너즈 채용 공고 자동 게시 파이프라인"
    )
    parser.add_argument("--image", required=True, help="Figma에서 Export한 이미지 경로")
    parser.add_argument("--company", required=True, help="기업명 (예: 탑헬스)")
    parser.add_argument("--category", required=True, help="기업 종류 (예: 건강기능식품 브랜드)")
    parser.add_argument("--position", required=True, help="포지션 종류 (예: 웹 콘텐츠 디자이너)")
    parser.add_argument("--description", required=True, help="업무 상세 설명")
    parser.add_argument("--hours", required=True, help="업무 시간 (예: 매일 4시간 11:00-16:00)")
    parser.add_argument("--start", default="ASAP", help="업무 시작일 (기본: ASAP)")
    parser.add_argument("--dry-run", action="store_true", help="실제 게시 없이 미리보기만")
    parser.add_argument("--skip-review", action="store_true", help="검수 건너뛰기")
    parser.add_argument("--no-threads", action="store_true", help="Threads 게시 안 함")
    parser.add_argument("--no-instagram", action="store_true", help="Instagram 게시 안 함")

    args = parser.parse_args()
    image_path = args.image

    posting = JobPosting(
        category=args.category,
        position=args.position,
        description=args.description,
        work_hours=args.hours,
        start_date=args.start,
    )

    print("=" * 60)
    print("🚀 디하 파트너즈 채용 공고 파이프라인")
    print(f"   기업: {args.company}")
    print(f"   포지션: {posting.category} / {posting.position}")
    print(f"   이미지: {image_path}")
    print("=" * 60)

    # ── Step 1: 텍스트 생성 ──
    print("\n📝 [1/3] 텍스트 생성")
    texts = generate_texts(posting)
    print(f"  ✅ 인스타그램 본문: {len(texts.instagram_caption)}자")
    print(f"  ✅ 스레드 메인: {len(texts.threads_main)}자")
    print(f"  ✅ 스레드 댓글: {len(texts.threads_reply)}자")
    print(f"  🏷️  해시태그: {' '.join(texts.hashtags)}")

    # ── Step 2: 검수 ──
    if not args.skip_review:
        print("\n🔍 [2/3] 검수 에이전트 실행")
        review = review_content(
            image_path=image_path,
            instagram_caption=texts.instagram_caption,
            threads_main=texts.threads_main,
            threads_reply=texts.threads_reply,
            category=posting.category,
            position=posting.position,
        )

        if review.issues:
            print("  ⚠️  발견된 이슈:")
            for issue in review.issues:
                print(f"     - {issue}")

        if not review.approved:
            print(f"\n  ❌ 검수 불통과: {review.feedback}")
            print("  파이프라인을 중단합니다.")
            sys.exit(1)

        print(f"  ✅ 검수 통과: {review.feedback}")
    else:
        print("\n⏭️  [2/3] 검수 건너뜀")

    # ── Dry run ──
    if args.dry_run:
        print("\n" + "=" * 60)
        print("🏁 DRY RUN 완료")
        print(f"   이미지: {image_path}")
        print("\n── 인스타그램 본문 ──")
        print(texts.instagram_caption)
        print("\n── 스레드 메인 포스트 ──")
        print(texts.threads_main)
        print("\n── 스레드 댓글 ──")
        print(texts.threads_reply)
        print("=" * 60)

        result_path = image_path.rsplit(".", 1)[0] + "_result.json"
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump({
                "company": args.company,
                "posting": {
                    "category": posting.category,
                    "position": posting.position,
                    "description": posting.description,
                    "work_hours": posting.work_hours,
                    "start_date": posting.start_date,
                },
                "texts": {
                    "instagram_caption": texts.instagram_caption,
                    "threads_main": texts.threads_main,
                    "threads_reply": texts.threads_reply,
                    "hashtags": texts.hashtags,
                },
                "image_path": image_path,
                "created_at": datetime.now().isoformat(),
            }, f, ensure_ascii=False, indent=2)
        print(f"   결과 JSON: {result_path}")
        return

    # ── Step 3: 게시 ──
    print("\n📮 [3/3] 게시")
    results = {}

    if not args.no_instagram:
        print("\n  [Instagram]")
        try:
            ig_result = publish_to_instagram(image_path, texts.instagram_caption)
            results["instagram"] = ig_result
        except Exception as e:
            print(f"  ❌ Instagram 게시 실패: {e}")
            results["instagram_error"] = str(e)

    if not args.no_threads:
        print("\n  [Threads]")
        try:
            th_result = publish_to_threads(
                main_text=texts.threads_main,
                reply_text=texts.threads_reply,
                image_path=image_path,
            )
            results["threads"] = th_result
        except Exception as e:
            print(f"  ❌ Threads 게시 실패: {e}")
            results["threads_error"] = str(e)

    print("\n" + "=" * 60)
    print("🏁 파이프라인 완료!")
    if results:
        result_path = image_path.rsplit(".", 1)[0] + "_result.json"
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"   결과: {result_path}")


if __name__ == "__main__":
    main()
