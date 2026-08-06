# agent-director-protocol (ADP)

*[English](README.md)*

**자기 숙제를 자기가 채점한 에이전트의 "완료했습니다!"를 그대로 믿지 마세요.**

ADP는 코딩 에이전트 하나를 **디렉터(director)**로 만들어, 계획하고 위임한 다음
실제 diff와 실제 테스트 출력으로 *검증*하게 합니다 — 그 전까지는 아무것도
완료로 치지 않습니다. 구현은 문서화된 검증 가능한 계약을 받은
**구현자(implementer)** 서브에이전트가 담당합니다. 막힌 implementer는 세 번째
추측 대신 증거를 들고 에스컬레이션하고, 더 강한 모델로의 승격은 범위가 제한되며
반드시 사전 고지됩니다. 그리고 사용자 몰래 서브에이전트를 우르르 만들지
않습니다.

이건 프레임워크가 아니라 프로토콜입니다 — Markdown 규칙, JSON Schema, 그리고
**Claude Code**와 **OpenAI Codex**용 얇은 어댑터. 런타임도, 프로젝트에 설치할
의존성도 없습니다.

## 설치

**Claude Code** — 아무 세션에서나 두 줄이면 끝이고, 이후로는 알아서
업데이트됩니다:

```
/plugin marketplace add produckyou-design/agent-director-protocol
/plugin install agent-director@agent-director-protocol
```

그다음 작은 작업 하나를 시켜보세요: *"직접 코딩하지 말고 위임해서 처리해."*
파일을 건드리기 전에 작업 계약(task contract)이 먼저 나와야 정상입니다.

**OpenAI Codex** — `core/`, `schemas/`, `codex/`를 대상 저장소에 복사하고
`AGENTS.md`에서 스킬을 참조하세요. [`codex/INSTALL.md`](codex/INSTALL.md) 참고.

