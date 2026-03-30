# OMG Checkpoint Helper Snippets

> Canonical Python snippets for recording state to `omg-state.json`.
> The full protocol is defined in SKILL.md § STEP 0.1.
> Use these snippets inline by substituting the `<phase>` / `<error message>` placeholders.

---

## 1. Checkpoint Recording

Record which phase the agent has entered. Run immediately at the start of each STEP.

```python
python3 -c "
import json,datetime,os,subprocess,fcntl
try:
    root=subprocess.check_output(['git','rev-parse','--show-toplevel'],stderr=subprocess.DEVNULL).decode().strip()
except:
    root=os.getcwd()
f=os.path.join(root,'.omc/state/omg-state.json')
if os.path.exists(f):
    with open(f,'r+') as fh:
        fcntl.flock(fh,fcntl.LOCK_EX)
        try:
            d=json.load(fh)
            d.update({'checkpoint':'<phase>','updated_at':datetime.datetime.utcnow().isoformat()+'Z'})
            fh.seek(0); json.dump(d,fh,ensure_ascii=False,indent=2); fh.truncate()
        finally:
            fcntl.flock(fh,fcntl.LOCK_UN)
" 2>/dev/null || true
```

Replace `<phase>` with: `plan` | `execute` | `verify` | `cleanup`

---

## 2. last_error Recording

Record an error message and increment `retry_count`. Run before any `exit 1` in pre-flight.

```python
python3 -c "
import json,datetime,os,subprocess,fcntl
try:
    root=subprocess.check_output(['git','rev-parse','--show-toplevel'],stderr=subprocess.DEVNULL).decode().strip()
except:
    root=os.getcwd()
f=os.path.join(root,'.omc/state/omg-state.json')
if os.path.exists(f):
    with open(f,'r+') as fh:
        fcntl.flock(fh,fcntl.LOCK_EX)
        try:
            d=json.load(fh)
            d['last_error']='<error message>'
            d['retry_count']=d.get('retry_count',0)+1
            d['updated_at']=datetime.datetime.utcnow().isoformat()+'Z'
            fh.seek(0); json.dump(d,fh,ensure_ascii=False,indent=2); fh.truncate()
        finally:
            fcntl.flock(fh,fcntl.LOCK_UN)
" 2>/dev/null || true
```

Replace `<error message>` with a short description of the failure.

---

## 3. Checkpoint-Based Resume

Read checkpoint and last_error on restart to determine where to resume.

```python
python3 -c "
import json, os, subprocess
try:
    root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], stderr=subprocess.DEVNULL).decode().strip()
except:
    root = os.getcwd()
f = os.path.join(root, '.omc/state/omg-state.json')
if os.path.exists(f):
    d=json.load(open(f))
    cp=d.get('checkpoint')
    err=d.get('last_error')
    if err: print(f'Previous error: {err}')
    if cp: print(f'Resuming from: {cp}')
" 2>/dev/null || true
```
