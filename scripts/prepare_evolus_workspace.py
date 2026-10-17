"""Explicit Evolus setup/pre-AMD validation; no AMD endpoint or statistical calculations."""
import sys
from _bootstrap import ROOT
from investigation.evolus_setup import main

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        # ProviderError is sanitized by the shared client. Never print credentials or raw requests.
        from investigation.models import ProviderError
        if isinstance(exc, (ValueError, ProviderError, OSError)):
            print('Evolus preparation failed: '+str(exc), file=sys.stderr)
        else:
            print('Evolus preparation failed: '+type(exc).__name__, file=sys.stderr)
        sys.exit(1)
