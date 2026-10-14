.PHONY: build download profile prepare test evidence monthly
build:
	docker compose build
download:
	docker compose run --rm app python scripts/download_cnbs.py
profile:
	docker compose run --rm app python scripts/profile_cnbs.py
prepare:
	docker compose run --rm app python scripts/prepare_cnbs.py
test:
	docker compose run --rm app pytest
evidence:
	docker compose run --rm app python scripts/fetch_cnbs_semantics_evidence.py
monthly:
	docker compose run --rm app python scripts/derive_cnbs_monthly.py