전체 옵션(사용자 전역 vs 프로젝트 단위, 플러그인 없이 수동 복사, 모델 프로필,
업데이트, 제거)은 [`claude/INSTALL.md`](claude/INSTALL.md)와 아래
[빠른 설치](#빠른-설치--claude-code) 절에 있습니다.

## 이걸 쓰면 뭐가 좋은가

퍼센트 수치는 없습니다. 대신 이 프로토콜이 잡으려고 만들어진 구체적인 실패
양상과, 각각을 막는 규칙입니다. 아래 상황을 겪어본 적이 없다면 이 저장소는
필요 없을 겁니다.

| 아마 겪어봤을 실패 양상 | 무엇이 막는가 |
|---|---|
| "완료했습니다!" — 그런데 실제 호출 경로에 연결이 안 됐거나 테스트가 아예 안 돌았음 | 실제 diff와 실제 테스트 출력으로 채점하는 10개 필수 [검수 게이트](core/REVIEW-GATES.md). implementer의 `status` 필드는 검토를 *시작*시킬 뿐, 끝내지 못함 |
| 스텁, 하드코딩된 반환값, 지어낸 테스트 출력이 동작하는 기능인 척 보고됨 | `placeholder_implementation` / `fake_success`가 주관적 판단이 아니라 이름이 붙은 객관적 [실패 사유](core/FAILURE-LOOP.md)로 정의됨 |
| 같은 잘못된 수정을 반복하며 턴을 태움 | 동일 근본 원인에 대한 세 번째 추측성 수정은 금지. 대신 [증거 기반 에스컬레이션](core/ESCALATION-PROTOCOL.md)을 해야 함 |
| 에스컬레이션 = "그냥 제일 큰 모델 박기" | [구조 에이전트](core/RESCUE-PROTOCOL.md)는 작업 하나, 최대 2회, 한 번에 축 하나만 — **추론 수준을 먼저 올리고, 그래도 실패할 때만 더 강한 모델** — 그리고 진짜 추론/능력 격차일 때만. 모순된 스펙은 재계획으로 라우팅 |
| 모델이 조용히 자기를 승격시키거나, 승인한 적 없는 서브에이전트를 우르르 생성 | 모든 승격과 배치는 실행 *전에* 고지되고 서브에이전트마다 `justification` 필수. `max_batch_agents` 초과 시 승인 요청이 되며, implementer는 아예 서브에이전트를 못 만듦 |
| 병렬 에이전트 둘이 같은 파일을 덮어씀 | 배정 전 8개 도메인 [충돌 검사](core/CONCURRENCY-RULES.md). 파일 하나만 공유해도 무조건 순차 실행 |
| 실패한 시도가 `git checkout .`으로 날아가면서 증거까지 같이 사라짐 | [상태 안전성](core/STATE-SAFETY.md): 실패한 작업은 검토 전까지 보존되고, 체크포인트는 실제 커밋 SHA |
| 모호한 지시("UI 고쳐줘")를 넘겼더니 엉뚱한 게 돌아옴 | 위임 전에 `current_state`, `target_behavior`, 객관적 `completion_criteria`를 갖춘 [작업 계약](core/TASK-CONTRACT.md)이 필수 |

측정치가 아니라 기대 효과로서의 부수적 효과 두 가지: 비싼 모델이 기계적인
편집 대신 설계와 검수에 턴을 쓰게 되고, 모든 결정이 문서로 남습니다(작업
계약, 검수 결과, 실패 루프 기록, 인수인계 기록) — 무엇이 바뀌었는지뿐 아니라
*왜* 그렇게 했는지를 나중에 추적할 수 있습니다.

**안 쓰는 게 나을 때:** 파일 하나짜리 스크립트, 버리는 프로토타입, 또는
검수 결과를 읽느니 diff를 직접 보는 게 빠른 작업. 이 프로토콜은 실제로
오버헤드(계약서, 고지, 증거)를 추가하며, 그 오버헤드는 조용한 실패의 대가가
그 절차 비용보다 큰 규모나 위험도의 작업에서만 본전을 뽑습니다.

## 해결하려는 문제

단일 최상위 모델이 혼자 작업하면 모든 것을 스스로 하려는 경향이 있습니다.
코드를 읽고, 변경 사항을 설계하고, 작성하고, 테스트하고, 자기 숙제를 스스로
채점하는 과정을 한 번의 끊김 없는 흐름으로 처리합니다. 이는 가장 유능하고(그리고
가장 비용이 큰) 모델의 주의력을 기계적인 편집에 소모시키고, "코드를 작성했다"와
"작업이 끝났다" 사이를 가로막는 독립적인 검증 단계를 제거합니다. 스스로 구현하고
스스로 검토하는 모델에게는 자신의 실수를 찾아내도록 강제하는 적대적 압력이
존재하지 않습니다. 그리고 정말로 막혔을 때, "다시 시도해봐"와 "그냥 모든 걸 더
큰 모델로 돌려"는 둘 다 나쁜 기본값입니다 — 하나는 같은 실수를 반복하며 턴을
낭비하고, 다른 하나는 애초에 필요 없던 작업에까지 예산을 낭비합니다.

이 저장소는 품질이나 비용이 몇 퍼센트 향상된다는 식의 검증 불가능한 주장을 하지
않습니다. 대신 하나의 메커니즘을 설명합니다. 작업을 **계획, 위임, 검토**하는
역할과 **구현**하는 역할로 나누고, 위임되는 모든 작업 단위를 문서화되고 검증
가능한 계약을 통과하도록 강제하며, 검토 역할이 자기보고된 "완료"를 신뢰하는 대신
실제 diff와 실제 테스트 출력 같은 증거를 검증하도록 요구하고, 막힌 implementer가
세 번째로 추측성 시도를 하는 대신 구조화되고 투명하게 공개되는 방식으로 더 큰
힘을 요청할 수 있게 합니다. 결과는 벤치마크 주장이 아니라 하나의 작업 흐름입니다.
문서를 읽고, 이 메커니즘이 여러분의 프로젝트에 맞는지 판단하고, 결과는 직접
평가하시기 바랍니다.


## 역할

| 역할 | 제품 코드 작성 | 테스트 작성 | 완료 선언 |
|---|---|---|---|
| director | 기록된 인수인계(takeover) 하에서만 | 아니오 | 예 |
| implementer | 예, 계약 범위 내에서 | 예 | 아니오 (상태만 자가 보고) |
| reviewer | 아니오 | 아니오 | 아니오 (director에게 조언) |

**구조 에이전트(Rescue Agent)**는 네 번째 역할이 아닙니다 — 이미 실패한 하나의
작업에 대해, 더 강한 모델이나 더 높은 추론 노력으로 채워지는 implementer 역할이며,
더 좁은 범위와 엄격한 시도 횟수 제한 아래 놓입니다. 다른 implementer 산출물과
완전히 동일하게 검토됩니다. reviewer는 반드시 별도의 참여자가 아니라 하나의
역할이며, 기본적으로 director가 수행합니다. 전체 정의, 경계, "director는 제품
코드를 작성하지 않는다"는 규칙은 [`core/ROLE-CONTRACT.md`](core/ROLE-CONTRACT.md)에
있습니다.

## 동작 방식

```
 analyze repo ──▶ interpret requirement ──▶ design ──▶ decompose into tasks
      │                                                       │
      │  core/DELEGATION-PROTOCOL.md                          ▼
      │  ▲ disclose agent composition                write a task contract per task
      │  │ before spawning anything                  core/TASK-CONTRACT.md
      │                                                       │
      │                                                       ▼
      │                                    order by dependency / conflict check
      │                                    core/CONCURRENCY-RULES.md
      │                                                       │
      │                                                       ▼
      │                                       delegate ──▶ implement + test
      │                                                (implementer role)
      │                                                       │
      │              stuck? (2 failed attempts,                ▼
      │               same root cause) ◀────────  director review (10 gates)
      │                    │                       core/REVIEW-GATES.md
      │                    ▼                                  │
      │        escalation request                ┌────────────┴────────────┐
      │        core/ESCALATION-PROTOCOL.md        ▼                         ▼
      │                    │                 approved             revision_required
      │                    ▼                      │                         │
      │        director classifies cause          ▼                         ▼
      │        core/RESCUE-PROTOCOL.md    completion standard   evidence-based revision
      │             │             │       core/COMPLETION-STANDARD.md   instruction, loop again
      │   reasoning/model    other cause          ▲                core/FAILURE-LOOP.md
      │      gap only        (spec/env/                                    │
      │             │         rollback)                                    │
      │             ▼             │                                        │
      │   Rescue Agent            │                                        │
      │   (1-shot, ≤2 tries)      │                                        │
      │       │       │           │                                        │
      │  succeeds   fails ────────┤                                        │
      │       │       │           │                                        │
      │       └──▶ review ◀───────┘                                        │
      │            + integrate         director picks ONE:                 │
      │                            direct intervention (takeover, last resort)
      │                            roll back / escalate to user /
      │                            reduce scope / convert to investigation
      │                            core/TAKEOVER-PROTOCOL.md
      ▼
 integration + regression pass across all tasks (core/COMPLETION-STANDARD.md)
```

위 다이어그램의 각 단계는 해당 단계를 정의하는 core 문서로 연결됩니다.
요약하자면 다음과 같습니다. 어떤 작업도 모호하게 위임되지 않고, 어떤 결과물도
자기보고만으로 수락되지 않으며, 막힌 implementer는 세 번째 추측을 하는 대신 더
큰 힘을 요청하고, 진짜 추론/모델 능력 격차만이 범위가 제한된 구조 에이전트
승격을 정당화하며, director의 직접 코딩은 그 승격이 실패했거나 애초에 해당되지
않을 때만 도달하는 최후의 수단이고, "완료"는 증거에 근거한 director의 판단이지
implementer의 `status` 필드가 결코 아닙니다.

## 에스컬레이션 → 구조 에이전트(Rescue Agent) → 인수인계(takeover)

혼자 작업하는 에이전트라면 이렇게 하지 않을 법한, 이 프로토콜에서 가장 특징적인
부분입니다. **동일한 문제에 대한 세 번째 추측성 수정은 금지됩니다.**

1. **동일한 근본 원인에 대해 활성 프로필의 `implementer.failure_threshold`
   (기본값 2)만큼 실패한 시도**(서로 다른 diff, 서로 다른 결과, 동일한 근본
   원인 — 단순 재프롬프트가 아님)는 추가 시도가 아니라 에스컬레이션 요청을
   촉발합니다. implementer는 멈추고
   `EFFORT_ESCALATION_REQUEST` / `MODEL_ESCALATION_REQUEST`를 제출하며,
   director 자신이 막혔을 때는 사용자에게 직접 `DIRECTOR_ESCALATION_REQUEST`를
   제출할 수 있습니다. 어느 역할도 스스로 자신의 모델이나 노력 수준을 바꾸지
   않습니다 — 요청자의 증거(실제 diff, 실제 테스트 출력)가 독립적으로 확인된
   뒤에만 승인됩니다. [`core/ESCALATION-PROTOCOL.md`](core/ESCALATION-PROTOCOL.md)
   참고.
2. **director가 실패 원인을 분류합니다.** `diagnosis_gap`, `reasoning_gap`,
   `model_capability_gap`, `requirement_conflict`, `environment_issue`,
   `rollback_needed` 중 정확히 하나로 분류합니다. `reasoning_gap`과
   `model_capability_gap`만이 더 큰 모델 힘을 정당화합니다 — 더 강한 모델은
   모순된 작업 계약이나 고장난 CI를 고치지 못합니다.
3. **진짜 추론/능력 격차 → 구조 에이전트(Rescue Agent)**: 이 작업 하나에만
   범위가 한정되고, 최대 두 번의 시도로 제한되며(implementer 자체의 루프
   횟수와는 별도로 계산), **한 번에 축 하나만, 그리고 노력 수준을 먼저**
   올립니다 — 1차 시도는 모델을 그대로 두고 추론 수준만 올리고(더 저렴하고,
   대개 그것만으로 충분합니다), 2차 시도에서 더 강한 모델을 추가합니다.
   모델을 먼저 올리는 건 implementer가 이미 가용한 최고 노력 수준에 도달해
   있던 경우로 한정됩니다. 격리된 마지막 통과 상태에서 시작하며, 명시적인 `forbidden_scope`가
   있고, 프로젝트를 재설계하지 않습니다. 반면 `requirement_conflict`는 구조
   에이전트 대상이 아닙니다 — director가 작업 계약 자체를 수정해서
   재위임합니다(더 나은 정보로 다시 하는 평범한 계획 작업). 모든 승격은
   시작되기 *전에* 사용자에게 고지됩니다 — 이전 시도, 사유, 배정된 모델/노력
   수준을 포함하며, 사전 승인 범위를 벗어나거나 추가 비용이 발생하면 명시적인
   승인 요청이 되고 — 종료 시에는 성공이든 실패든 그에 맞는 통지가 옵니다.
   조용히 처리되는 것은 없습니다. [`core/RESCUE-PROTOCOL.md`](core/RESCUE-PROTOCOL.md) 참고.
4. **구조 에이전트마저 실패했거나, 수정된 작업 계약마저 실패했거나, 애초에
   둘 중 어디로도 연결되지 않았을 때** director가 다음 중 하나를 선택합니다:
   직접 개입(인수인계 — 여전히 기록으로 게이팅되며, 여전히 최후의 수단이지
   자동으로 이어지는 다음 단계가 아님), 롤백, 사용자에게 에스컬레이션, 범위
   축소, 또는 읽기 전용 조사 작업으로 전환. [`core/TAKEOVER-PROTOCOL.md`](core/TAKEOVER-PROTOCOL.md) 참고.

세 가지 스키마가 고지 요건을 희망 사항이 아니라 검증 가능한 것으로 만듭니다.
[`agent-composition-disclosure.schema.json`](schemas/agent-composition-disclosure.schema.json)
(스폰 전에 명시되는, 누가 실행되려는지),
[`promotion-notice.schema.json`](schemas/promotion-notice.schema.json)
(이 작업이 왜 승격되는지, 필요할 때의 승인 게이트),
[`rescue-outcome-notice.schema.json`](schemas/rescue-outcome-notice.schema.json)
(무슨 일이 일어났는지, 그리고 팀이 원래 등급으로 복귀했는지)입니다.

## 저장소 구조

```
agent-director-protocol/
├─ README.md  README.ko.md  LICENSE  CHANGELOG.md
├─ CONTRIBUTING.md  SECURITY.md  CODE_OF_CONDUCT.md  .gitignore
├─ core/                         platform-neutral protocol (11 docs)
│  ├─ ROLE-CONTRACT.md           DELEGATION-PROTOCOL.md
│  ├─ TASK-CONTRACT.md           FAILURE-LOOP.md
│  ├─ REVIEW-GATES.md            CONCURRENCY-RULES.md
│  ├─ ESCALATION-PROTOCOL.md     RESCUE-PROTOCOL.md
│  ├─ TAKEOVER-PROTOCOL.md       STATE-SAFETY.md
│  ├─ COMPLETION-STANDARD.md
├─ claude/                       Claude Code adapter
│  ├─ skills/agent-director/SKILL.md + references/*.md (7 templates)
│  ├─ CLAUDE.md.example          profiles/default.yaml
│  └─ INSTALL.md
├─ codex/                        OpenAI Codex adapter
│  ├─ skills/agent-director/SKILL.md + references/*.md (7 templates)
│  ├─ AGENTS.md.example          profiles/sol-director.yaml
│  └─ INSTALL.md
├─ schemas/                      11 JSON Schema (draft-07) documents
├─ examples/                     4 worked, schema-valid scenarios
│  ├─ python-project/  web-project/  existing-codebase/  new-project/
├─ scripts/                      validation scripts (check_repository.py, ...)
├─ tests/                        unittest suite
└─ .github/workflows/            CI: runs the validation scripts
```

## 빠른 설치 — Claude Code

**권장 — 플러그인으로 설치.** 스스로 업데이트되는 유일한 설치 방식입니다.
Claude Code가 백그라운드에서 마켓플레이스를 갱신하며,
`/plugin update agent-director@agent-director-protocol`로 즉시 최신 릴리스를
받을 수도 있습니다(반드시 전체 이름으로 — 짧은 이름은 인식되지 않습니다).

```
/plugin marketplace add produckyou-design/agent-director-protocol
/plugin install agent-director@agent-director-protocol
```

플러그인에는 스킬과 함께 `core/`, `schemas/`가 포함되어 있어 따로 복사할 것이
없습니다. 자세한 내용, 셸 명령어 버전, 제거 방법은
[`claude/INSTALL.md`](claude/INSTALL.md)를 참고하세요.

**또는 파일을 직접 복사** — 특정 프로젝트에 벤더링하는 방식이며, 업데이트
경로가 없습니다(릴리스마다 다시 복사해야 함). 스킬을 프로젝트(또는 사용자
전역 스킬 디렉터리)에 복사한 다음,
[`claude/CLAUDE.md.example`](claude/CLAUDE.md.example)의 director-mode 스니펫을
여러분의 `CLAUDE.md`에 병합하세요. 아래 명령어는
[`claude/INSTALL.md`](claude/INSTALL.md)에서 그대로 가져온 것입니다.

```bash
# Project install (macOS/Linux)
mkdir -p <project>/.claude/skills
cp -r claude/skills/agent-director <project>/.claude/skills/agent-director
cp -r core <project>/core
cp -r schemas <project>/schemas
```

```powershell
# Project install (Windows PowerShell)
New-Item -ItemType Directory -Force -Path "<project>\.claude\skills" | Out-Null
Copy-Item -Recurse "claude\skills\agent-director" "<project>\.claude\skills\agent-director"
Copy-Item -Recurse "core" "<project>\core"
Copy-Item -Recurse "schemas" "<project>\schemas"
```

사용자 전역 설치(모든 프로젝트에서 사용 가능)를 원한다면 대신
`~/.claude/skills/agent-director`로 복사하세요. 전체 단계, 설치 확인, 프로필
선택, 제거 방법은 [`claude/INSTALL.md`](claude/INSTALL.md)를 참고하세요.

## 빠른 설치 — Codex

`core/`, `schemas/`, `codex/`를 대상 저장소에 복사한 다음,
[`codex/AGENTS.md.example`](codex/AGENTS.md.example)의 director-mode 섹션을
해당 저장소의 `AGENTS.md`에 추가하세요. 아래 명령어는
[`codex/INSTALL.md`](codex/INSTALL.md)에서 그대로 가져온 것입니다.

```bash
cp -r agent-director-protocol/core target-repo/core
cp -r agent-director-protocol/schemas target-repo/schemas
cp -r agent-director-protocol/codex target-repo/codex
```

```powershell
Copy-Item -Recurse agent-director-protocol\core target-repo\core
Copy-Item -Recurse agent-director-protocol\schemas target-repo\schemas
Copy-Item -Recurse agent-director-protocol\codex target-repo\codex
```

Codex에는 "director/implementer"라는 개념이 네이티브로 존재하지 않습니다. 이
어댑터는 프로토콜을 `AGENTS.md`, `codex exec` 워커 실행, 그리고 이름이 지정된
프로필 위에 매핑합니다. 전체 단계(선택적인 네이티브 `.agents/skills` 검색 경로와
프로필-`config.toml` 매핑 포함)는 [`codex/INSTALL.md`](codex/INSTALL.md)에
있습니다.

## 3분 만에 시작하기

1. 여러분의 플랫폼에 맞게 스킬을 설치합니다(위 참조).
2. 작은 기능 브랜치에서 에이전트에게 **"이 기능에 대해 director로 동작해줘"**라고
   요청합니다. 한 줄짜리 수정이 아니라, 움직이는 부분이 2개 이상인 작업을
   고르세요.
3. "동작 방식"에서 설명한 순서를 확인하세요. director는 먼저 에이전트 구성(모델,
   노력 수준, 이번 세션에서 구조 에이전트 사용 가능 여부)을 고지한 뒤, 관련
   코드를 읽고, (파일 편집을 바로 시작하지 않고) **작업 계약(task contract)**을
   작성한 뒤, 그 계약을 서브에이전트에게 위임하고, 실제 테스트 출력이 담긴
   **구현 보고서(implementation report)**를 요구하고, 증거와 함께 열 가지 검사
   항목을 채점한 **검토 결과(review result)**를 작성하고, 마지막으로 실제로
   검증한 내용을 인용하는 짧은 **완료 보고서**를 내야 합니다.
4. 만약 director가 작업 계약도 없이, 인수인계(takeover) 기록도 없이 제품
   코드를 직접 편집하는 모습이 보이거나 — 아무 고지 없이 서브에이전트를 더 강한
   모델로 조용히 승격시킨다면, 프로토콜이 지켜지지 않고 있는 것입니다. 아래
   "잘못된 사용" 절을 참고하세요.

## 설정 및 모델 프로필

각 플랫폼은 **기본 프로필 하나**만 제공합니다(`claude/profiles/default.yaml`,
`codex/profiles/sol-director.yaml`) — Claude Code나 Codex가 강제하는
메커니즘이 아니라 **스킬 자체의 지침이 읽는 관례**입니다. 자동으로
적용되며, 따로 선택할 게 없습니다.

**이 프로필이 누가 director인지 결정하지 않습니다.** director는 항상 지금
이 세션을 실행 중인 모델입니다 — 프로젝트 도중 `/model`로 모델을 바꾸면
director도 그 즉시 같이 바뀌고, 별도로 고칠 파일이 없습니다. 프로필이 실제로
담고 있는 건 오늘 누가 director 자리에 있든 그대로 유지돼야 하는 운영
정책입니다: 스폰되는 implementer가 작업 종류별로 받는 모델/노력 수준,
서브에이전트 배치가 사용자 승인 없이 도달할 수 있는 최대 크기
(`max_batch_agents`), 그리고 한 작업에서 몇 번 실패해야 구조 프로토콜
분류가 시작되는지(`failure_threshold`)입니다:

```yaml
# Model names are environment aliases the user may freely change; the protocol never depends on a specific model name.
director:
  preferred_models: [opus-5, fable-5]  # 이 역할에 권장되는 등급일 뿐, 반드시 골라야 하는 선택지가 아님
  effort: high        # optional hint; adapters map to platform mechanism or omit
  max_batch_agents: 4  # 이 크기를 넘는 배치는 스폰 전에 사용자 승인 필요
implementer:
  preferred_models: [opus-5, sonnet-5]  # 토큰당이 아니라 완료된 작업당 비용으로 선택
  effort_by_task_kind:
    investigation: high   # root-cause hunts, competing hypotheses, design judgement
    audit: high            # pre-release compliance / security review
    implementation: medium
    pipeline: medium       # release/deploy execution — procedure fidelity, not creativity
    mechanical: low        # version bumps, doc sync, single-line edits
  effort_default: medium
  failure_threshold: 2   # 구조 프로토콜 분류 전까지 허용되는 실패 루프 횟수
reviewer:
  inherit: director   # default: reviewer == director
```

모델 이름은 환경 별칭(alias)이므로 여러분의 플랫폼이 실제로 어떤 모델로
해석하든 자유롭게 바꿔도 됩니다. `core/`는 어떤 모델 이름도 언급하지 않으며,
오직 `*/profiles/*.yaml`만 언급합니다.

**implementer 등급 선택: 토큰당이 아니라 완료된 작업당 비용으로 판단하세요.**
토큰 단가가 낮은 모델이라도 같은 일을 끝내는 데 더 많은 단계, 더 많은 재시도,
더 많은 감독이 필요하다면 총비용은 오히려 더 클 수 있습니다 — 게다가 도입
할인가가 끝나면 토큰 단가 격차 자체도 표면적인 수치보다 좁아지는 경우가
많습니다. 추론 노력 수준도 같은 논리가 반대 방향으로 작동합니다. 앞단에 더
쓰는 것이 턴 수를 줄여 총비용을 *낮추는* 경우가 있고, 반대로 능력 있는 모델을
적당한 노력 수준으로 쓰는 지점이 효율적인 경우도 많습니다. 이전 모델에서
가져온 effort 기본값은 그대로 옮겨지는 일이 드뭅니다. 이 저장소는 벤치마크
수치를 제시하지 않습니다 — 정답은 워크로드와 (변동하는) 가격에 따라 달라지므로,
여러분의 실제 작업으로 등급과 노력 수준을 직접 비교하되 *완료까지의 비용*으로
비교하세요.

**프로젝트가 다른 정책을 원할 때만 프로필을 오버라이드하세요** — 예를 들어 더 엄격한 프로젝트는
`max_batch_agents`를 낮추고, implementer 실행 비용이 저렴한 프로젝트는
`failure_threshold`를 올립니다(Codex 기본값이 이미 그렇게 돼있습니다 —
`codex/profiles/sol-director.yaml` 참고). 오버라이드하려면: 파일을 복사해서
직접 편집하거나, (Claude Code) `CLAUDE.md`에서 다른 이름의 프로필 파일을
가리키게 하거나, (Codex) 필드를 각 플랫폼의 `INSTALL.md`에서 설명하는 대로
여러분의 `config.toml` / 이름 있는 프로필로 번역하면 됩니다.

## 새 프로젝트에 적용하기

아무것도 없는 상태에서 시작하더라도 director의 첫 번째 임무는 여전히 분해에
앞선 분석과 설계입니다. 읽어야 할 기존 코드베이스는 없지만, 여전히 해석해야 할
요구사항과, 식별하고 순서를 정해야 할(그중 어떤 것이 병렬 실행에 안전한지
포함하여) 작업 집합이 존재합니다. 전체 시연은
[`examples/new-project/`](examples/new-project/)를, 단일 작업으로 이루어진
그린필드 빌드는 [`examples/python-project/`](examples/python-project/)를
참고하세요.

## 기존 프로젝트에 적용하기

위임 절차는 저장소 분석에서 시작합니다. 해결책에 대한 의견을 형성하기 전에
실제 코드, 코드의 관례, 테스트를 먼저 읽습니다. 버그 수정과 추가 기능 모두
동일한 "작업 계약 → 구현 → 검토" 주기를 거치며, 차이는 `must_read_files`,
`interfaces_to_preserve`, `preservation_conditions`가 보통 실질적인 무게를
갖는다는 점입니다(그린필드에서는 비어 있는 것과 대조적으로). 리비전 루프가 한
번 있는 추가 기능 예시는 [`examples/web-project/`](examples/web-project/)를,
두 번의 실패 후 director 인수인계에 이르는 버그 수정 예시는
[`examples/existing-codebase/`](examples/existing-codebase/)를 참고하세요.

## 실제 예시 모음

| 예시 | 보여주는 내용 |
|---|---|
| [`examples/python-project/`](examples/python-project/) | 그린필드 CLI 도구, 단일 작업, 첫 번째 루프에서 승인 — 프로토콜의 가장 단순한 전체 실행. |
| [`examples/web-project/`](examples/web-project/) | 기존 웹 앱에 추가된 기능; 루프 1은 `not_wired_into_flow`로 실패, 루프 2에서 승인. |
| [`examples/existing-codebase/`](examples/existing-codebase/) | 버그 수정; 동일한 근본 원인으로 두 번 실패가 집계된 후 director가 인수인계. |
| [`examples/new-project/`](examples/new-project/) | 새 서비스의 독립된 두 작업을 병렬로 배정, 전체 충돌 도메인 점검 포함. |

이 네 가지 예시는 구조 에이전트/에스컬레이션 계층이 도입되기 전에 작성되었으며,
여전히 인수인계 경로를 직접 보여줍니다(더 강한 모델이었어도 도움이 되지
않았을 `requirement_conflict` 유형 사례). `reasoning_gap` 사례에서 그 인수인계
앞에 구조 에이전트 승격이 어디에 위치할지 함께 보려면
[`core/RESCUE-PROTOCOL.md`](core/RESCUE-PROTOCOL.md)를 같이 읽으세요.

## 실제 발췌: 작업 계약(task contract)

[`examples/existing-codebase/02-task-contract.json`](examples/existing-codebase/02-task-contract.json)에서
발췌·축약:

```json
{
  "task_id": "T-301",
  "title": "Fix timezone and off-by-one bug in weekly report aggregator",
  "objective": "Weekly sales totals must be computed consistently in UTC and must include every event from the full 7-day week, so reports do not silently under- or over-count sales depending on server locale or the exact second of a sale.",
  "current_state": "src/reports/aggregator.py's weekly_totals() calls timestamp.astimezone() with no explicit timezone, defaulting to the server's local time, and compares event timestamps to the week boundary using a strict '<', which excludes events landing exactly on the boundary.",
  "target_behavior": "weekly_totals(events) buckets every event by its UTC calendar week, inclusive of the full week, regardless of the server's local timezone setting.",
  "editable_files": ["src/reports/aggregator.py", "tests/reports/test_aggregator.py"],
  "forbidden_files": ["src/reports/exporter.py", "src/billing/invoice_totals.py"],
  "completion_criteria": [
    "A sale event timestamped 2026-08-02T23:30:00Z is counted in the week starting 2026-07-27, not the following week, regardless of server timezone."
  ],
  "test_commands": ["pytest tests/reports/test_aggregator.py -v"],
  "report_format": "implementation-report.schema.json"
}
```

## 실제 발췌: 검토 결과(review-result) 판정

[`examples/python-project/04-review-result.json`](examples/python-project/04-review-result.json)에서
발췌한 `approved` 판정(`revision_required` 판정과 `failure_reasons` 예시는
[`examples/existing-codebase/04-review-result.json`](examples/existing-codebase/04-review-result.json)
참고):

```json
{
  "task_id": "T-101",
  "loop_number": 1,
  "verdict": "approved",
  "checks": {
    "feature_wired_into_flow": {
      "result": "pass",
      "evidence": "Ran `python -m expense_tracker add 12.50 food --note lunch` ... directly in a shell; all three subcommands are registered in cli.py's argparse subparsers and produce the expected output, not just defined in isolation."
    },
    "tests_actually_executed": {
      "result": "pass",
      "evidence": "Re-ran `pytest tests/ -v` independently of the implementer's report: 8 passed in 0.39s, matching the reported test names and count."
    }
  },
  "notes": "Clean first-pass implementation. No revision loop required."
}
```

## 인수인계(takeover) 예시

[`examples/existing-codebase/`](examples/existing-codebase/)는 타임존/오프바이원
버그를 다룹니다. 두 번의 완전한 리비전 루프가 *동일한* 근본 원인으로 실패하는데,
매 시도가 일반적인 UTC 주 경계 규칙을 고치는 대신 director가 제공한 정확한 재현
날짜만 패치하기 때문입니다(루프 1은 `placeholder_implementation`, 루프 2는
`repeated_same_error` + `instruction_not_applied`). 두 루프 모두
`counted_as_failure: true`로 기록된 뒤에야 director는
[`09-takeover-record.json`](examples/existing-codebase/09-takeover-record.json)을
작성합니다 — "작업이 단순해서"가 아니라 두 실패의 구체적 증거와 실제 인과 분석
(`repeated_failure_cause`)을 인용하면서요 — 그런 다음
[`10-completion.md`](examples/existing-codebase/10-completion.md)에 따라 하나의
함수 본문으로 범위가 제한된 단일 직접 수정을 수행합니다.

## 병렬 작업 규칙

두 작업을 동시에 구현자에게 배정할 수 있는 것은 여덟 개의 충돌 도메인
(`files`, `data_structures`, `interfaces`, `db_entities`, `shared_configs`,
`state_stores`, `build_targets`, `user_flows`) 중 어느 것도 겹치지 않을 때뿐입니다.
단 하나의 도메인이라도 교집합이 있으면, 설령 두 작업이 의도상 무관해 보여도
순차 실행으로 강제됩니다 — 파일 하나만 공유해도 항상 순차화를 강제하기에
충분합니다. 전체 규칙과 실제 예시는
[`core/CONCURRENCY-RULES.md`](core/CONCURRENCY-RULES.md)를 참고하세요.

이 검사를 통과하는 것은 분리가 *안전하다*는 뜻이지 *필요하다*는 뜻이 아닙니다.
기본값은 검증 가능한 단위 규칙을 만족하는 최소 개수의 작업 계약이며, 구현자
하나가 여러 단계를 순차적으로 처리하는 게 예외가 아니라 흔한 경우입니다.
서브에이전트를 하나 이상으로 나누려면 다음 사유 중 하나가 그 서브에이전트의
`justification`으로 명시돼야 합니다
([`schemas/agent-composition-disclosure.schema.json`](schemas/agent-composition-disclosure.schema.json) 참고):

1. **진짜 병렬 이득** — 작업들의 `conflict_domains`가 서로 겹치지 않고,
   더 빨리 끝내는 것이 실질적으로 중요할 때.
2. **다른 effort 또는 모델 tier가 실제로 필요할 때** — 예: 한 부분은
   `investigation` 성격 작업이고 나머지는 `mechanical` 작업일 때.
3. **위험 범위 격리** — 위험한 변경을 안전한 변경과 독립적으로 리뷰하고
   싶을 때.
4. **진짜로 독립적인 검증 가능한 결과물들** — 억지로 하나의 계약에 묶으면
   개별적으로 리뷰하거나 되돌리기가 더 어려워질 때.

"더 작은 diff"나 "더 깔끔한 작업 ID" 같은 이유만으로는 절대 충분하지
않습니다. 활성 프로필의 `director.max_batch_agents`(기본값 4)를 넘는
배치는, 충돌 도메인 검사를 아무리 깔끔하게 통과하더라도 스폰되기 전에
사용자의 명시적 승인이 필요합니다. [`core/DELEGATION-PROTOCOL.md`](core/DELEGATION-PROTOCOL.md)
4단계를 참고하세요.

배치의 일부만 실패했을 때는 각 작업을 그 작업 자체의 증거로 판단합니다.
통과한 작업은 정상적으로 통합되고(실패한 작업에 의존하는 경우는 제외),
실패한 작업은 각자의 실패 루프를 각자의 횟수로 진행합니다 — 실패는 작업
간에 합산되지 않습니다. 만약 그 실패가 구현자 한 명의 문제가 아니라
*설계 자체*가 틀렸음을 드러낸다면, director는 통합을 멈추고 설계 단계로
돌아갑니다.

## 상태 안전성

이 문서의 다른 모든 규칙은 복구 가능한 작업 상태를 전제하므로,
[`core/STATE-SAFETY.md`](core/STATE-SAFETY.md)가 그 전제를 명시적인 규칙으로
만듭니다:

- **마지막 통과 체크포인트**("작업 시작 전 상태"가 아니라 실제 커밋 SHA나
  태그)를 첫 배정 전에 확보하고, 작업 트리가 더러우면 먼저 정리합니다 —
  그러지 않으면 이후의 모든 diff가 모호해집니다.
- **실패한 시도의 변경 내용은 director가 검토하기 전에 절대 파기하지
  않습니다.** 그 diff야말로 수정 지시, 구조 에이전트 패키지, 인수인계
  기록이 모두 의존하는 증거입니다. 검토 전 작업물에 `git checkout .`,
  `reset --hard`, `clean -fd`는 금지입니다.
- **implementer는 메인 라인에 커밋하지 않습니다.** 통합은 검수 게이트를
  통과한 뒤 director가 하는 단계이며, implementer는 자기 전용
  worktree/브랜치 안에서는 자유롭게 커밋해도 됩니다.
- **파괴적 작업은 의도적인 결정**이지 다른 작업에 딸린 부수 단계가 아닙니다
  — 이미 푸시된 브랜치의 force-push나 히스토리 재작성, 유일한 사본의 삭제,
  체크포인트 자체의 폐기 등.
- **동시에 실행되는 implementer는 격리된 작업 사본을 받습니다.** 충돌 도메인
  검사는 *의도된* 변경만 다루며, 한 에이전트의 부수적 쓰기나 재생성된
  아티팩트가 다른 에이전트의 diff에 섞이는 것까지 막아주지는 않습니다.
  격리 수단이 없으면 순차 실행합니다.

## 잘못된 사용 (안티패턴)

- **계약 없이 "UI 고쳐줘"를 위임하기.** 모호한 요청은 작업 계약이 아닙니다.
  director는 먼저 실제 문제를 재현하고 구체적인 `current_state` /
  `target_behavior` / `completion_criteria`를 작성해야 합니다.
- **"작은 작업이니까"라며 director가 직접 코딩하기.** 작업의 크기는 위임이나
  인수인계 요건을 건너뛰는 타당한 이유가 될 수 없습니다.
  `core/ROLE-CONTRACT.md`와 `core/TAKEOVER-PROTOCOL.md`를 참고하세요.
- **두 번 실패한 즉시 인수인계로 건너뛰기.** 두 번의 실패한 루프는 분류를
  촉발하며, 추론/능력 격차인 경우 *먼저* 구조 에이전트 시도를 촉발합니다 —
  인수인계는 그것마저 실패했을 때 일어나는 일이지, 자동으로 이어지는 다음
  단계가 아닙니다. `core/RESCUE-PROTOCOL.md` 참고.
- **아무 고지 없이 서브에이전트를 더 강한 모델로 승격시키기.** 모든 구조
  에이전트 승격 — 그리고 해결된 뒤 원래 등급으로의 복귀 — 은 일어나는 시점에
  통지됩니다. 결과 코드가 괜찮더라도, 조용한 승격(또는 조용한 원상복귀)은
  프로토콜 위반입니다.
- **implementer의 `status: complete`를 그대로 신뢰하기.** 이는 검토를
  시작시킬 뿐, 결코 검토를 끝내지 않습니다. director는 반드시 증거를 독립적으로
  검증해야 합니다.
- **재프롬프트를 리비전 루프로 계산하기.** 실패 후 새로운 증거 기반 지시 없이
  "되게 해줘"라고 다시 요청하는 것은 루프가 아니며, 두 번의 실패 임계값(에스컬레이션
  조건)에 포함되지 않습니다.
- **파일을 공유하는 작업을 병렬로 실행하기.** 다른 모든 충돌 도메인이 독립적이더라도,
  두 implementer가 동시에 같은 파일을 건드리는 것은 항상 차단되어야 하며,
  순차적으로 처리해야 합니다.
- **"혹시 모르니" 서브에이전트를 잘게 쪼개기.** 기본값은 검증 가능한 단위
  규칙을 만족하는 최소 개수의 작업이지, 최대한 잘게 쪼개는 게 아닙니다.
  고지되는 모든 서브에이전트는 `justification`을 명시해야 하고,
  `director.max_batch_agents`를 넘는 배치는 스폰되기 전에 사용자 승인이
  필요합니다 — 충돌 도메인 검사를 통과하는 것은 그 배치가 병렬 실행하기
  *안전하다*는 뜻이지, *규모가 적절하다*는 뜻이 아닙니다.
  `core/DELEGATION-PROTOCOL.md` 4단계와 `core/CONCURRENCY-RULES.md`를
  참고하세요.
- **implementer가 스스로 서브에이전트를 만들기.** 위임은 오직 director만
  합니다. implementer가 작업 도중 도움이 더 필요하다고 판단하면 그건
  차단됨/범위 밖 발견 사항으로 보고해야지, 직접 실행해서는 안 됩니다.
  `core/ROLE-CONTRACT.md` 참고.

## 한계

- **플랫폼 메커니즘은 서로 다르며, 이 저장소는 둘 사이의 대칭성을 억지로
  맞추지 않습니다.** Claude Code에는 네이티브 서브에이전트(Task/Agent 도구)가
  있지만, Codex에는 이에 대응하는 영속적인 서브에이전트 개념이 없습니다. 여기서
  Codex의 implementer 역할은 작업마다 새로 실행되는 `codex exec` 호출(또는 덜
  선호되는 방식으로 세션 내 서브에이전트 스레드)입니다. 두 어댑터는 동일한
  프로토콜을 각 플랫폼의 실제 기본 요소로 설명할 뿐, 공유된 구현체가 아닙니다.
- **프로필은 관례이지 강제 사항이 아닙니다.** 두 플랫폼 모두 이 저장소가
  연결할 수 있는 내장 "활성 프로필" 개념을 갖고 있지 않습니다. 프로필 YAML은
  director 자신의 지침(스킬)이 실제로 그것을 읽고 적용할 때만 동작합니다.
- **이것은 런타임이 아니라 지침입니다.** 이 저장소의 어떤 것도 규칙을
  기계적으로 강제하는 코드가 아닙니다. 준수 여부는 전적으로 모델이 실제로
  프로토콜을 따르는지에 달려 있습니다. `SKILL.md`나 `AGENTS.md`를 무시하는
  모델을, 제품 코드를 직접 작성하거나 스스로를 조용히 승격시키는 것으로부터
  이 저장소의 어떤 것도 막아주지 않습니다.

## 보안 유의사항

- 작업 계약은 정당하게 명령 실행을 지시할 수 있습니다(`test_commands`,
  `manual_verification`). 민감한 환경에서 실행하기 전에 `test_commands`를
  검토하세요 — 이는 implementer 세션이 가진 권한으로 실행됩니다.
- 작업 계약, 구현 보고서, 검토 결과, 에스컬레이션 요청, 인수인계 기록 어디에도
  비밀 정보, 자격 증명, 토큰을 절대 넣지 마세요. 이 문서들은 읽을 수 있는 감사
  기록으로 의도된 것입니다.
- 보고서에는 실제 명령 출력이 포함될 수 있습니다(`test_executions.output_excerpt`).
  기록하거나 공유하기 전에 그 출력에서 비밀 정보를 지우세요.

## 검증

어떤 변경 사항이든 신뢰하기 전에 전체 저장소 점검을 실행하세요.

```
python scripts/check_repository.py
```

Python 3.10+와 `pip install jsonschema`가 필요합니다. 이 명령은 모든 예시
JSON 문서에 대한 스키마 검증, 스킬/템플릿 구조 점검, 파일 간 링크 해석 확인,
민감 정보 스캔을 실행합니다. 종료 코드 0은 모두 통과했음을 의미합니다. CI는
모든 변경 사항에 대해 동일한 명령을 실행합니다(`.github/workflows/`의 일반
텍스트 상태, 배지 없음).

## 기여하기

변경 사항을 제안하는 방법, 스키마 우선(schema-first) 작업 흐름, 로컬에서
검증을 실행하는 방법은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

## 라이선스

[MIT](LICENSE) — 개인과 조직 누구나, 어떤 플랫폼에서든 최대한 자유롭게
재사용할 수 있도록 기본 라이선스로 선택되었습니다.

## 한국어 번역

이 문서(`README.ko.md`)는 [README.md](README.md)의 한국어 번역본입니다.
