# agent-director-protocol (ADP)

*[English](README.md)*

**자기 숙제를 스스로 채점한 에이전트의 “완료”를 그대로 믿지 마세요.**

ADP는 하나의 Claude Code 세션을 **Director**로 운영합니다. Director는
계획하고, 작업을 위임하고, 실제 diff와 실제 테스트 출력으로 검증한 뒤에만
완료를 판단합니다. 구현은 명확하고 검증 가능한 계약을 받은 worker가
수행합니다. 같은 원인에 대한 세 번째 추측성 수정은 금지되며 모든 추가와
승격은 사전에 고지됩니다.

이 배포본은 **Claude Code만 지원합니다.** ADP는 런타임이 아니라 Markdown
규칙, JSON Schema, 템플릿과 얇은 Claude Code adapter입니다. 대상 프로젝트에
설치할 daemon이나 별도 의존성은 없습니다.

## 설치

권장 방식은 Claude Code 플러그인 설치입니다.

```
/plugin marketplace add produckyou-design/agent-director-protocol
/plugin install agent-director@agent-director-protocol
```

작은 기능을 골라 Claude에게 “직접 코딩하지 말고 위임해”라고 요청하세요.
파일을 건드리기 전에 구성 고지와 작업 계약이 보여야 합니다.

전체 설치, 업데이트, 수동 복사와 제거 방법은
[`claude/INSTALL.md`](claude/INSTALL.md)에 있습니다.

## 무엇을 막는가

| 흔한 실패 | 막는 규칙 |
|---|---|
| 실제 연결이나 테스트 없이 “완료”라고 보고 | 실제 diff와 테스트 출력으로 검사하는 [10개 review gate](core/REVIEW-GATES.md) |
| stub이나 만들어낸 성공 결과 | `placeholder_implementation`, `fake_success` 같은 객관적 [failure reason](core/FAILURE-LOOP.md) |
| 같은 깨진 수정을 반복 | 같은 원인에 대한 세 번째 추측성 시도 금지 및 증거 기반 escalation |
| 조용한 모델 승격이나 worker 추가 | composition, promotion, addition disclosure를 실행 전에 고지 |
| 병렬 worker의 공유 파일 충돌 | [conflict-domain 검사](core/CONCURRENCY-RULES.md)로 공유 상태는 순차 처리 |
| 실패한 작업의 증거 유실 | [state safety](core/STATE-SAFETY.md)로 checkpoint와 실패 diff 보존 |
| 모호한 작업의 모호한 위임 | 현재 상태, 목표, 범위와 완료 조건을 적는 [task contract](core/TASK-CONTRACT.md) |

## 역할

| 역할 | 제품 코드 작성 | 전체 완료 선언 |
|---|---:|---:|
| Director | 기록된 사용자 승인 takeover에서만 | 예 |
| Implementer | 계약 범위 안에서 작성 | 아니오, evidence 보고만 |
| Reviewer | 작성하지 않음 | 아니오, Director에게 조언 |

Task tree에는 Director가 정확히 하나뿐입니다. Director는 root/current parent
Claude Code 세션입니다. 생성되는 모든 worker는 생성 전에 Director가
비(非)Director 역할을 부여받습니다. worker는 `director_mode: on`을
announce하거나 root-level disclosure를 게시하거나, 부모 contract를 다시
분해하거나, worker를 spawn/manage하거나, 작업을 integrate하거나 전체 task
완료를 선언해서는 안 됩니다.

모든 worker contract에는 다음 항목이 들어갑니다.

- `goal`
- scope와 non-goals
- `success_criteria`
- `failure_criteria`
- `termination_criteria`
- `required_evidence`

역할이나 기준이 빠지거나 모호하면 pre-spawn failure입니다.

## 동작 방식

```
분석 → 설계 → 구성 고지 → 작업 계약 작성 → 위임
  → 구현 및 테스트 → diff/evidence 확인 → 검토 → 통합
```

핵심 규칙은 다음 문서에 정의되어 있습니다.

- [역할 계약](core/ROLE-CONTRACT.md)
- [위임 프로토콜](core/DELEGATION-PROTOCOL.md)
- [작업 계약](core/TASK-CONTRACT.md)
- [동시성 규칙](core/CONCURRENCY-RULES.md)
- [검토 gate](core/REVIEW-GATES.md)
- [실패 loop](core/FAILURE-LOOP.md)
- [Escalation 프로토콜](core/ESCALATION-PROTOCOL.md)
- [Rescue 프로토콜](core/RESCUE-PROTOCOL.md)
- [Takeover 프로토콜](core/TAKEOVER-PROTOCOL.md)
- [완료 기준](core/COMPLETION-STANDARD.md)
- [상태 안전성](core/STATE-SAFETY.md)

## Worker recovery와 cleanup

네이티브 `RUNNING` worker는 기본적으로 보존합니다. wait timeout은 해당
대기 동안 final result가 도착하지 않았다는 관찰일 뿐입니다. timeout만으로
완료, interrupt, close, 분할 또는 재디스패치로 판단하지 않습니다.

첫 timeout에서는 관찰을 기록하고 작업에 맞는 bounded wait를 한 번 더
수행합니다. 단, crash, 반복된 tool error, 명시적 failure, runtime disconnect,
명백하게 반복되는 동일 command 같은 fatal runtime evidence가 이미 있으면
예외입니다.

파일 상태는 lifecycle evidence가 아닙니다. read-only 작업에서 파일 변경
여부는 stall evidence가 아니며, write 작업에서도 파일 변경이 없다는 사실만
으로 stall을 입증할 수 없습니다. read-only architecture/design 최종 report는
구체적 scope, evidence, findings, tests 또는 inspection commands와 unresolved
risks를 포함할 때만 completed-work artifact입니다.

