# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Novel Forge Claude (NFC)** — PD(기획자)와 AI가 협업하여 웹소설을 기획하고 집필하는 인터랙티브 작성 도구. 코드 프로젝트가 아닌 **AI 주도의 창작 워크플로우**이며, 전체 스펙은 `NFC_plan.md`에 정의되어 있다.

**핵심 원칙**: CLI(`python nfc.py <cmd>`)는 상태 관리 도구일 뿐이고, 콘텐츠 생성(방향성 제안, 기획안, 전개 옵션, 원고, 퇴고 등)은 Claude Code가 직접 수행한다. 이 문서가 Claude Code의 **행동 매뉴얼**이다.

---

## 단축키 (Shortcut)

사용자는 영어 약자 한 글자로 의사결정을 입력할 수 있다. Claude Code는 이를 인식하여 적절한 CLI 명령으로 변환한다.

### 항목 선택 단계 (방향성/전개 선정)

| 단축키 | 명령 | 설명 |
|--------|------|------|
| `S <id>` | select | **[S]elect** — 항목 선정 |
| `H <id>` | hold | **[H]old** — 항목 보류 |
| `D <id>` | discard | **[D]iscard** — 항목 폐기 |
| `R` | retry | **[R]etry** — 전체 재생성 |
| `G` | regen | **[G]enerate** — 선정 유지, 나머지 재생성 (Phase 2) |
| `C` | confirm-end | **[C]onfirm** — 선정 종료 (Phase 2) |

### 결과물 검토 단계 (기획안/원고/퇴고)

| 단축키 | 명령 | 설명 |
|--------|------|------|
| `A` | approve | **[A]pprove** — 승인 |
| `M "<피드백>"` | revise | **[M]odify** — 수정 요청 |
| `D` | reject | **[D]ismiss** — 폐기 |

### 확인 단계 (전개 선정 확인)

| 단축키 | 명령 | 설명 |
|--------|------|------|
| `A` | approve | **[A]pprove** — 승인 |
| `R` | reject | **[R]eject** — 돌아가기 |

한국어 자연어 입력도 동일하게 지원한다. (예: "2번", "승인", "다시 해줘")

---

## 시작 흐름 (Startup)

사용자가 소설 관련 요청을 하면("소설 써줘", "새 소설 시작하자", "이어서 쓰자" 등) **반드시 먼저 신규/계속 여부를 확인**한다.

### 1. 신규 작성 vs 기존 프로젝트 진행 확인

사용자에게 다음을 질문한다:
- **"새 소설을 시작할까요, 아니면 기존 프로젝트를 이어서 진행할까요?"**

단, 사용자의 요청이 명확한 경우 질문을 생략할 수 있다:
- "새 소설 시작하자" → 바로 신규 작성 흐름
- "이어서 쓰자" → 바로 기존 프로젝트 흐름

### 2-A. 신규 작성

1. 사용자에게 **장르, 키워드, 분위기**를 질문한다
2. 영문 프로젝트 제목(디렉토리명)을 제안하고 확인받는다
3. 프로젝트를 생성한다:
   ```bash
   python nfc.py init "<프로젝트명>" --title <영문디렉토리명>
   ```
4. Phase 1 방향성 제안 단계로 진입한다

### 2-B. 기존 프로젝트 이어서 진행

1. 작업 디렉토리에서 기존 프로젝트 목록을 탐색한다 (Glob으로 `projects/*/state.json` 검색)
2. **프로젝트가 1개**인 경우: 해당 프로젝트를 안내하고 진행 확인
3. **프로젝트가 여러 개**인 경우: 목록을 제시하고 사용자가 선택
4. 선택된 프로젝트의 상태를 확인한다:
   ```bash
   python nfc.py status
   ```
5. 컨텍스트 파일(`context/` 폴더)이 있으면 읽어서 맥락을 파악한다
6. 해당 단계의 AI 행동 가이드에 따라 이어서 진행한다

### 2-C. 프로젝트가 없는 경우

