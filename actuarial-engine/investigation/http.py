"""Bounded HTTP transport with explicit errors, no hidden retries or redirects."""
import json
import socket
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler
from investigation.models import ProviderError
from investigation.io import strict_json

MAX_RESPONSE_BYTES=2_000_000


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # do not forward provider credentials to redirected hosts


def send(url,method='GET',headers=None,body=None,timeout=60,transport=None):
    request=Request(url,data=body,headers=headers or {},method=method)
    opener=transport or build_opener(NoRedirect()).open
    try:
        with opener(request,timeout=timeout) as response:
            raw=response.read(MAX_RESPONSE_BYTES+1)
            if len(raw)>MAX_RESPONSE_BYTES: raise ProviderError('Provider response exceeds size limit')
            return raw.decode('utf-8'),dict(response.headers)
    except HTTPError as exc:
        raise ProviderError(f'Provider HTTP error {exc.code}') from None
    except (URLError,TimeoutError,socket.timeout,OSError,UnicodeError) as exc:
        # Never include request headers, secrets or server error bodies in logs.
        raise ProviderError('Provider timeout or transport/encoding failure') from None


def json_body(value):return json.dumps(value,ensure_ascii=False,allow_nan=False).encode('utf-8')
