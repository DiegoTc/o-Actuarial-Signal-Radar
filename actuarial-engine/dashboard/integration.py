"""Expose verified saved integration evidence, never secrets or configured-only claims."""
import hashlib
import json


def integration_status(root):
    pending = {'amd_status':'NOT_CONFIGURED','evolus_status':'CONFIGURED_PRE_AMD'}
    try:
        deployment=json.loads((root/'evolus/token_factory_deployment.json').read_text())
        if deployment.get('model_step')=='LlmCall' and deployment.get('model_key','').startswith('own/'):
            pending={'amd_status':'CONFIGURED','evolus_status':'CONFIGURED','model_provider':'amd_token_factory',
                'model_name':deployment['model_id']}
    except (OSError,ValueError,KeyError,TypeError):pass
    try:
        receipt = json.loads((root/'reports/investigations/token-factory/verification.json').read_text())
        if receipt['provider'] != 'amd_token_factory' or receipt['status'] != 'VERIFIED': return pending
        for case in ['market_claims_2025_09','market_ratio_2025_03']:
            record = receipt['cases'][case]
            path = root/'data/processed/investigations'/f'{case}.json'
            if record['validation_status'] != 'PASS' or record['human_review_required'] is not True or not record['execution_id']:
                return pending
            if hashlib.sha256(path.read_bytes()).hexdigest() != record['saved_package_file_sha256']: return pending
        return {'amd_status':'VERIFIED','evolus_status':'VERIFIED','model_provider':'amd_token_factory',
                'model_name':receipt['model'],'integration_verified_at':receipt['verified_at']}
    except (OSError,ValueError,KeyError,TypeError): return pending
