"""Phase 1: Planning Agent — 방향성 제안, 기획안 빌드업, 컨텍스트 생성."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .base_agent import PhaseAgent
from ..providers.base import AIProvider


PROMPT_FILE = "phase1_planning.md"


class PlanningAgent(PhaseAgent):
    """Phase 1 에이전트: 기획 (방향성, 기획안, 컨텍스트 수립)."""

    def __init__(self, provider: AIProvider, prompts_dir: Optional[Path] = None, **kwargs):
        template = _load_template(prompts_dir)
        super().__init__(provider, template, **kwargs)

    def propose_directions(self, context: dict, genre_keywords: str) -> str:
        """장르/키워드 기반 방향성 5개 생성."""
        user_msg = (
            f"장르/키워드: {genre_keywords}\n\n"
            "위 키워드를 바탕으로 웹소설 방향성 5개를 제안해 주세요.\n"
            "각 방향성은 2~3줄로 요약하고, 번호를 붙여주세요."
        )
        response = self.execute(context, user_msg)
        return response.content

    def build_plan(self, context: dict, selected_direction: str) -> str:
        """선정된 방향성을 기반으로 상세 기획안 작성."""
        user_msg = (
            f"선정된 방향성:\n{selected_direction}\n\n"
            "위 방향성을 바탕으로 상세 기획안을 작성해 주세요.\n"
            "세계관, 주요 캐릭터, 핵심 갈등, 플롯 아크, 테마를 포함해 주세요."
        )
        response = self.execute(context, user_msg, max_tokens=8192)
        return response.content

    def create_context_files(self, context: dict, plan: str) -> str:
        """기획안을 기반으로 6개 컨텍스트 파일 내용 생성."""
        user_msg = (
            f"승인된 기획안:\n{plan}\n\n"
            "위 기획안을 바탕으로 다음 6개 컨텍스트 파일의 내용을 생성해 주세요:\n"
            "1. character_profiles.md — 주요 캐릭터 프로필\n"
            "2. setting_world.md — 세계관/배경 설정\n"
            "3. concept.md — 핵심 컨셉\n"
            "4. plot_outline.md — 플롯 아웃라인\n"
            "5. themes.md — 테마/주제\n"
            "6. tone.md — 톤/분위기\n\n"
            "각 파일을 `### filename.md` 헤더로 구분하여 출력해 주세요."
        )
        response = self.execute(context, user_msg, max_tokens=8192)
        return response.content

    def analyze_manuscript(self, context: dict, manuscript: str) -> str:
        """임포트된 원고 분석 → 컨텍스트 추출."""
        user_msg = (
            f"임포트된 원고:\n{manuscript[:20000]}\n\n"
            "위 원고를 분석하여 다음 6개 컨텍스트 파일의 내용을 추출해 주세요:\n"
            "1. character_profiles.md\n2. setting_world.md\n3. concept.md\n"
            "4. plot_outline.md\n5. themes.md\n6. tone.md\n\n"
            "각 파일을 `### filename.md` 헤더로 구분하여 출력해 주세요."
        )
        response = self.execute(context, user_msg, max_tokens=8192)
        return response.content


def _load_template(prompts_dir: Optional[Path] = None) -> str:
    if prompts_dir:
        path = prompts_dir / PROMPT_FILE
        if path.exists():
            return path.read_text(encoding="utf-8")
    # Fallback: built-in default
    default_path = Path(__file__).parent.parent / "prompts" / PROMPT_FILE
    if default_path.exists():
        return default_path.read_text(encoding="utf-8")
    return _DEFAULT_TEMPLATE


_DEFAULT_TEMPLATE = """\
당신은 웹소설 기획 전문 AI 어시스턴트입니다.
PD(기획자)의 결정에 따르며, 창의적인 제안을 하되 독단적 결정을 하지 않습니다.

## 역할
- 장르/키워드를 바탕으로 매력적인 방향성을 제안합니다.
- 선정된 방향성을 상세 기획안으로 확장합니다.
- 기획안을 바탕으로 작품 컨텍스트 파일을 생성합니다.

## 출력 규칙
- 한국어로 출력합니다.
- 방향성은 2~3줄로 간결하게 요약합니다.
- 기획안은 세계관, 캐릭터, 갈등, 플롯, 테마를 포함합니다.
"""
