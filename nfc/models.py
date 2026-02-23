"""데이터 모델: Phase, Step, ItemStatus 열거형 및 ProjectState."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional


class Phase(str, Enum):
    PHASE1 = "phase1"
    PHASE2 = "phase2"
    PHASE3 = "phase3"
    PHASE4 = "phase4"


class Step(str, Enum):
    # Phase 1
    DIRECTION_PROPOSAL = "direction_proposal"
    DIRECTION_DECISION = "direction_decision"
    PLAN_BUILDUP = "plan_buildup"
    PLAN_DECISION = "plan_decision"
    CONTEXT_CREATION = "context_creation"
    # Phase 2
    DEVELOPMENT_PROPOSAL = "development_proposal"
    DEVELOPMENT_DECISION = "development_decision"
    DEVELOPMENT_CONFIRM = "development_confirm"
    # Phase 3
    STYLE_SETUP = "style_setup"
    MODE_SELECTION = "mode_selection"
    WRITING = "writing"
    WRITING_DECISION = "writing_decision"
    # Phase 4
    PROOFREADING = "proofreading"
    PROOFREAD_DECISION = "proofread_decision"
    CONTEXT_UPDATE = "context_update"
    CONTEXT_SIZE_CHECK = "context_size_check"
    COMPLETE = "complete"


class ItemStatus(str, Enum):
    PROPOSED = "proposed"
    SELECTED = "selected"
    HELD = "held"
    DISCARDED = "discarded"


@dataclass
class Item:
    id: int
    text: str
    status: str = ItemStatus.PROPOSED.value
    probability: Optional[float] = None

    def to_dict(self) -> dict:
        d = {"id": self.id, "text": self.text, "status": self.status}
        d["probability"] = self.probability
        return d

    @classmethod
    def from_dict(cls, d: dict) -> Item:
        return cls(
            id=d["id"],
            text=d["text"],
            status=d.get("status", ItemStatus.PROPOSED.value),
            probability=d.get("probability"),
        )


@dataclass
class ProjectState:
    project_name: str
    novel_title: str
    phase: str = Phase.PHASE1.value
    step: str = Step.DIRECTION_PROPOSAL.value
    episode_count: int = 0
    context_version: int = 0
    items: list[Item] = field(default_factory=list)
    selected_developments: list[str] = field(default_factory=list)
    config: dict = field(default_factory=lambda: {"style_reference": None, "writing_modes": {}})
    revision_feedback: Optional[str] = None
    draft_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "novel_title": self.novel_title,
            "phase": self.phase,
            "step": self.step,
            "episode_count": self.episode_count,
            "context_version": self.context_version,
            "items": [item.to_dict() for item in self.items],
            "selected_developments": self.selected_developments,
            "config": self.config,
            "revision_feedback": self.revision_feedback,
            "draft_files": self.draft_files,
        }

    @classmethod
    def from_dict(cls, d: dict) -> ProjectState:
        items = [Item.from_dict(i) for i in d.get("items", [])]
        return cls(
            project_name=d["project_name"],
            novel_title=d["novel_title"],
            phase=d.get("phase", Phase.PHASE1.value),
            step=d.get("step", Step.DIRECTION_PROPOSAL.value),
            episode_count=d.get("episode_count", 0),
            context_version=d.get("context_version", 0),
            items=items,
            selected_developments=d.get("selected_developments", []),
            config=cls._migrate_config(d.get("config", {"style_reference": None, "writing_modes": {}})),
            revision_feedback=d.get("revision_feedback"),
            draft_files=cls._migrate_draft_files(d),
        )

    @staticmethod
    def _migrate_draft_files(d: dict) -> list[str]:
        """기존 draft_file(단일) → draft_files(리스트) 마이그레이션."""
        if "draft_files" in d:
            return d["draft_files"]
        old = d.get("draft_file")
        return [old] if old else []

    @staticmethod
    def _migrate_config(config: dict) -> dict:
        """기존 writing_mode(단일) → writing_modes(dict) 마이그레이션."""
        if "writing_mode" in config and "writing_modes" not in config:
            old = config.pop("writing_mode")
            config["writing_modes"] = {"1": old} if old else {}
        if "writing_modes" not in config:
            config["writing_modes"] = {}
        # writing_mode 키가 남아있으면 제거
        config.pop("writing_mode", None)
        return config

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, text: str) -> ProjectState:
        return cls.from_dict(json.loads(text))

    def next_item_id(self) -> int:
        if not self.items:
            return 1
        return max(item.id for item in self.items) + 1

    def get_item(self, item_id: int) -> Optional[Item]:
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def selected_count(self) -> int:
        return sum(1 for item in self.items if item.status == ItemStatus.SELECTED.value)
