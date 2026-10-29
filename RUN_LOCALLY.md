# Run locally

Use **Python 3.12** and **Node.js 22+** (npm). From this repository directory:

```sh
python3.12 dev.py
```

The launcher installs tested Python dependencies in `.venv`, creates a private `app/.env` from the example when missing, and starts services on loopback only. Ctrl+C stops them. By default SQLite data persists in `app/receipto.db`. Set `POSTGRESQL_DB_URL` to use PostgreSQL instead; apply Alembic migrations to that database before use.

API docs are at http://127.0.0.1:5000/docs.

## Integrations

Configure your own credentials in `app/.env`. OpenAI, Discord, Google Sheets, and AWS features require their respective credentials and permissions. Blank values leave those integrations unconfigured; local data functionality can still run. No credentials are included. Do not commit `.env`, credentials JSON, generated databases, or private keys.

This is a local development setup, not a public deployment. AgentOps cloud operations and Receipto integration routes should only be exposed behind authentication and authorization.
