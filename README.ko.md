# agent-director-protocol

*[English](README.md)*

AI 코딩 에이전트를 위한 플랫폼 중립적 운영 프로토콜입니다. 역량이 높은 하나의
**디렉터(director)**가 계획하고, 작업을 분해하고, 위임하고, 검토하며,
**구현자(implementer)** 서브에이전트가 실제 코드를 작성합니다. 핵심 프로토콜은
플랫폼에 독립적이며, 얇은 어댑터가 Claude Code와 OpenAI Codex에 이를 연결합니다.

## 해결하려는 문제

단일 최상위 모델이 혼자 작업하면 모든 것을 스스로 하려는 경향이 있습니다.
코드를 읽고, 변경 사항을 설계하고, 작성하고, 테스트하고, 자기 숙제를 스스로
채점하는 과정을 한 번의 끊김 없는 흐름으로 처리합니다. 이는 가장 유능하고(그리고
가장 비용이 큰) 모델의 주의력을 기계적인 편집에 소모시키고, "코드를 작성했다"와
"작업이 끝났다" 사이를 가로막는 독립적인 검증 단계를 제거합니다. 스스로 구현하고
스스로 검토하는 모델에게는 자신의 실수를 찾아내도록 강제하는 적대적 압력이
존재하지 않습니다.

이 저장소는 품질이나 비용이 몇 퍼센트 향상된다는 식의 검증 불가능한 주장을 하지
않습니다. 대신 하나의 메커니즘을 설명합니다. 작업을 **계획, 위임, 검토**하는
역할과 **구현**하는 역할로 나누고, 위임되는 모든 작업 단위를 문서화되고 검증
가능한 계약을 통과하도록 강제하며, 검토 역할이 자기보고된 "완료"를 신뢰하는 대신
실제 diff와 실제 테스트 출력 같은 증거를 검증하도록 요구합니다. 결과는 벤치마크
주장이 아니라 하나의 작업 흐름입니다. 문서를 읽고, 이 메커니즘이 여러분의
프로젝트에 맞는지 판단하고, 결과는 직접 평가하시기 바랍니다.

## 역할

| 역할 | 제품 코드 작성 | 테스트 작성 | 완료 선언 |
|---|---|---|---|
| director | 기록된 인수인계(takeover) 하에서만 | 아니오 | 예 |
| implementer | 예, 계약 범위 내에서 | 예 | 아니오 (상태만 자가 보고) |
| reviewer | 아니오 | 아니오 | 아니오 (director에게 조언) |

reviewer는 반드시 별도의 참여자가 아니라 하나의 역할이며, 기본적으로 director가
수행합니다. 전체 정의, 경계, "director는 제품 코드를 작성하지 않는다"는 규칙은
[`core/ROLE-CONTRACT.md`](core/ROLE-CONTRACT.md)에 있습니다.

## 동작 방식

```
 analyze repo ──▶ interpret requirement ──▶ design ──▶ decompose into tasks
      │                                                       │
      │  core/DELEGATION-PROTOCOL.md                          ▼
      │                                          write a task contract per task
      │                                          core/TASK-CONTRACT.md
      │                                                       │
      │                                                       ▼
      │                                    order by dependency / conflict check
      │                                    core/CONCURRENCY-RULES.md
      │                                                       │
      │                                                       ▼
      │                                       delegate ──▶ implement + test
      │                                                (implementer role)
      │                                                       │
      │                                                       ▼
      │                                          director review (10 gates)
      │                                          core/REVIEW-GATES.md
      │                                                       │
      │                                    ┌──────────────────┴──────────────────┐
      │                                    ▼                                     ▼
      │                              approved                          revision_required /
      │                                    │                               rejected
      │                                    ▼                                     │
      │                          completion standard                            ▼
      │                          core/COMPLETION-STANDARD.md         evidence-based revision
      │                                    ▲                         instruction, loop again
      │                                    │                         core/FAILURE-LOOP.md
      │                                    │                                     │
      │                                    │                     2 counted failures on this task?
      │                                    │                                     │
      │                                    │                                    yes
      │                                    │                                     ▼
      │                                    └───────────────────────  takeover record, then a
      │                                                               single bounded direct fix
      │                                                               core/TAKEOVER-PROTOCOL.md
      ▼
 integration + regression pass across all tasks (core/COMPLETION-STANDARD.md)
```

위 다이어그램의 각 단계는 해당 단계를 정의하는 core 문서로 연결됩니다.
요약하자면 다음과 같습니다. 어떤 작업도 모호하게 위임되지 않고, 어떤 결과물도
자기보고만으로 수락되지 않으며, 객관적으로 독립된 실패가 두 번 발생했을 때만
director가 제품 코드를 직접 건드릴 수 있고, "완료"는 증거에 근거한 director의
판단이지 implementer의 `status` 필드가 결코 아닙니다.

## 저장소 구조