기존 프로젝트 진행을 선택했지만 프로젝트가 없으면, 안내 후 **신규 작성 흐름(2-A)**으로 전환한다.

---

## Workflow Architecture (4-Phase 순환 구조)

- **Phase 1** (최초 1회): 장르/키워드 → 방향성 5개 제안 → PD 선정 → 기획안 빌드업 → PD 승인 → `context/` 폴더에 6개 마크다운 파일 생성
- **Phase 2**: 컨텍스트 기반 전개 옵션 5개 생성 (일반 3개 prob ≤ 0.90, 희귀 2개 prob < 0.10) → PD가 1~3개 선정
- **Phase 3**: 문체 설정 → 장면별/1화 분량 모드 선택 → 집필 (복수 전개 시 멀티 에이전트 병렬 작성)
- **Phase 4**: 퇴고 → 원고 최종 확정 → 컨텍스트 갱신 → (필요 시) 백업 & 요약 압축 → **Phase 2로 복귀**

Phase 2 → 3 → 4 → 2 사이클이 연재 종료까지 반복된다.

---

## Phase별 AI 행동 가이드

### Phase 1: 컨텍스트 수립

#### Step 1-1: 방향성 제안 (`direction_proposal`)

**AI가 할 일:**
1. 사용자가 제시한 장르/키워드/분위기를 바탕으로 **서로 다른 방향성 5개**를 생성한다
2. 각 방향성은 2~3줄 요약으로 작성한다
3. 생성한 방향성을 CLI로 등록한다:
   ```bash
   python nfc.py add "방향성 1: 요약 내용"
   python nfc.py add "방향성 2: 요약 내용"
   python nfc.py add "방향성 3: 요약 내용"
   python nfc.py add "방향성 4: 요약 내용"
   python nfc.py add "방향성 5: 요약 내용"
   ```
4. 등록 후 다음 단계로 이동한다:
   ```bash
   python nfc.py next
   ```
5. 사용자에게 5개 방향성을 보기 좋게 제시하고 선택을 요청한다:
   ```
   번호로 선택하세요.  [S]elect <번호> / [H]old <번호> / [D]iscard <번호> / [R]etry
   ```

**사용자 응답 처리:**
- `S <id>` 또는 번호: `python nfc.py select <id>` → Step 1-3(기획안 빌드업)으로 자동 이동
- `H <id>`: `python nfc.py hold <id>`
- `D <id>`: `python nfc.py discard <id>`
- `R`: `python nfc.py retry` → 추가 키워드/힌트를 요청 후 방향성 5개 재생성

#### Step 1-3: 기획안 빌드업 (`plan_buildup`)

**AI가 할 일:**
1. 선정된 방향성을 기반으로 **구체적인 기획안**을 작성한다:
   - 세계관, 주인공/주요 캐릭터, 핵심 컨셉트, 플롯 뼈대, 테마, 톤앤매너, 예상 분량
2. 기획안을 마크다운 파일로 저장한다:
   ```bash
   python nfc.py save plan "drafts/plan_v1.md"
   ```
3. 다음 단계로 이동한다:
   ```bash
   python nfc.py next
   ```
4. 사용자에게 기획안을 제시하고 의사결정을 요청한다:
   ```
   [A]pprove(승인) / [M]odify(수정) / [D]ismiss(폐기)
   ```

**사용자 응답 처리:**
- `A`: `python nfc.py approve` → Step 1-5(컨텍스트 생성)로 이동
- `M "<피드백>"`: `python nfc.py revise "<수정 피드백>"` → 피드백 반영 후 기획안 재작성
- `D`: `python nfc.py reject` → Step 1-1(방향성 제안)으로 복귀

#### Step 1-5: 컨텍스트 생성 (`context_creation`)

