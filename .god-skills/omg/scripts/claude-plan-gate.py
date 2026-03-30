#!/usr/bin/env python3
"""OMG Claude plan gate wrapper.

Wraps the Claude Code ExitPlanMode hook so OMG can skip redundant plannotator
launches when the current plan content has already been reviewed.

Fixes applied:
- Double execution: saves plannotator result to state so skip guard activates
  on subsequent ExitPlanMode hook invocations.
- Page error: captures plannotator stdout so its approval JSON is NOT passed
  to Claude Code's hook system. emit_hook_decision() writes the correct format.
- ralphmode transition: writes next_mode="ralphmode" to state on approval.
- rc=32 CONVERSATION APPROVAL MODE: fallback when plannotator UI cannot bind port.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

try:
    import fcntl
    _FCNTL_AVAILABLE = True
except ImportError:
    _FCNTL_AVAILABLE = False


SKIP_STATUSES = {"approved", "manual_approved", "feedback_required", "infrastructure_blocked"}
POST_PLAN_PHASES = {"execute", "verify", "verify_ui", "cleanup", "done", "ralphmode"}
PLANNOTATOR_PORT = int(os.environ.get("PLANNOTATOR_PORT", "47291"))
_LOCK_FILE = Path(tempfile.gettempdir()) / "omg-plannotator-claude-gate.lock"


def git_root() -> Path:
    try:
        return Path(
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        )
    except Exception:
        return Path.cwd()


def state_path(root: Path) -> Path:
    return root / ".omc" / "state" / "omg-state.json"


def load_state(root: Path) -> dict[str, Any]:
    path = state_path(root)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(root: Path, state: dict[str, Any]) -> None:
    path = state_path(root)
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    if _FCNTL_AVAILABLE:
        with open(path, "w", encoding="utf-8") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                json.dump(state, fh, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)
    else:
        path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def find_plan_text(root: Path, payload: str) -> str:
    for candidate in (
        root / ".omc" / "plans" / "omg-plan.md",
        root / "plan.md",
        root / "docs" / "plan.md",
    ):
        if candidate.exists():
            try:
                return candidate.read_text(encoding="utf-8")
            except Exception:
                continue

    try:
        data = json.loads(payload)
    except Exception:
        return ""

    tool_input = data.get("tool_input", {})
    if isinstance(tool_input, dict):
        plan = tool_input.get("plan")
        if isinstance(plan, str):
            return plan
    return ""


def plan_hash(plan_text: str) -> str:
    if not plan_text:
        return ""
    return hashlib.sha256(plan_text.encode("utf-8")).hexdigest()


def should_skip(state: dict[str, Any], current_hash: str) -> bool:
    phase = state.get("phase")
    if phase in POST_PLAN_PHASES:
        return True

    gate_status = state.get("plan_gate_status")
    last_hash = state.get("last_reviewed_plan_hash")
    return bool(current_hash and gate_status in SKIP_STATUSES and last_hash == current_hash)


def reset_for_revised_plan(root: Path, state: dict[str, Any], current_hash: str) -> None:
    last_hash = state.get("last_reviewed_plan_hash")
    if not current_hash or current_hash == last_hash:
        return

    if state.get("plan_gate_status") in SKIP_STATUSES:
        state["plan_gate_status"] = "pending"
        state["plan_approved"] = False
        state["plan_current_hash"] = current_hash
        state["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
        save_state(root, state)


def update_state_after_plannotator(
    root: Path,
    state: dict[str, Any],
    rc: int,
    current_hash: str,
) -> None:
    now = datetime.datetime.utcnow().isoformat() + "Z"

    if rc == 0:
        state["plan_gate_status"] = "approved"
        state["plan_approved"] = True
        state["phase"] = "execute"
        state["next_mode"] = "ralphmode"
    elif rc == 10:
        state["plan_gate_status"] = "feedback_required"
        state["plan_approved"] = False

    state["last_reviewed_plan_hash"] = current_hash
    state["plan_current_hash"] = current_hash
    state["last_reviewed_plan_at"] = now
    state["plan_review_method"] = "plannotator"
    state["updated_at"] = now
    save_state(root, state)


def is_plannotator_listening(port: int) -> bool:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect(("127.0.0.1", port))
        s.close()
        return True
    except Exception:
        return False


def try_acquire_lock() -> Optional[Any]:
    if not _FCNTL_AVAILABLE:
        return object()
    try:
        fh = open(_LOCK_FILE, "w")
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fh
    except (IOError, OSError):
        return None


def release_lock(fh: Any) -> None:
    if not _FCNTL_AVAILABLE or fh is None:
        return
    try:
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()
        _LOCK_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def run_plannotator(payload: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["plannotator"],
        input=payload,
        text=True,
        capture_output=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def emit_hook_decision(decision: str, reason: str = "") -> None:
    payload: dict[str, Any] = {"decision": decision}
    if reason:
        payload["reason"] = reason
    print(json.dumps(payload))


def main() -> int:
    payload = sys.stdin.read()
    root = git_root()
    state = load_state(root)
    current_hash = plan_hash(find_plan_text(root, payload))

    if should_skip(state, current_hash):
        status = state.get("plan_gate_status", "unknown")
        phase = state.get("phase", "unknown")
        print(
            f"[OMG][PLAN] Claude hook skipped: plan gate already recorded "
            f"(status={status}, phase={phase}).",
            file=sys.stderr,
        )
        emit_hook_decision("allow", f"Skipped: plan already reviewed ({status})")
        return 0

    if is_plannotator_listening(PLANNOTATOR_PORT):
        print(
            f"[OMG][PLAN] plannotator already listening on port {PLANNOTATOR_PORT} "
            "— deferring to existing instance.",
            file=sys.stderr,
        )
        emit_hook_decision("allow", "Deferred: plannotator already running")
        return 0

    lock_fh = try_acquire_lock()
    if lock_fh is None:
        print(
            "[OMG][PLAN] Another plannotator launch is in progress — skipping duplicate.",
            file=sys.stderr,
        )
        emit_hook_decision("allow", "Skipped: concurrent launch detected")
        return 0

    try:
        reset_for_revised_plan(root, state, current_hash)
        rc, stdout, stderr = run_plannotator(payload)

        update_state_after_plannotator(root, state, rc, current_hash)

        if rc == 0:
            emit_hook_decision(
                "allow",
                "Plan approved by plannotator. "
                "OMG: next_mode=ralphmode written to state — invoke /omc:ralphmode to begin autonomous execution.",
            )
            return 0
        elif rc == 10:
            emit_hook_decision(
                "allow",
                "Plan review requested changes. "
                "Revise plan.md and re-enter plan mode to reopen plannotator.",
            )
            return 0
        elif rc == 32:
            emit_hook_decision(
                "allow",
                "plannotator UI unavailable (port bind blocked / sandbox). "
                "CONVERSATION APPROVAL MODE: output plan.md to the user in full, "
                "ask them to reply 'approve' or provide specific feedback. "
                "Do NOT proceed to development until explicit approval is received.",
            )
            return 0
        else:
            if stderr:
                print(f"[OMG][PLAN] plannotator stderr: {stderr.strip()}", file=sys.stderr)
            emit_hook_decision("allow", f"plannotator exited with code {rc}.")
            return 0
    finally:
        release_lock(lock_fh)


if __name__ == "__main__":
    raise SystemExit(main())
