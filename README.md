# Receipto

A FastAPI receipt-processing service with spreadsheet and worksheet records, optional Discord ingestion, OpenAI receipt extraction and Google Sheets synchronization.

## Local start

Requires Python 3.12.

```sh
python3.12 dev.py
```

See [RUN_LOCALLY.md](RUN_LOCALLY.md) for storage, configuration and port details. The launcher uses isolated dependencies and persistent local data.

## Verification

[VALIDATION.md](VALIDATION.md) lists the passing integration tests and how to rerun them.

## External services

Supply your own credentials in `app/.env` for the integrations you enable. Cloud integrations have not been validated against live accounts. The launcher binds to localhost for development; public deployment requires authentication, authorization and an appropriate deployment configuration.

SQLite is the default local database; PostgreSQL remains supported through POSTGRESQL_DB_URL. Worksheet creation defaults to Google synchronization. Pass `sync_google: false` explicitly for local-only worksheet records.

[Original project notes and attribution](docs/original-project-notes.md).
