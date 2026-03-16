# Context: plannotator 피드백 루프 버그

## Workflow Context

omg 스킬 PLAN 단계 흐름:
1. 에이전트가 plan.md 작성
2. ExitPlanMode → claude-plan-gate.py → plannotator 실행
3. 사용자가 브라우저에서 Approve 또는 Send Feedback 클릭
4. Approve → EXECUTE 진행 / Feedback → plan.md 수정 후 재시도

## Affected Users

| 역할 | 영향 |
|------|------|
| Claude Code 사용자 | plannotator 피드백 후 plan이 수정되지 않아 EXECUTE 단계로 진행됨 |
| Codex / Gemini 사용자 | exit 10 후 OMG 루프 종료로 피드백 반영 불가 |

## Current Workarounds

1. 피드백 후 plan.md를 반드시 수정하여 hash를 변경
2. `omg-state.json`의 `plan_gate_status`를 수동으로 `pending`으로 리셋
3. `last_reviewed_plan_hash`를 null로 초기화 후 재시도

## Adjacent Problems

- 에이전트가 피드백을 읽고 plan.md를 수정했음에도 hash 계산 불일치로 SKIP 발생 가능성
- 피드백 내용이 state에 저장되지만 다음 루프에서 참조되지 않음