progress telemetry가 없으면 `stalled`가 아니라 `unknown`으로 분류합니다.
명시적 fatal evidence 또는 선언된 bounded no-progress window가 끝난 경우에만
하나의 bounded interrupt를 허용합니다. interrupt는 현재 작업을 중단하고
이미 확보한 evidence만 요약하며 새 work, tests, edits를 시작하지 말고
종료하라는 뜻입니다. queued progress 요청은 interrupt가 아닙니다.

terminal result cleanup은 stalled recovery와 분리합니다. Director는 먼저
권위 있는 report/evidence를 캡처하고 저장한 다음 worker lifecycle을 하나의
atomic cleanup claim으로 reconcile합니다. root 세션이 끝나기 전에 자신이
만든 모든 lifecycle을 reconcile해야 하며 unreconciled child를 남겨 두고
조용히 종료해서는 안 됩니다.

worker를 close하거나 resume해도 fork가 main working tree에 자동 merge되지는
않습니다. Director는 fork diff나 report를 검토한 뒤 명시적으로 통합해야
합니다.

## 빠른 시작

1. Claude Code 플러그인을 설치하거나 Claude adapter를 수동 복사합니다.
2. 의미 있는 작업 부분이 두 개 이상인 기능을 고릅니다.
3. Claude에게 “이 기능의 Director로 동작해”라고 요청합니다.
4. 구성 고지 → task contract → worker report → 독립 review → 완료 evidence
   순서가 지켜지는지 확인합니다.

Director가 contract와 takeover 기록 없이 제품 코드를 직접 수정하거나,
worker를 조용히 추가·승격하면 프로토콜이 지켜지지 않은 것입니다.

## 설정 및 프로필

[`claude/profiles/default.yaml`](claude/profiles/default.yaml)은 skill이
읽는 정책 메타데이터입니다. Director 모델을 선택하거나 런타임을 강제하는
기능은 아닙니다. Director는 root Claude Code 세션을 실행하는 모델이며,
adapter는 의도한 정책과 네이티브 capability의 경계를 정직하게 기록합니다.

프로토콜은 프로젝트 전체의 숫자 worker cap을 만들지 않습니다. capacity의
권한은 네이티브 런타임에 있습니다. capacity를 알 수 없으면 한 개의 순차
worker를 사용하고 `capacity_source: "unknown"`으로 기록합니다. 병렬 작업은
두 개 이상의 독립적으로 검증 가능한 그룹, 분리된 conflict domain, dependency edge 없음,
격리된 write와 관찰된 capacity가 모두 있어야 합니다. work contract에는
`independent_groups`, `conflict_domains`, `dependency_edges`, `planned_workers`,
`capacity_source`, `write_isolation`, `why_fewer_workers_cannot_absorb`를
기록합니다. 관찰된 capacity가 있으면 `planned_workers = min(독립 그룹 수,
observed capacity)`를 사용하고, capacity가 unknown이면 worker 하나를
사용합니다. 속도나 효율만으로 worker를 추가할 수 없습니다.

## 프로젝트에 적용하기

프로젝트에 직접 설치할 때는 Claude skill과 platform-neutral 파일을 복사합니다.

```powershell
New-Item -ItemType Directory -Force -Path "<project>\.claude\skills" | Out-Null
Copy-Item -Recurse "claude\skills\agent-director" "<project>\.claude\skills\agent-director"
Copy-Item -Recurse "core" "<project>\core"
Copy-Item -Recurse "schemas" "<project>\schemas"
```

지속적인 프로젝트 지침이 필요하면
[`claude/CLAUDE.md.example`](claude/CLAUDE.md.example)을 프로젝트의
`CLAUDE.md`에 병합합니다.

## 예시

| 예시 | 보여주는 내용 |
|---|---|
| [`examples/python-project/`](examples/python-project/) | 첫 loop에서 승인되는 간단한 greenfield 작업 |
| [`examples/web-project/`](examples/web-project/) | 증거 기반 revision 한 번이 있는 기능 추가 |
| [`examples/existing-codebase/`](examples/existing-codebase/) | 기록된 실패 후 takeover에 이르는 버그 수정 |
| [`examples/new-project/`](examples/new-project/) | 독립 작업 그룹과 conflict-domain 검사 |

## 한계

- Claude adapter는 지침과 템플릿이지 hard enforcement runtime이 아닙니다.
  `SKILL.md`나 `CLAUDE.md`를 무시하는 모델을 이 저장소가 기계적으로 막지는
  못합니다.
- 프로필은 관례입니다. 문서와 다르면 네이티브 Claude Code 동작과 capacity가
  우선합니다.
- worker의 `complete` 자기보고는 review를 시작할 뿐 완료의 증거가 아닙니다.

## 보안 유의사항

task contract, report, escalation record, takeover record에 secret·credential·
token을 넣지 마세요. 실행 전 `test_commands`와 `manual_verification`을
검토하고, 캡처한 command output에서는 secret을 제거하세요.

## 검증

변경을 신뢰하기 전에 전체 검사를 실행합니다.

```
python scripts/check_repository.py
```

이 검사는 schema, 예시, Claude skill tree, 링크, 템플릿과 민감정보 규칙을
검증합니다. CI도 모든 push와 pull request에서 같은 검사를 실행합니다.

## 기여하기

schema-first 작업 흐름, 릴리스 절차와 로컬 검증 명령은
[`CONTRIBUTING.md`](CONTRIBUTING.md)를 참고하세요.

## 라이선스

[MIT](LICENSE).

## English translation

[`README.md`](README.md)가 이 문서의 영어 원문입니다.
