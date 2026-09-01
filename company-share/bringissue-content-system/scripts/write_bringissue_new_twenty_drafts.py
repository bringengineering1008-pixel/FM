from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = Path(os.environ["BRINGISSUE_REGISTRY"])


def paragraphs(post: dict) -> list[str]:
    topic = post["topic"]
    angle = post["editorial_angle"]
    if topic == "상품리뷰":
        return [
            "첫인상만으로 결론을 내리기보다 실제 사용 장면부터 차근차근 봤습니다.",
            f"이 영상에서 가장 중요한 포인트는 {angle}입니다. 사양표보다 누구에게 필요한지, 국내에서 쓰기 전에 무엇을 확인해야 하는지가 더 현실적인 기준이 됩니다.",
            "구매를 고민한다면 가격·호환성·사후지원 세 가지를 따로 확인하는 편이 안전합니다. 영상의 반응은 참고하되 최종 판단은 공식 판매 정보와 현재 가격을 기준으로 하세요.",
        ]
    if topic in {"스포츠", "게임"}:
        return [
            "결과만 보면 놓치기 쉬운 장면이 있습니다. 화면의 흐름을 따라가면 승부가 바뀌기 전부터 작은 신호가 반복됩니다.",
            f"제가 주목한 지점은 {angle}입니다. 한 번의 화려한 장면보다 그 직전의 위치, 선택, 팀의 반응을 함께 봐야 맥락이 선명해집니다.",
            "그래서 이 영상은 단순 하이라이트보다 과정이 재미있습니다. 아래 장면 순서대로 보면 제목의 궁금증이 자연스럽게 풀립니다.",
        ]
    if topic == "음악":
        return [
            "처음에는 곡보다 화면의 분위기가 먼저 들어오지만, 두 번째부터는 목소리와 편곡의 작은 변화가 들립니다.",
            f"핵심은 {angle}입니다. 가사를 길게 옮기기보다 도입·전환·후반의 표정과 화면을 따라가며 왜 여운이 남는지 정리했습니다.",
            "이어폰으로 한 번, 화면과 함께 한 번 들어보면 같은 곡도 다르게 느껴집니다. 특히 후반부로 갈수록 초반에 쌓아둔 감정이 어떻게 회수되는지 확인해 보세요.",
        ]
    if topic == "IT":
        return [
            "알고 나면 간단하지만 막상 급할 때는 순서가 헷갈리는 기능입니다. 영상의 핵심 단계만 실제 사용 흐름에 맞춰 정리했습니다.",
            f"포인트는 {angle}입니다. 촬영 각도와 테두리 보정, 저장 형식을 확인하면 별도 스캐너 없이도 결과가 훨씬 깔끔해집니다.",
            "중요 문서는 저장 뒤 글자가 확대해도 선명한지, 페이지 순서가 맞는지 마지막으로 확인하세요. 개인정보가 있다면 공유 범위도 함께 점검하는 것이 좋습니다.",
        ]
    return [
        "처음에는 가볍게 웃고 지나갈 장면처럼 보입니다. 그런데 표정과 대화의 간격을 따라가면 사람들이 이 영상을 다시 찾는 이유가 보입니다.",
        f"이 글에서 살펴볼 핵심은 {angle}입니다. 대사를 그대로 옮기기보다 장면이 만들어진 맥락과 반응을 중심으로 정리했습니다.",
        "짧은 반전만 떼어 보면 자극적인 클립이지만, 앞뒤 흐름까지 보면 인물의 선택과 제작진의 편집이 함께 만든 재미라는 점이 선명해집니다.",
    ]


def render(post: dict) -> str:
    p1, p2, p3 = paragraphs(post)
    labels = ["첫인상", "상황이 열린 순간", "분위기가 달라진 지점", "놓치면 아쉬운 디테일", "제목의 궁금증이 풀린 순간", "마지막에 남은 여운"]
    body = [
        f"# {post['draft_title']}",
        "",
        "안녕하세요. **브링이슈**입니다. 🙂",
        "",
        p1,
        "",
        f"==오늘의 한 줄 포인트: {post['editorial_angle']}==",
        "",
        "━━━━━━━━━━━━━━",
        "",
        "## 🔍 영상에서 먼저 볼 포인트",
        "",
        p2,
        "",
    ]
    for i, label in enumerate(labels, 1):
        body += [
            f"### 📸 {i}. {label}",
            "",
            f"![영상 캡처 {i}](scene-{i:02d}.jpg)",
            "",
            f"__브링이슈 해설__  {post['editorial_angle']}이라는 관점에서 보면, 이 장면은 다음 흐름을 이해하게 만드는 중요한 단서입니다.",
            "",
        ]
    body += [
        "━━━━━━━━━━━━━━",
        "",
        "## 💡 보고 나서 정리한 결론",
        "",
        p3,
        "",
        f"==결국 이 영상의 재미는 ‘{post['thumbnail_text'][1]}’라는 질문을 장면으로 확인하는 데 있습니다.==",
        "",
        "여러분은 어느 장면이 가장 기억에 남으셨나요? 댓글로 남겨주세요. 😊",
        "",
        "※ 본문 이미지는 원본 영상을 설명·비평하기 위한 장면 캡처입니다. 채널 로고와 워터마크를 지우지 않았으며 원본을 대체할 수 있는 연속 장면·긴 클립은 사용하지 않습니다.",
        "",
        f"**원본 영상**  {post['channel']} · {post['source_title']}",
        "",
        post["url"],
        "",
        f"#브링이슈 #{post['topic'].replace('·','')} #오늘뜬유튜브 #유튜브리뷰 #화제영상",
        "",
    ]
    return "\n".join(body)


def main() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    for post in data["posts"]:
        out = ROOT / "blog-assets" / f"{post['scheduled_at'][:10]}-{post['slug']}" / "draft.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(post), encoding="utf-8")
    summary = ROOT / "blog" / "batches" / "2026-08-23-bringissue-new-twenty-posts.md"
    rows = ["# 브링이슈 신규 20편 예약 원장", "", "|순서|예약|제목|원본|", "|---:|---|---|---|"]
    for p in data["posts"]:
        rows.append(f"|{p['order']}|{p['scheduled_at'][5:16].replace('T',' ')}|{p['draft_title']}|[{p['channel']}]({p['url']})|")
    summary.write_text("\n".join(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