**AI가 할 일:**
1. 승인된 기획안을 바탕으로 프로젝트 디렉토리의 `context/` 폴더에 6개 마크다운 파일을 Write 도구로 직접 생성한다:
   - `context/character_profiles.md` — 주인공, 조연 등 캐릭터 프로필
   - `context/setting_world.md` — 시대/공간적 배경 및 고유 규칙
   - `context/concept.md` — 로그라인, 장르, 매력 포인트
   - `context/plot_outline.md` — 전체 시놉시스와 플롯 뼈대
   - `context/themes.md` — 스토리를 관통하는 테마와 메인 상징물
   - `context/tone.md` — 톤앤매너, 예상 분량 등 기타사항
2. 다음 단계로 이동한다:
   ```bash
   python nfc.py next
   ```
   → Phase 2로 전환

---

### Phase 2: 전개 선정

#### Step 2-1: 전개 옵션 생성 (`development_proposal`)

**AI가 할 일:**
1. `context/` 폴더의 6개 파일을 모두 읽어 현재 맥락을 파악한다
2. **완전히 다른 방향성**을 가진 5개 전개 옵션을 생성한다
3. 각 옵션은 `<text>` + `<probability>` 태그 포맷으로 작성한다
4. **확률 분포 규칙**을 반드시 준수한다:
   - 일반 옵션 3개: probability ≤ 0.90 (자연스러운 전개)
   - 희귀 옵션 2개: probability < 0.10 (독창적이고 기발한 전개)
5. CLI로 등록한다 (반드시 `-p` 플래그로 확률 지정):
   ```bash
   python nfc.py add "<text>전개 방향 요약</text><probability>0.75</probability>" -p 0.75
   python nfc.py add "<text>전개 방향 요약</text><probability>0.60</probability>" -p 0.60
   python nfc.py add "<text>전개 방향 요약</text><probability>0.85</probability>" -p 0.85
   python nfc.py add "<text>희귀 전개 요약</text><probability>0.05</probability>" -p 0.05
   python nfc.py add "<text>희귀 전개 요약</text><probability>0.03</probability>" -p 0.03
   ```
6. 등록 후 다음 단계로 이동한다:
   ```bash
   python nfc.py next
   ```
7. 사용자에게 5개 옵션을 확률과 함께 제시하고 선택을 요청한다:
   ```
   [S]elect <번호> (최대 3개) / [H]old <번호> / [D]iscard <번호> / [R]etry / [G]enerate(부분 재생성) / [C]onfirm(선정 종료)
   ```

**사용자 응답 처리:**
- `S <id> [<id>...]`: `python nfc.py select <id> [<id>...]` (최대 3개까지 누적 선택 가능)
- `H <id>`: `python nfc.py hold <id>`
- `D <id>`: `python nfc.py discard <id>`
- `R`: `python nfc.py retry` → 전개 옵션 5개 전체 재생성
- `G`: `python nfc.py regen` → 선정된 항목 유지, 미선정 항목 폐기 후 새 옵션 생성 (최대 3개 선정까지 반복 가능)
- `C`: `python nfc.py confirm-end` → 선정 확인 단계로 이동

#### Step 2-3: 전개 선정 확인 (`development_confirm`)

**AI가 할 일:**
1. 선정된 전개 목록을 사용자에게 보여주고 확인한다:
   ```
   전개 선정을 종료하시겠습니까?  [A]pprove(확인) / [R]eject(돌아가기)
   ```

**사용자 응답 처리:**
- `A`: `python nfc.py approve` → Phase 3로 이동
- `R`: `python nfc.py reject` → 전개 선정 단계로 복귀

---

### Phase 3: 집필

#### Step 3-1: 문체 설정 (`style_setup`)

**AI가 할 일:**
1. 사용자에게 참고할 문체를 질문한다:
   - "참고할 문체가 있으신가요? (작가명, 작품명, 문체 설명 등)"
2. 사용자 응답에 따라 설정한다:
   ```bash
   python nfc.py config style_reference "<문체 레퍼런스>"
   ```
   또는 "없음"이면 설정 없이 진행
3. 다음 단계로 이동한다:
   ```bash
   python nfc.py next
   ```

#### Step 3-2: 작성 모드 선택 (`mode_selection`)

