"""Provider settings and shared constants; no analytical configuration."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol
import os
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
CONFIGURATION_VERSION = 'investigation-v1'
PROMPT_VERSION = 'evidence-investigation-v1'
SIGNAL_SCHEMA_VERSION = 'investigation-signal-v1'
RESPONSE_SCHEMA_VERSION = 'investigation-response-v1'
CASE_PATTERN = r'^(market|institution_[0-9]{4})_(claims|premiums|ratio)_[0-9]{4}_[0-9]{2}$'


class ProviderError(RuntimeError):
    """Remote failure; callers must not silently fall back to mock."""


def endpoint(value):
    parsed = urlsplit(value)
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('Endpoint must be an HTTP(S) URL without embedded credentials, query or fragment')
    return value.rstrip('/')


@dataclass(frozen=True)
class Settings:
    provider: str = 'mock'
    language: str = 'en'
    base_url: str = ''
    model: str = 'deterministic-placeholder-v1'
    api_key: str = field(default='', repr=False)
    timeout_seconds: float = 60
    max_tokens: int = 2500

    @classmethod
    def from_env(cls, provider=None, language=None, environ=None):
        env = os.environ if environ is None else environ
        chosen = provider or env.get('INVESTIGATION_PROVIDER') or 'mock'
        lang = language or env.get('INVESTIGATION_LANGUAGE') or 'en'
        if chosen not in {'mock', 'amd_vllm', 'amd_token_factory'} or lang not in {'en','es'}:
            raise ValueError('Use provider mock/amd_vllm/amd_token_factory and language en/es')
        timeout = float(env.get('INVESTIGATION_TIMEOUT_SECONDS') or 60)
        tokens = int(env.get('INVESTIGATION_MAX_TOKENS') or 2500)
        if not 0 < timeout <= 300 or not 128 <= tokens <= 16384:
            raise ValueError('Timeout must be in (0,300]; max_tokens in [128,16384]')
        base, model, secret = '', 'deterministic-placeholder-v1', ''
        if chosen in {'amd_vllm', 'amd_token_factory'}:
            prefix = 'AMD_TOKEN_FACTORY' if chosen == 'amd_token_factory' else 'AMD_VLLM'
            base = env.get(prefix+'_BASE_URL','').strip()
            model = env.get(prefix+'_MODEL','').strip()
            if not base or not model:
                raise ValueError(chosen+' requires '+prefix+'_BASE_URL and '+prefix+'_MODEL')
            base = endpoint(base)
            if not base.endswith('/v1'):
                raise ValueError(prefix+'_BASE_URL must end in /v1')
            secret = env.get(prefix+'_API_KEY','')
            if chosen == 'amd_token_factory' and (not secret or not base.startswith('https://')):
                raise ValueError('Token Factory requires HTTPS and AMD_TOKEN_FACTORY_API_KEY')
        return cls(chosen,lang,base,model,secret,timeout,tokens)


class ModelProvider(Protocol):
    def complete(self, messages: list[dict], response_schema: dict) -> tuple[str, dict]: ...
