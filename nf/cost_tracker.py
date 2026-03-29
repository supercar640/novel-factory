"""토큰 사용량 및 비용 추적."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class CostTracker:
    """프로젝트별 AI API 토큰 사용량과 비용을 추적.

    데이터는 project_root/cost_log.json에 저장.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.log_file = project_root / "cost_log.json"
        self._log = self._load()

    def _load(self) -> list[dict]:
        if self.log_file.exists():
            with open(self.log_file, encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self):
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(self._log, f, ensure_ascii=False, indent=2)

    def record(
        self,
        phase: str,
        provider_name: str,
        usage: dict,
        action: str = "",
    ):
        """API 호출 기록 추가."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "provider": provider_name,
            "action": action,
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
        }
        self._log.append(entry)
        self._save()

    def summary(self) -> str:
        """사용량 요약 출력."""
        if not self._log:
            return "(사용 기록 없음)"

        total_in = sum(e.get("input_tokens", 0) for e in self._log)
        total_out = sum(e.get("output_tokens", 0) for e in self._log)

        # Phase별 집계
        phase_stats: dict[str, dict] = {}
        for entry in self._log:
            phase = entry.get("phase", "unknown")
            if phase not in phase_stats:
                phase_stats[phase] = {"input": 0, "output": 0, "calls": 0}
            phase_stats[phase]["input"] += entry.get("input_tokens", 0)
            phase_stats[phase]["output"] += entry.get("output_tokens", 0)
            phase_stats[phase]["calls"] += 1

        lines = [
            f"총 호출: {len(self._log)}회",
            f"총 토큰: {total_in:,} in / {total_out:,} out",
            "",
        ]
        for phase, stats in sorted(phase_stats.items()):
            lines.append(
                f"  {phase}: {stats['calls']}회, "
                f"{stats['input']:,} in / {stats['output']:,} out"
            )

        return "\n".join(lines)

    def reset(self):
        """비용 기록 초기화."""
        self._log = []
        self._save()
