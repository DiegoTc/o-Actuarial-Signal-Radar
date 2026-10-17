"""Remote vLLM OpenAI-compatible chat; endpoint configuration is not AMD proof."""
from investigation.http import send,json_body
from investigation.models import ProviderError
from investigation.io import strict_json


class AMDVLLMClient:
    def request_options(self):
        return {}

    def response_format(self, response_schema):
        return {'type':'json_schema','json_schema':{'name':'actuarial_investigation','strict':True,'schema':response_schema}}

    def __init__(self,settings,transport=None):
        self.settings,self.transport=settings,transport

    def complete(self,messages,response_schema):
        s=self.settings
        headers={'Content-Type':'application/json'}
        if s.api_key:headers['Authorization']='Bearer '+s.api_key
        request={'model':s.model,'messages':messages,'temperature':0,'max_tokens':s.max_tokens,'stream':False,
                 'response_format':self.response_format(response_schema)}
        request.update(self.request_options())
        raw,headers_out=send(s.base_url+'/chat/completions',method='POST',headers=headers,body=json_body(request),
                             timeout=s.timeout_seconds,transport=self.transport)
        try:
            data=strict_json(raw)
            choice=data['choices'][0]
            content=choice['message']['content']
            if not isinstance(content,str):raise ValueError('Non-text completion')
            metadata={'response_model':data.get('model'),'finish_reason':choice.get('finish_reason'),
                      'request_id':headers_out.get('x-request-id') or headers_out.get('X-Request-Id'),
                      'usage':data.get('usage'), 'original_transport_response':raw}
            return content,metadata
        except (ValueError,KeyError,IndexError,TypeError):
            error=ProviderError('Malformed OpenAI-compatible response envelope')
            error.raw_response=raw
            raise error from None


class AMDTokenFactoryClient(AMDVLLMClient):
    """Shared AMD gateway: JSON-object mode, followed by the full local schema validator.

    Qwen's shared route does not guarantee strict JSON-schema generation. Never
    misrepresent this service as a project-provisioned vLLM/GPU instance.
    """
    def response_format(self, response_schema):
        return {'type':'json_object'}

    def request_options(self):
        # Qwen defaults to xhigh reasoning on the shared gateway. Bound demo latency
        # explicitly using the documented cross-model supported low setting.
        return {'reasoning_effort':'low' if self.settings.model.startswith('Qwen') else 'none'}


def matches_token_factory_model(served, requested):
    """Verified gateway prefixes the response model with its catalog provider ID."""
    return served in {requested, 'self-dploy/'+requested}
