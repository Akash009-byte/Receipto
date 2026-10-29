# Validation

17 HTTP integration checks passed on Python 3.12 with local test storage. Tests use isolated test database names and no cloud credentials.


Checks:

- OpenAPI
- Readiness
- Create spreadsheet record
- Read spreadsheet
- Update spreadsheet
- Activate spreadsheet
- Current spreadsheet
- Google worksheet requires configuration
- Create worksheet
- Activate worksheet
- Read worksheet
- Update worksheet
- Duplicate spreadsheet rejected
- Delete spreadsheet
- Deleted spreadsheet returns 404
- Discord status without credentials
- Discord send unavailable without credentials

Run again after installing requirements.lock.txt:

```sh
.venv/bin/python tests/smoke.py
```

Mongo projects require a local MongoDB server (default port 27017; override TEST_MONGO_PORT for tests). Keep the backend stopped on port 18510 before testing. Live OpenAI, AWS, Discord and Google Sheets integrations require valid credentials and remain unverified.
