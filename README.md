# Novel Forge Claude (NFC)

PD(기획자)와 AI가 협업하여 웹소설을 기획하고 집필하는 인터랙티브 작성 도구.

Claude Code 위에서 동작하며, PD가 의사결정을 내리고 AI가 콘텐츠를 생성하는 4단계 순환 워크플로우로 소설을 완성한다.

## 시작하기

### 요구사항

- Python 3.10+
- [Claude Code](https://claude.ai/code) CLI

### 실행

```bash
# Claude Code에서 실행 (권장)
# novel_forge_claude 폴더에서 Claude Code를 열고 "소설 써줘"라고 입력

# CLI 직접 실행
python nfc.py status          # 현재 상태 확인
python nfc.py init "제목"     # 새 프로젝트 생성

# 대화형 모드
python nfc.py                 # 인자 없이 실행하면 REPL 진입
```

## 워크플로우

```
Phase 1: 컨텍스트 수립 (최초 1회)
  장르/키워드 입력 → 방향성 5개 제안 → PD 선정 → 기획안 작성 → PD 승인 → 컨텍스트 확정

  ┌─────────────────────────────────────────────────────┐
  │                                                     │
  │  Phase 2: 전개 선정                                  │
  │    전개 옵션 5개 생성 → PD가 1개 선정                 │
  │                    ↓                                │
  │  Phase 3: 집필                                       │
  │    문체 설정 → 작성 모드 선택 → 원고 작성 → PD 승인    │
  │                    ↓                                │
  │  Phase 4: 퇴고 및 컨텍스트 갱신                       │
  │    퇴고 → PD 승인 → 컨텍스트 업데이트 → Phase 2로 복귀 │
  │                                                     │
  └─────────────────────────────────────────────────────┘
```

Phase 2 → 3 → 4 → 2 사이클이 연재 종료까지 반복된다.

## 의사결정 단축키

모든 단계에서 영어 한 글자로 빠르게 응답할 수 있다.

### 항목 선택 (방향성/전개 선정)

| 단축키 | 명령 | 설명 |
|--------|------|------|
| `S <id>` | select | **[S]elect** — 항목 선정 (1개) |
| `H <id>` | hold | **[H]old** — 항목 보류 |
| `D <id>` | discard | **[D]iscard** — 항목 폐기 |
| `R` | retry | **[R]etry** — 전체 재생성 |
| `C` | confirm-end | **[C]onfirm** — 선정 종료 (Phase 2) |

### 결과물 검토 (기획안/원고/퇴고)

| 단축키 | 명령 | 설명 |
|--------|------|------|
| `A` | approve | **[A]pprove** — 승인 |
| `M "피드백"` | revise | **[M]odify** — 수정 요청 |
| `D` | reject | **[D]ismiss** — 폐기 |

한국어 자연어 입력도 지원한다. ("2번", "승인", "다시 해줘" 등)

## CLI 명령어

```
python nfc.py <command>
```

| 명령어 | 단축키 | 설명 |
|--------|--------|------|
| `init <name> [--title <dir>]` | — | 새 프로젝트 생성 |
| `status` | — | 현재 상태 표시 |
| `items` | — | 제안 항목 목록 |
| `add "<text>" [-p 0.XX]` | — | 항목 추가 |
| `select <id>` | `S` | 항목 선정 (1개만) |
| `hold <id>` | `H` | 항목 보류 |
| `discard <id>` | `D` | 항목 폐기 |
| `retry` | `R` | 전체 재생성 |
| `approve` | `A` | 승인 |
| `revise "<feedback>"` | `M` | 수정 요청 |
| `reject` | `D` | 결과물 폐기 |
| `confirm-end` | `C` | 전개 선정 종료 (Phase 2) |
| `save <type> <file>` | — | 초안 저장 (plan/manuscript/proofread) |
| `config <key> <value>` | — | 설정 변경 (style_reference, writing_mode, auto_write) |
| `context-update` | — | 컨텍스트 갱신 완료 |
| `context-backup` | — | 컨텍스트 백업 |
| `next` | — | 다음 단계 진행 |

## 프로젝트 구조

```
novel_forge_claude/
├── nfc.py                  # 엔트리포인트
├── nfc/                    # CLI 패키지
│   ├── models.py           # 데이터 모델 (Phase, Step, Item, ProjectState)
│   ├── state.py            # 상태 머신 (전이, 검증, 실행)
│   ├── fileops.py          # 파일 시스템 관리
│   ├── cli.py              # CLI 라우팅
│   ├── display.py          # 출력 포매팅
│   └── interactive.py      # 대화형 REPL
├── projects/               # 소설 프로젝트 저장소
│   └── {소설제목}/
│       ├── state.json      # 워크플로우 상태
│       ├── context/        # 활성 컨텍스트 (6개 md 파일)
│       ├── episodes/       # 완성 원고 (ep001.md, ep002.md, ...)
│       ├── drafts/         # 작업 중 초안
│       └── backup/         # 컨텍스트 백업
├── CLAUDE.md               # Claude Code 행동 매뉴얼
├── NFC_plan.md             # 전체 기획 스펙
└── README.md
```

## 핵심 개념

### PD 중심 의사결정

AI는 제안만 하고, 모든 결정은 PD(사용자)가 내린다. 선정/보류/폐기/수정/리트라이가 모든 단계에서 일관되게 적용된다.

### 컨텍스트 시스템

6개 마크다운 파일이 소설의 현재 상태를 추적한다:

| 파일 | 내용 |
|------|------|
| `character_profiles.md` | 캐릭터 프로필 및 관계도 |
| `setting_world.md` | 세계관, 배경 설정 |
| `concept.md` | 로그라인, 장르, 매력 포인트 |
| `plot_outline.md` | 플롯 뼈대, 진행 상황 |
| `themes.md` | 테마, 상징물, 복선 추적 |
| `tone.md` | 톤앤매너, 분량 설정 |

매 회차 완료 시 자동으로 갱신되며, 크기가 커지면 백업 후 요약 압축한다.

### 전개 옵션 확률 분포

Phase 2에서 생성하는 5개 전개 옵션은 확률 분포 규칙을 따른다:

- **일반 옵션 3개**: probability ≤ 0.90 (자연스러운 전개)
- **희귀 옵션 2개**: probability < 0.10 (독창적이고 기발한 전개)

이를 통해 뻔한 전개와 의외의 전개를 균형 있게 제시한다.