**AI가 할 일:**
1. 사용자에게 **전개별로** 작성 모드를 선택하도록 요청한다:
   - **scene** (장면별 작성): 하나의 장면을 작성 후 PD 피드백 수렴
   - **episode** (1화 분량 작성): 한 회차 분량(5,500자 이상) 일괄 작성
2. 전개가 **1개**인 경우:
   ```bash
   python nfc.py config writing_mode_1 "scene"
   ```
3. 전개가 **복수(2~3개)**인 경우, 각 전개를 안내하고 개별적으로 설정한다:
   ```bash
   python nfc.py config writing_mode_1 "episode"
   python nfc.py config writing_mode_2 "scene"
   python nfc.py config writing_mode_3 "episode"   # 3개인 경우
   ```
4. 다음 단계로 이동한다 (모든 전개에 모드가 설정되어야 진행 가능):
   ```bash
   python nfc.py next
   ```

#### Step 3-3: 집필 (`writing`)

**AI가 할 일:**
1. 다음을 모두 참조하여 원고를 작성한다:
   - `context/` 폴더의 6개 컨텍스트 파일
   - 선정된 전개 방향 (`status`의 selected_developments)
   - 문체 레퍼런스 (설정된 경우)
   - 각 전개별 작성 모드 (`status`의 config.writing_modes)
   - 수정 피드백 (revise로 돌아온 경우)
2. 복수 전개가 선정된 경우(2~3개), Task 도구로 멀티 에이전트를 활용하여 각 전개를 **병렬로 작성**한다. 각 에이전트에 해당 전개의 작성 모드를 전달한다
3. episode 모드의 경우 **5,500자 이상** 작성한다
4. 원고를 파일로 저장한다 (복수 전개 시 각각 save):
   ```bash
   # 단일 전개
   python nfc.py save manuscript "drafts/ep_draft.md"
   # 복수 전개 (각각 저장 — save가 누적됨)
   python nfc.py save manuscript "drafts/ep_draft_1.md"
   python nfc.py save manuscript "drafts/ep_draft_2.md"
   python nfc.py save manuscript "drafts/ep_draft_3.md"   # 3개인 경우
   ```
5. 다음 단계로 이동한다:
   ```bash
   python nfc.py next
   ```
6. 사용자에게 원고를 제시하고 의사결정을 요청한다:
   ```
   [A]pprove(승인) / [M]odify(수정) / [D]ismiss(폐기)
   ```

**사용자 응답 처리:**
- `A`: `python nfc.py approve` → Phase 4(퇴고)로 이동
- `M "<피드백>"`: `python nfc.py revise "<수정 피드백>"` → 피드백 반영 후 재집필
- `D`: `python nfc.py reject` → 집필 단계로 복귀하여 재작성

---

### Phase 4: 퇴고 및 컨텍스트 갱신

#### Step 4-1: 퇴고 (`proofreading`)

**AI가 할 일:**
1. Phase 3에서 승인된 원고와 현재 컨텍스트를 참조하여 퇴고한다:
   - 문체 일관성
   - 오탈자, 문법 오류
   - 문맥 흐름, 캐릭터 행동 일관성
   - 설정 충돌 여부
2. 수정 사항이 반영된 퇴고 결과물을 저장한다 (복수 전개 시 각각 save):
   ```bash
   # 단일 전개
   python nfc.py save proofread "drafts/ep_proofread.md"
   # 복수 전개
   python nfc.py save proofread "drafts/ep_proofread_1.md"
   python nfc.py save proofread "drafts/ep_proofread_2.md"
   ```
3. 다음 단계로 이동한다:
   ```bash
   python nfc.py next
   ```
4. 사용자에게 수정 사항과 퇴고 결과물을 제시하고 의사결정을 요청한다:
   ```
   [A]pprove(승인) / [M]odify(수정) / [D]ismiss(폐기)
   ```

**사용자 응답 처리:**
- `A`: `python nfc.py approve` → 컨텍스트 갱신 단계로 이동
- `M "<피드백>"`: `python nfc.py revise "<수정 피드백>"` → 추가 퇴고
- `D`: `python nfc.py reject` → Phase 3 집필 단계로 복귀하여 재집필

