# Fabric — LM Studio Provider 설정 가이드

> LM Studio를 로컬 AI 백엔드로 사용하여 fabric을 오프라인·프라이버시 환경에서 실행하는 방법을 설명합니다.

**목차**

1. [LM Studio란?](#1-lm-studio란)
2. [사전 준비](#2-사전-준비)
3. [LM Studio 설치 및 모델 로드](#3-lm-studio-설치-및-모델-로드)
4. [LM Studio 서버 시작](#4-lm-studio-서버-시작)
5. [fabric에 LM Studio 설정](#5-fabric에-lm-studio-설정)
   - [방법 A: `fabric --setup` 대화형 설정](#방법-a-fabric---setup-대화형-설정)
   - [방법 B: .env 파일 직접 편집](#방법-b-env-파일-직접-편집)
   - [방법 C: 명령어 플래그로 일회성 사용](#방법-c-명령어-플래그로-일회성-사용)
6. [연결 확인 및 테스트](#6-연결-확인-및-테스트)
7. [패턴별 모델 라우팅](#7-패턴별-모델-라우팅)
8. [트러블슈팅](#8-트러블슈팅)
9. [참고 자료](#9-참고-자료)

---

## 1. LM Studio란?

[LM Studio](https://lmstudio.ai)는 macOS / Windows / Linux에서 로컬 LLM을 다운로드하고 실행할 수 있는 데스크톱 앱입니다.
`/v1/chat/completions` 등 **OpenAI API 호환 엔드포인트**를 내장 서버로 제공하므로, OpenAI API를 지원하는 모든 클라이언트에서 LM Studio를 그대로 교체해 사용할 수 있습니다.

### 왜 fabric + LM Studio인가?

| 이유 | 설명 |
|------|------|
| **완전 오프라인** | API 키 불필요, 인터넷 차단 환경에서도 동작 |
| **프라이버시** | 데이터가 로컬 밖으로 전송되지 않음 |
| **비용 없음** | 추론 비용 0원 |
| **모델 자유도** | Llama, Mistral, Gemma, Phi, DeepSeek 등 Hugging Face 모델 직접 선택 |
| **네이티브 지원** | fabric v1.4+ 에서 `LM Studio` 벤더 공식 내장 |

---

## 2. 사전 준비

```bash
# fabric 설치 확인 (v1.4.0 이상 권장)
fabric --version

# 미설치 시 설치
# macOS (Homebrew)
brew install fabric-ai

# 또는 공식 인스톨러
curl -fsSL https://raw.githubusercontent.com/danielmiessler/fabric/main/scripts/installer/install.sh | bash

# 패턴 최신화
fabric -u
```

---

## 3. LM Studio 설치 및 모델 로드

### 3-1. LM Studio 다운로드

```
https://lmstudio.ai
```

macOS, Windows, Linux(AppImage) 패키지 제공.

### 3-2. 모델 다운로드

LM Studio 앱에서 **Discover** 탭 → 모델 검색 → **Download**.

권장 범용 모델 (일반 PC 기준):

| 모델 | 크기 | 용도 |
|------|------|------|
| `lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF` | ~5 GB | 범용 |
| `bartowski/gemma-3-12b-it-GGUF` | ~7 GB | 코드·분석 |
| `lmstudio-community/Mistral-7B-Instruct-v0.3-GGUF` | ~4 GB | 빠른 요약 |
| `lmstudio-community/DeepSeek-R1-Distill-Qwen-7B-GGUF` | ~5 GB | 추론·분석 |
| `lmstudio-community/Phi-4-mini-instruct-GGUF` | ~2.5 GB | 경량·빠름 |

> **모델 ID 확인**: 다운로드 후 앱 좌측 목록 또는 API 응답의 `id` 필드에서 확인.
> 형식: `publisher/model-name` (예: `lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF`)

---

## 4. LM Studio 서버 시작

### 방법 1: CLI (권장)

```bash
# LM Studio CLI 설치 (앱 설치 후 자동 등록)
lms server start

# 상태 확인
lms server status

# 서버 중지
lms server stop
```

### 방법 2: 앱 GUI

1. LM Studio 앱 실행
2. 좌측 사이드바 → **Developer** (또는 **Local Server**) 탭
3. **Start Server** 클릭
4. 기본 포트: **1234**

### 방법 3: 로그인 시 자동 시작

앱 설정(`Cmd/Ctrl + ,`) → **Start server on app startup** 활성화

### 서버 동작 확인

```bash
# 모델 목록 확인 (서버 정상 동작 시 JSON 반환)
curl http://localhost:1234/v1/models

# 응답 예시
# {
#   "data": [
#     { "id": "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF", ... }
#   ]
# }
```

> **기본 엔드포인트**: `http://localhost:1234/v1`
> 포트 변경 시 앱 설정 또는 `lms server start --port <PORT>`

---

## 5. fabric에 LM Studio 설정

### 방법 A: `fabric --setup` 대화형 설정

```bash
fabric --setup
```

프롬프트가 순서대로 표시됩니다:

```
Available vendors:
  1. OpenAI
  2. Anthropic
  3. Google
  4. LM Studio          ← 선택
  5. Ollama
  ...

Enter vendor number: 4

Enter LM Studio API base URL [http://localhost:1234/v1]:
(Enter 키로 기본값 사용)

Fetching models from LM Studio...
Available models:
  1. lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF
  2. bartowski/gemma-3-12b-it-GGUF
  ...

Enter model number (or model name): 1

Default vendor set to: LM Studio
Default model set to:  lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF
```

> **주의**: `fabric --setup` 실행 전에 반드시 LM Studio 서버가 실행 중이어야 모델 목록을 불러올 수 있습니다.

---

### 방법 B: .env 파일 직접 편집

설정 파일 위치: `~/.config/fabric/.env`

```bash
# 현재 설정 확인
cat ~/.config/fabric/.env

# 편집
nano ~/.config/fabric/.env
# 또는
code ~/.config/fabric/.env
```

**최소 필수 설정:**

```dotenv
# ─── LM Studio Provider ───────────────────────────────
LM_STUDIO_API_BASE_URL=http://localhost:1234/v1

# ─── 기본 벤더 / 모델 ────────────────────────────────
DEFAULT_VENDOR=LM Studio
DEFAULT_MODEL=lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF
```

**완전한 설정 예시 (다른 provider와 공존):**

```dotenv
# ─── OpenAI (선택) ─────────────────────────────────────
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# ─── Anthropic (선택) ──────────────────────────────────
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx

# ─── LM Studio (로컬) ──────────────────────────────────
LM_STUDIO_API_BASE_URL=http://localhost:1234/v1

# ─── 기본값: LM Studio 사용 ──────────────────────────
DEFAULT_VENDOR=LM Studio
DEFAULT_MODEL=lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF
```

> **API 키**: LM Studio는 기본적으로 인증이 필요 없습니다.
> Developer 설정에서 토큰 인증을 활성화했다면 `LM_STUDIO_API_KEY=<your-token>` 을 추가하세요.

**변경사항 즉시 반영** — fabric은 명령 실행 시 `.env`를 매번 읽으므로 재시작이 불필요합니다.

---

### 방법 C: 명령어 플래그로 일회성 사용

설정 파일을 변경하지 않고 특정 명령에서만 LM Studio를 사용합니다:

```bash
# --vendor 와 -m 플래그 사용
cat article.txt | fabric -p summarize \
  --vendor "LM Studio" \
  -m "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF"

# YouTube 요약
fabric -y "https://youtube.com/watch?v=VIDEO_ID" \
  -p extract_wisdom \
  --vendor "LM Studio" \
  -m "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF"

# 스트리밍 출력
echo "코드 리뷰해줘" | fabric -p explain_code \
  --vendor "LM Studio" \
  -m "bartowski/gemma-3-12b-it-GGUF" \
  --stream
```

---

## 6. 연결 확인 및 테스트

### 6-1. 모델 목록 확인

```bash
# LM Studio 벤더의 사용 가능 모델 목록
fabric --listmodels --vendor "LM Studio"

# 또는 전체 모델 목록 (현재 설정 벤더 포함)
fabric --listmodels
```

### 6-2. 빠른 동작 테스트

```bash
# 간단한 텍스트 요약
echo "Fabric is an open-source AI prompt orchestration framework." \
  | fabric -p summarize

# 예상 출력 (로컬 모델이 처리)
# ONE SENTENCE SUMMARY:
# Fabric is an open-source framework for AI prompt orchestration using reusable patterns.
```

### 6-3. 연결 진단

```bash
# 서버 직접 호출 테스트
curl -s http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
    "messages": [{"role": "user", "content": "Say hello"}],
    "stream": false
  }' | jq '.choices[0].message.content'
```

---

## 7. 패턴별 모델 라우팅

무거운 작업과 가벼운 작업에 각각 다른 로컬 모델을 자동 배정할 수 있습니다.

`~/.config/fabric/.env` 에 추가:

```dotenv
# ─── 패턴별 모델 라우팅 (LM Studio) ──────────────────

# 코드 분석 → 코드 특화 모델
FABRIC_MODEL_PATTERN_EXPLAIN_CODE=LM Studio|bartowski/gemma-3-12b-it-GGUF

# 빠른 요약 → 경량 모델
FABRIC_MODEL_PATTERN_SUMMARIZE=LM Studio|lmstudio-community/Phi-4-mini-instruct-GGUF

# 심층 분석 → 고성능 모델
FABRIC_MODEL_PATTERN_EXTRACT_WISDOM=LM Studio|lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF
FABRIC_MODEL_PATTERN_ANALYZE_PAPER=LM Studio|lmstudio-community/DeepSeek-R1-Distill-Qwen-7B-GGUF

# 글쓰기 → 범용 모델
FABRIC_MODEL_PATTERN_WRITE_ESSAY=LM Studio|lmstudio-community/Mistral-7B-Instruct-v0.3-GGUF
FABRIC_MODEL_PATTERN_IMPROVE_WRITING=LM Studio|lmstudio-community/Mistral-7B-Instruct-v0.3-GGUF
```

---

## 8. 트러블슈팅

### ❌ `Error: connection refused` 또는 모델 목록 비어있음

```bash
# LM Studio 서버 실행 여부 확인
curl http://localhost:1234/v1/models

# 서버 재시작
lms server stop && lms server start

# 포트 사용 중인 프로세스 확인 (macOS/Linux)
lsof -i :1234
```

### ❌ `fabric --setup` 시 LM Studio 모델 목록이 안 뜸

설정 중 서버가 실행 중이어야 합니다. 서버를 먼저 시작하고 다시 시도:

```bash
lms server start
fabric --setup
```

또는 방법 B (`.env` 직접 편집)로 설정하세요.

### ❌ 이상한 출력 / 시스템 프롬프트 무시

일부 모델은 system role을 지원하지 않습니다. `--raw` 플래그로 user role에 프롬프트를 전달:

```bash
cat article.txt | fabric -p summarize --raw
```

### ❌ `DEFAULT_VENDOR=LM Studio` 설정 후에도 다른 벤더가 사용됨

`.env` 파일에서 `DEFAULT_VENDOR` 값 앞뒤 공백 및 따옴표 없음을 확인:

```dotenv
# 올바름
DEFAULT_VENDOR=LM Studio

# 잘못됨 (따옴표 포함하면 안 됨)
DEFAULT_VENDOR="LM Studio"
```

### ❌ `fabric --listmodels` 에서 LM Studio 모델이 보이지 않음

LM Studio에 모델이 로드(다운로드)되어 있어야 합니다. 앱에서 모델을 먼저 다운로드하세요.

### ❌ 응답이 매우 느림

- 로드된 모델이 너무 큰 경우 경량 모델(Phi-4-mini 등)로 교체
- LM Studio 앱 설정에서 GPU 레이어 수(`GPU Layers`) 늘리기 (GPU 있는 경우)
- 컨텍스트 길이(`Context Length`) 줄이기

---

## 9. 참고 자료

| 자료 | 링크 |
|------|------|
| Fabric GitHub | [danielmiessler/fabric](https://github.com/danielmiessler/fabric) |
| LM Studio 공식 사이트 | [lmstudio.ai](https://lmstudio.ai) |
| LM Studio OpenAI 호환 API 문서 | [lmstudio.ai/docs/developer/openai-compat](https://lmstudio.ai/docs/developer/openai-compat) |
| Fabric PR #1302 (LM Studio 네이티브 지원 추가) | [github.com/danielmiessler/fabric/pull/1302](https://github.com/danielmiessler/fabric/pull/1302) |
| Fabric Discussion #857 (LM Studio 사용 팁) | [github.com/danielmiessler/fabric/discussions/857](https://github.com/danielmiessler/fabric/discussions/857) |
| Fabric 패턴 라이브러리 | [fabric/patterns](https://github.com/danielmiessler/fabric/tree/main/patterns) |

---

> **관련 스킬**: [fabric SKILL.md](../../.god-skills/fabric/SKILL.md) · [oh-my-gods README](../../README.md)
