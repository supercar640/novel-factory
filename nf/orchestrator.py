"""Orchestrator — 상태 머신과 Phase별 에이전트를 연결하는 핵심 계층.

standalone 모드에서 NF가 직접 AI를 호출할 때 사용.
passthrough 모드에서는 이 모듈을 사용하지 않고 외부 AI(Claude Code 등)가 직접 처리.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .config import (
    load_ai_config,
    get_provider_config,
    create_provider,
    PHASE_MAP,
)
from .agents.base_agent import PhaseAgent
from .agents.planning_agent import PlanningAgent
from .agents.development_agent import DevelopmentAgent
from .agents.writing_agent import WritingAgent
from .agents.revision_agent import RevisionAgent
from .models import ProjectState


# Phase → Agent class mapping
AGENT_CLASSES = {
    "phase1": PlanningAgent,
    "phase2": DevelopmentAgent,
    "phase3": WritingAgent,
    "phase4": RevisionAgent,
}


class Orchestrator:
    """NF 오케스트레이터: 현재 Phase에 맞는 에이전트를 생성하고 실행."""

    def __init__(self, project_root: Path, prompts_dir: Optional[Path] = None):
        self.project_root = project_root
        self.prompts_dir = prompts_dir or (project_root.parent.parent / "nf" / "prompts")
        self._ai_config = load_ai_config(project_root)
        self._agents: dict[str, PhaseAgent] = {}

    def get_agent(self, phase: str) -> PhaseAgent:
        """Phase에 맞는 에이전트를 (캐시하여) 반환."""
        if phase not in self._agents:
            provider_config = get_provider_config(self._ai_config, phase)
            provider = create_provider(provider_config)

            agent_cls = AGENT_CLASSES.get(phase, PhaseAgent)
            extra_kwargs = {}
            temp = provider_config.get("temperature")
            if temp is not None:
                extra_kwargs["temperature"] = temp
            max_tok = provider_config.get("max_tokens")
            if max_tok is not None:
                extra_kwargs["max_tokens"] = max_tok

            if agent_cls != PhaseAgent:
                self._agents[phase] = agent_cls(
                    provider,
                    prompts_dir=self.prompts_dir,
                    **extra_kwargs,
                )
            else:
                from .prompts import _load_shared_template
                self._agents[phase] = PhaseAgent(
                    provider,
                    _load_shared_template(self.prompts_dir),
                    **extra_kwargs,
                )

        return self._agents[phase]

    def load_context(self, state: ProjectState) -> dict:
        """프로젝트의 컨텍스트를 읽어서 dict로 반환."""
        return PhaseAgent.load_context(self.project_root, state)

    def validate_providers(self) -> list[str]:
        """모든 Phase의 프로바이더 설정을 검증. 에러 목록 반환."""
        errors = []
        for phase_key in ("phase1", "phase2", "phase3", "phase4"):
            try:
                pc = get_provider_config(self._ai_config, phase_key)
                provider = create_provider(pc)
                err = provider.validate()
                if err:
                    label = PHASE_MAP.get(phase_key, phase_key)
                    errors.append(f"{label}: {err}")
            except Exception as e:
                errors.append(f"{phase_key}: {str(e)}")
        return errors

    @property
    def ai_config(self) -> dict:
        return self._ai_config

    def reload_config(self):
        """ai_config.json을 다시 읽고 에이전트 캐시를 초기화."""
        self._ai_config = load_ai_config(self.project_root)
        self._agents.clear()
