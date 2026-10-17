FROM python:3.12-slim-bookworm@sha256:54c85f3c47607a77f32adec749d3c81d1348bf25833671f512b26a9b6d778cb3
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY scripts/ scripts/
COPY actuarial-engine/ actuarial-engine/
COPY config/ config/
COPY schemas/ schemas/
COPY amd/ amd/
COPY docs/ docs/
COPY evolus/ evolus/
COPY tests/ tests/
COPY pytest.ini .
CMD ["python", "scripts/profile_cnbs.py", "--help"]