#### Step 4-3: 컨텍스트 갱신 (`context_update`)

**AI가 할 일:**
1. 최종 확정된 원고에서 변경 사항을 분석한다
2. `context/` 폴더의 해당 파일들을 Edit 도구로 직접 업데이트한다:
   - 새 캐릭터 등장/관계 변화 → `character_profiles.md`
   - 새 세계관 요소/설정 변화 → `setting_world.md`
   - 플롯 진행 상황 → `plot_outline.md`
   - 테마/복선 전개 → `themes.md`
   - 톤 변화 → `tone.md`
   - 컨셉 변화 → `concept.md`
3. 갱신 완료를 표시한다:
   ```bash
   python nfc.py context-update
   ```
4. 다음 단계로 이동한다:
   ```bash
   python nfc.py next
   ```

#### Step 4-4: 컨텍스트 크기 점검 (`context_size_check`)

**AI가 할 일:**
1. `context/` 폴더의 전체 파일 크기를 평가한다
2. AI 처리에 부담되는 수준이라고 판단되면:
   - 사용자에게 컨텍스트 압축을 제안한다
   - 승인받으면 백업 후 요약본으로 교체한다:
     ```bash
     python nfc.py context-backup
     ```
   - `context/` 파일들을 요약본으로 교체한다 (Write 도구 사용)
   - 사용자에게 요약본을 확인받는다
3. 압축이 불필요하면 그대로 진행한다:
   ```bash
   python nfc.py next
   ```

#### Step 4-5: 회차 완료 (`complete`)

**AI가 할 일:**
1. 회차 완료를 사용자에게 알린다
2. 다음 회차 진행 여부를 확인한다
3. 계속 진행 시:
   ```bash
   python nfc.py next
   ```
   → 원고가 `episodes/`에 자동 저장되고 Phase 2로 복귀
   - 단일 전개: `ep001.md`
   - 복수 전개: `ep001a.md`, `ep001b.md`, `ep001c.md` (전개 순서대로 a,b,c 접미사)

---

## 창작 규칙

### 전개 옵션 포맷 (Phase 2)

각 전개 옵션은 반드시 다음 포맷을 사용한다:

```
옵션 N.
<text>방향성 요약 내용</text>
<probability>0.XX</probability>
```

### 확률 분포 규칙

| 구분 | 개수 | probability 범위 | 설명 |
|------|------|------------------|------|
| 일반 옵션 | 3개 | ≤ 0.90 | 비교적 자연스러운 전개 |
| 희귀 옵션 | 2개 | < 0.10 | 매우 독창적이고 기발한 전개 |

- 1.0에 가까울수록 뻔한 전개, 0.0에 가까울수록 독창적
- 희귀 옵션이라고 해서 맥락에 안 맞아도 되는 것은 아님. 독창적이되 스토리 맥락에 부합해야 함

### 집필 모드

| 모드 | 설명 | 분량 |
|------|------|------|
| **scene** (장면별) | 하나의 장면을 작성 후 PD 피드백 수렴 | 장면 단위 |
| **episode** (1화 분량) | 한 회차 분량 일괄 작성 | 5,500자 이상 |

- 복수 전개 시 전개별로 다른 모드를 설정할 수 있다 (`config writing_mode_N`)
- 문체는 전체 공통, 작성 모드만 전개별 개별 선택

### 문체 적용

- 문체 레퍼런스가 설정된 경우 해당 스타일을 모방하여 집필
- "없음"인 경우 AI 기본 문체로 자연스럽게 작성
- 퇴고 시 문체 일관성을 반드시 점검

---

## 컨텍스트 파일 관리

### 6개 필수 파일

| 파일 | 내용 |
|------|------|
| `character_profiles.md` | 주인공, 조연 등 캐릭터 프로필 및 관계도 |
| `setting_world.md` | 시대/공간적 배경, 세계관 규칙 |
| `concept.md` | 로그라인, 장르, 매력 포인트 |
| `plot_outline.md` | 전체 시놉시스와 플롯 뼈대, 진행 상황 |
| `themes.md` | 스토리를 관통하는 테마, 상징물, 복선 |
| `tone.md` | 톤앤매너, 예상 분량 등 기타사항 |

