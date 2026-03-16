# Platform Map: plannotator 피드백 루프

## Hooks

| 라이프사이클 | Claude Code | Codex / Gemini / OpenCode |
|-------------|-------------|--------------------------|
| PLAN 진입 | ExitPlanMode PermissionRequest hook → claude-plan-gate.py | plannotator-plan-loop.sh (blocking CLI) |
| 피드백 신호 | hook return code (0=approved, non-zero=rejected) | exit 10 |
| 피드백 저장 | omg-state.json plannotator_feedback 필드 | FEEDBACK_FILE JSON |
| 루프 재진입 | EnterPlanMode → 수정 → ExitPlanMode | script 재실행 |

## Platform Gaps

| 플랫폼 | 갭 |
|--------|-----|
| Claude Code | claude-plan-gate.py의 exit 0/1 반환값이 approved/rejected 의미를 가짐 — feedback_required도 exit 0 반환 시 approved로 오인 |
| Codex/Gemini | exit 10 후 SKILL.md에서 `exit 1`로 처리 — 에이전트가 루프 재진입 안 함 |
| 공통 | SKIP_FEEDBACK 상황에서 에이전트가 "plan.md 미수정"임을 알 수 없음 |
