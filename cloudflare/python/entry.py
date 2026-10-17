"""Minimal Pyodide probe. This is NOT a port of the threaded production API."""
import json
import sys
from workers import Response, WorkerEntrypoint

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        from urllib.parse import urlsplit
        path = urlsplit(request.url).path
        if path == '/probe/https':
            # Connectivity only: no credentials, workflow execution or model usage.
            from js import fetch
            response = await fetch('https://api.evolus.ai/api/v1/memories')
            return Response(json.dumps({'https_reached':True,'upstream_status':response.status,
                'authenticated':False}),headers={'Content-Type':'application/json'})
        if path == '/probe':
            import threading
            try:
                t = threading.Thread(target=lambda: None)
                t.start()
                t.join()
                thread_state = 'functional'
            except Exception as exc:
                thread_state = type(exc).__name__
            return Response(json.dumps({'runtime':'pyodide','python':sys.version.split()[0],
                'threading':thread_state,'api_ported':False}),headers={'Content-Type':'application/json'})
        # Read-only endpoint snapshots are exported by the existing Python normalizer.
        if path in ['/api/summary','/api/signals','/api/cases'] or path.startswith('/api/cases/'):
            from js import Request
            response = await self.env.ASSETS.fetch(Request.new('https://assets.local'+path+'.json'))
            return response
        return Response(json.dumps({'error':'PROBE_ONLY_NO_INVESTIGATION_PORT'}),status=501,headers={'Content-Type':'application/json'})