### 생성 시점
- Phase 1 완료 시 Write 도구로 `context/` 폴더에 6개 파일을 직접 생성

### 갱신 시점
- Phase 4 컨텍스트 갱신 단계에서 Edit 도구로 해당 파일을 직접 업데이트

### 백업/압축 절차
1. `python nfc.py context-backup` 실행 → `backup/context_v{N}/`에 백업 생성
2. `context/` 파일들을 핵심 내용만 추출한 요약본으로 교체 (Write 도구)
3. 사용자에게 요약본을 제시하고 승인받음

---

## CLI 명령 레퍼런스

엔트리포인트: `python nfc.py <command>`

| 명령어 | 단축키 | 설명 |
|--------|--------|------|
| `init <name> [--title <dir>]` | — | 새 프로젝트 생성, Phase 1 시작 |
| `status` | — | 현재 상태 (Phase/Step/가능한 명령) 표시 |
| `items` | — | 제안 항목 목록 (상태/확률 포함) |
| `add "<text>" [-p 0.XX]` | — | 제안 항목 추가 (Phase 2에서 -p 사용) |
| `select <id> [<id>...]` | `S` | 항목 선정 (Phase 1: 1개, Phase 2: 1~3개) |
| `hold <id>` | `H` | 항목 보류 |
| `discard <id>` | `D` | 항목 폐기 |
| `retry` | `R` | 전체 폐기 후 재생성 요청 |
| `regen` | `G` | 선정 유지, 나머지 재생성 (Phase 2 전용) |
| `approve` | `A` | 현재 단계 승인 |
| `revise "<feedback>"` | `M` | 수정 요청 (피드백 포함) |
| `reject` | `D` | 폐기하고 이전 단계로 복귀 |
| `confirm-end` | `C` | 전개 선정 종료 확인 (Phase 2 전용) |
| `save <type> <file>` | — | 초안 파일 저장 (plan/manuscript/proofread). 복수 save 시 누적 |
| `config <key> <value>` | — | 설정 (style_reference, writing_mode_N) |
| `context-update` | — | 컨텍스트 갱신 완료 표시 |
| `context-backup` | — | 컨텍스트 백업 + 압축 준비 |
| `next` | — | 다음 단계로 진행 |

---

## Key Rules

- **PD 중심 의사결정**: 모든 단계에서 AI는 제안만 하고, PD(사용자)가 선정/보류/폐기/수정/리트라이를 판정
- **의사결정 패턴**: 선정/보류/폐기/수정/리트라이가 모든 Phase에서 일관되게 적용됨
- **단축키 지원**: 사용자가 영어 약자(A/M/D/S/H/R/G/C) 또는 한국어 자연어로 응답하면, AI가 적절한 CLI 명령으로 변환하여 실행한다
- **컨텍스트 크기 관리**: Phase 4에서 컨텍스트가 AI 처리에 부담되는 수준이면, `backup/context_v{N}/`에 백업 후 요약본으로 교체 (PD 승인 필요)
- **전개 옵션 포Q3���b�G��!�ty>` 태그 사용, 샘플링 분포 규칙 준수 필수

## 소설 프로젝트 디렉토리 구조

```
projects/
└── {소설제목}/
    ├── state.json              # 워크플로우 상태
    ├── context/                # 활성 컨텍스트 (6개 md 파일)
    │   ├── character_profiles.md
    │   ├── setting_world.md
    │   ├── concept.md
    │   ├── plot_outline.md
    │   ├── themes.md
    │   └── tone.md
    ├── episodes/               # 완성 원고 (ep001.md, ep002a.md, ep002b.md, ...)
    ├── drafts/                 # 작업 중 초안
    └── backup/
        └── context_v{N}/       # 컨텍스트 백업
```
