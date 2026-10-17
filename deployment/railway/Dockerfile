FROM python:3.12-slim-bookworm@sha256:54c85f3c47607a77f32adec749d3c81d1348bf25833671f512b26a9b6d778cb3
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY deployment/railway/requirements.txt /tmp/runtime-requirements.txt
RUN pip install --no-cache-dir -r /tmp/runtime-requirements.txt
# This context is produced by prepare_bundle.py, never the unrestricted repository.
COPY actuarial-engine/ actuarial-engine/
COPY scripts/ scripts/
COPY schemas/ schemas/
COPY data/ data/
COPY reports/ reports/
COPY docs/ docs/
COPY evolus/ evolus/
COPY deployment/railway/artifact-manifest.json deployment/railway/artifact-manifest.json
USER 65534:65534
CMD ["python", "scripts/serve_dashboard_api.py"]
