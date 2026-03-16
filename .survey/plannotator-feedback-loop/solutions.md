# Solution Landscape: plannotator 피드백 루프 버그

## Root Cause Analysis

### 버그 A (Critical) — claude-plan-gate.py
- 위치: `should_skip()` + `main()` 반환값
- 원인: `SKIP_STATUSES`에 `feedback_required` 포함 → same hash + feedback_required → `exit 0`
- 영향: Claude Code가 hook exit 0을 "plan approved" 신호로 해석 → 피드백 미반영 상태로 EXECUTE 진행

### 버그 B (High) — omg SKILL.md exit 10 처리
- 위치: STEP 1 pre-flight bash block의 exit 10 분기
- 원인: `exit 1` 반환으로 에이전트가 OMG 실패로 오인, 피드백 반영 후 루프 재진입 명세 없음
- 영향: 에이전트가 피드백을 받아도 PLAN 루프를 재시작하지 않음

### 버그 C (Medium) — SKIP_FEEDBACK vs feedback 구분 없음
- 위치: SKILL.md STEP 1 exit 10 처리 메시지
- 원인: 새 피드백과 plan.md 미수정 재진입을 동일한 메시지로 처리
- 영향: 에이전트가 상황을 파악하지 못해 적절한 조치를 취하지 못함

## Fix Summary

| 버그 | 파일 | 수정 방향 |
|------|------|-----------|
| A | claude-plan-gate.py | `feedback_required` + same hash → `exit 1` (not 0) |
| B | omg SKILL.md | exit 10 → 루프 재진입 지시 명시, exit 1 → exit 10 유지 |
| C | omg SKILL.md | SKIP_FEEDBACK vs 일반 feedback 구분 메시지 추가 |

## Key Insight

plannotator 피드백 루프의 핵심 불변식은 "feedback_required + same hash ≠ approved"이다.
`claude-plan-gate.py`가 이 불변식을 위반(exit 0 반환)하여 루프 전체가 무너진다.