```
agent-director-protocol/
├─ README.md  README.ko.md  LICENSE  CHANGELOG.md
├─ CONTRIBUTING.md  SECURITY.md  CODE_OF_CONDUCT.md  .gitignore
├─ core/                         platform-neutral protocol (8 docs)
│  ├─ ROLE-CONTRACT.md           DELEGATION-PROTOCOL.md
│  ├─ TASK-CONTRACT.md           FAILURE-LOOP.md
│  ├─ REVIEW-GATES.md            CONCURRENCY-RULES.md
│  ├─ TAKEOVER-PROTOCOL.md       COMPLETION-STANDARD.md
├─ claude/                       Claude Code adapter
│  ├─ skills/agent-director/SKILL.md + references/*.md
│  ├─ CLAUDE.md.example          profiles/{opus-director,fable-director}.yaml
│  └─ INSTALL.md
├─ codex/                        OpenAI Codex adapter
│  ├─ skills/agent-director/SKILL.md + references/*.md
│  ├─ AGENTS.md.example          profiles/sol-director.yaml
│  └─ INSTALL.md
├─ schemas/                      5 JSON Schema (draft-07) documents
├─ examples/                     4 worked, schema-valid scenarios
│  ├─ python-project/  web-project/  existing-codebase/  new-project/
├─ scripts/                      validation scripts (check_repository.py, ...)
├─ tests/                        unittest suite
└─ .github/workflows/            CI: runs the validation scripts
```

## 빠른 설치 — Claude Code

스킬을 프로젝트(또는 사용자 전역 스킬 디렉터리)에 복사한 다음,
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
3. "동작 방식"에서 설명한 순서를 확인하세요. director는 먼저 관련 코드를 읽고,
   (파일 편집을 바로 시작하지 않고) **작업 계약(task contract)**을 작성한 뒤,
   그 계약을 서브에이전트에게 위임하고, 실제 테스트 출력이 담긴 **구현
   보고서(implementation report)**를 요구하고, 증거와 함께 열 가지 검사 항목을
   채점한 **검토 결과(review result)**를 작성하고, 마지막으로 실제로 검증한
   내용을 인용하는 짧은 **완료 보고서**를 내야 합니다.
4. 만약 director가 작업 계약도 없이, 인수인계(takeover) 기록도 없이 제품
   코드를 직접 편집하는 모습이 보인다면, 프로토콜이 지켜지지 않고 있는 것입니다.
   아래 "잘못된 사용" 절을 참고하세요.

## 설정 및 모델 프로필

프로필(`claude/profiles/*.yaml`, `codex/profiles/sol-director.yaml`)은 Claude
Code나 Codex가 강제하는 메커니즘이 아니라 **스킬 자체의 지침이 읽는 관례**입니다.
각 프로필은 역할별 선호 모델을 지정하는 작은 YAML 파일입니다.

```yaml
# Model names are environment aliases the user may freely change; the protocol never depends on a specific model name.
director:
  preferred_models: [opus-5]
  effort: high        # optional hint; adapters map to platform mechanism or omit
implementer:
  preferred_models: [sonnet-5]
reviewer:
  inherit: director   # default: reviewer == director
```

모델 이름은 환경 별칭(alias)이므로 여러분의 플랫폼이 실제로 어떤 모델로
해석하든 자유롭게 바꿔도 됩니다. `core/`는 어떤 모델 이름도 언급하지 않으며,
오직 `*/profiles/*.yaml`만 언급합니다. 프로필을 바꾸려면 YAML 파일을 직접
편집하거나, (Claude Code) 선택한 파일을 `SKILL.md` 옆의 `profile.yaml`로
복사하거나, (Codex) `preferred_models`/`effort` 필드를 각 플랫폼의
`INSTALL.md`에서 설명하는 대로 여러분의 `config.toml` / 이름 있는 프로필로
번역하면 됩니다.

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

## 잘못된 사용 (안티패턴)

- **계약 없이 "UI 고쳐줘"를 위임하기.** 모호한 요청은 작업 계약이 아닙니다.
  director는 먼저 실제 문제를 재현하고 구체적인 `current_state` /
  `target_behavior` / `completion_criteria`를 작성해야 합니다.
- **"작은 작업이니까"라며 director가 직접 코딩하기.** 작업의 크기는 위임이나
  인수인계 요건을 건너뛰는 타당한 이유가 될 수 없습니다.
  `core/ROLE-CONTRACT.md`와 `core/TAKEOVER-PROTOCOL.md`를 참고하세요.
- **implementer의 `status: complete`를 그대로 신뢰하기.** 이는 검토를
  시작시킬 뿐, 결코 검토를 끝내지 않습니다. director는 반드시 증거를 독립적으로
  검증해야 합니다.
- **재프롬프트를 리비전 루프로 계산하기.** 실패 후 새로운 증거 기반 지시 없이
  "되게 해줘"라고 다시 요청하는 것은 루프가 아니며, 두 번의 실패 임계값(인수인계
  조건)에 포함되지 않습니다.
- **파일을 공유하는 작업을 병렬로 실행하기.** 다른 모든 충돌 도메인이 독립적이더라도,
  두 implementer가 동시에 같은 파일을 건드리는 것은 항상 차단되어야 하며,
  순차적으로 처리해야 합니다.

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
  모델을 이 저장소의 어떤 것도 막아서 제품 코드를 직접 작성하지 못하게 하지
  않습니다.

## 보안 유의사항

- 작업 계약은 정당하게 명령 실행을 지시할 수 있습니다(`test_commands`,
  `manual_verification`). 민감한 환경에서 실행하기 전에 `test_commands`를
  검토하세요 — 이는 implementer 세션이 가진 권한으로 실행됩니다.
- 작업 계약, 구현 보고서, 검토 결과, 인수인계 기록 어디에도 비밀 정보,
  자격 증명, 토큰을 절대 넣지 마세요. 이 문서들은 읽을 수 있는 감사 기록으로
  의도된 것입니다.
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
