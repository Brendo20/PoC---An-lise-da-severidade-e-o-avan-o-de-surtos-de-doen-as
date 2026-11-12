"""Cliente Groq limitado; chave em memória, sem credenciais em logs ou URLs."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

MODEL = "openai/gpt-oss-20b"
ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"


class ProviderError(RuntimeError):
    def __init__(self, code: str, status: int | None = None, provider_code: str | None = None):
        super().__init__(code)
        self.code, self.status, self.provider_code = code, status, provider_code

    def diagnostic(self) -> dict:
        return {"http_status": self.status, "provider_code": self.provider_code}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class GroqClient:
    def __init__(self, key: str | None = None, model: str | None = None, opener=None):
        self.key = os.environ.get("GROQ_API_KEY", "") if key is None else key
        self.model = model or os.environ.get("GROQ_MODEL", MODEL)
        self.opener = opener or urllib.request.build_opener(NoRedirect()).open

    @property
    def configured(self) -> bool:
        return bool(self.key) and self.model == MODEL

    def complete(self, messages: list, *, tools: list | None = None, schema: dict | None = None) -> dict:
        if not self.configured:
            raise ProviderError("provider_not_configured")
        if len(json.dumps(messages, ensure_ascii=False)) > 28000:
            raise ProviderError("context_limit")
        payload = {"model": self.model, "messages": messages, "temperature": 0.1,
                   "max_completion_tokens": 1800, "reasoning_effort": "low"}
        if tools:
            # GPT-OSS na Groq suporta ferramentas, mas não chamadas paralelas.
            if len(tools) != 1:
                raise ProviderError("invalid_tool_configuration")
            payload.update(tools=tools, tool_choice={"type": "function", "function": {
                "name": tools[0]["function"]["name"]}}, parallel_tool_calls=False)
        if schema is not None:
            payload["response_format"] = {"type": "json_schema", "json_schema": {
                "name": "srag_report", "strict": True, "schema": schema}}
        request = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(), headers={
            "Authorization": "Bearer " + self.key, "Accept": "application/json",
            "Content-Type": "application/json", "User-Agent": "indicium-srag-poc/0.1"})
        try:
            with self.opener(request, timeout=25) as response:
                raw = response.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                raise ProviderError("response_limit")
            result = json.loads(raw)
            choice = result["choices"][0]
            message = choice["message"]
            if choice.get("finish_reason") not in ("stop", "tool_calls"):
                raise ProviderError("incomplete_response")
            # Descartar campos de raciocínio interno, mesmo que o provedor os retorne.
            return {"message": {key: message[key] for key in ("role", "content", "tool_calls") if key in message},
                    "usage": {key: result.get("usage", {}).get(key, 0)
                              for key in ("prompt_tokens", "completion_tokens", "total_tokens")},
                    "response_id": str(result.get("id", ""))[:120]}
        except urllib.error.HTTPError as error:
            # Não guardar mensagem bruta/failed_generation: podem conter prompts ou raciocínio.
            provider_code = None
            try:
                details = json.loads(error.read(8192)).get("error", {})
                candidate = details.get("code") if isinstance(details, dict) else None
                if candidate in ("tool_use_failed", "json_validate_failed", "model_not_found",
                                 "context_length_exceeded", "rate_limit_exceeded", "invalid_api_key"):
                    provider_code = candidate
            except (ValueError, TypeError, AttributeError, OSError):
                pass
            code = {401: "authentication_error", 403: "permission_error", 429: "rate_limit"}.get(
                error.code, f"provider_http_{error.code}")
            raise ProviderError(code, error.code, provider_code) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise ProviderError("provider_connection_error") from None
        except (ValueError, KeyError, IndexError, TypeError):
            raise ProviderError("invalid_provider_response") from None
