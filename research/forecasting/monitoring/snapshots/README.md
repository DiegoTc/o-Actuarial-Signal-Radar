# Snapshot registry

Version only compact registration manifests here. Full raw bytes, source receipts, documentary metadata and derivation files live in the Git-ignored storage configured in `../config.json`.

Every registry manifest names an explicit snapshot and binds raw and derived hashes. Original download time is preserved separately from registration time. Never use a mutable `latest` pointer, overwrite a snapshot, or copy raw CSV files into this public directory. Two byte-identical copies are one vintage, not revision evidence.
