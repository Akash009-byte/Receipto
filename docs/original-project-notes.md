# Receipto

Start locally with **Python 3.12** and Node.js 22+: `python3.12 dev.py`. See [RUN_LOCALLY.md](RUN_LOCALLY.md) for setup and [VALIDATION.md](VALIDATION.md) for tested behavior.

SQLite is the default local database. Worksheet creation defaults to Google synchronization; pass `sync_google: false` for an explicit local-only record. Cloud integrations require your own credentials.

# receipto prototype

This is a fastapi prototype generated using WeDAA, you can find documentation and help at [WeDAA Docs](https://www.wedaa.tech/docs/introduction/what-is-wedaa/)

## Features

- 📝 **Note Management**: Create, read, and delete notes via REST API
- 🤖 **Discord Integration**: Bot that monitors messages and processes images
- 🧾 **AI Receipt Processing**: Automatically extract data from receipt images using OpenAI GPT-4 Vision
- 📸 **Image Download**: Automatically download and store receipt images
- 🔍 **Smart Detection**: Recognizes receipt images and processes them with AI
- 📊 **Google Sheets Integration**: Connect to and manage Google Spreadsheets and worksheets

## Prerequisites

- python version >= 3
- OpenAI API Key (for receipt processing)
- Discord Bot Token (for Discord integration)
- Google Service Account (for Google Sheets integration)

## Environment Variables

Create a `.env` file in the root directory with:

```bash
# Server Configuration
SERVER_PORT=5000

# Database Configuration
POSTGRESQL_DB_URL=postgresql+asyncpg://receipto@localhost:5432/receipto

# Application Configuration
APP_NAME=receipto

# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DUMP_CHANNEL_ID=your_dump_channel_id_here

# AI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google Sheets Configuration
GOOGLE_SHEETS_API_KEY=your_google_sheets_api_key_here
```

## Project Structure

```
receipto/
├── app/                          # Main application
│   ├── ai_agents/               # AI processing modules
│   │   ├── receipt_processor.py # OpenAI GPT-4 Vision integration
│   │   └── image_downloader.py  # Image download utilities
│   ├── discord_bot/             # Discord bot integration
│   │   ├── bot.py              # Core Discord bot
│   │   ├── message_events.py   # Message event handlers
│   │   └── config.py           # Discord configuration
│   ├── api/routes/             # REST API endpoints
│   ├── services/               # Business logic
│   ├── models/                 # Data models
│   └── core/                   # Core functionality
├── dump/                       # Downloaded receipt images
└── docker/                     # Docker configurations
```

## Dependencies

This application is configured to work with external component(s).

Docker compose files are provided for the same to get started quickly.

Component details:

- Postgresql DB: `docker compose -f docker/postgresql.yml up -d`

On launch, receipto will refuse to start if it is not able to connect to any of the above component(s).

## Get Started

Run the `./start.sh` script to quickly get started.

Or

Manually Step:

1. Create a new virtual env

```
python -m venv .venv
```

2. Activate the virtual environment

```
source .venv/bin/activate
```

3. Install the requirements for project

```
pip install -r requirements.txt
```

4. Enter the `app/` directory, Run the FastAPI application:

```
gunicorn -c gunicorn_dev_config.py main:app
```

Open [http://localhost:5000/management/health/readiness](http://localhost:5000/management/health/readiness) to view it in your browser.

## Discord Receipt Processing

1. **Upload Receipt Images**: Simply upload receipt images to any Discord channel your bot can see
2. **Automatic Processing**: The bot will automatically:
   - Download the image to the `dump/` folder
   - Process it with OpenAI GPT-4 Vision
   - Extract vendor, date, items, total, and other details
   - Send formatted results back to Discord
3. **Supported Formats**: PNG, JPG, JPEG, GIF, BMP, WebP

### Example Discord Interaction:

```
User: [uploads receipt image]
Bot: 🤖 Processing receipt with AI... Please wait!

🧾 Receipt Processed Successfully!

📋 Details:
• Vendor: Walmart
• Date: 2024-01-15
• Total: $45.67
• Items: 8 item(s)
• File: receipt.jpg

✅ Status: Valid

📝 Items:
1. Milk - $3.99
2. Bread - $2.50
3. Eggs - $4.25
... and 5 more items
```

## API Endpoints

### Notes
- `POST /api/notes` - Create new note
- `GET /api/notes` - Get all notes
- `GET /api/notes/{id}` - Get specific note
- `DELETE /api/notes/{id}` - Delete note

### Discord
- `GET /api/discord/status` - Check Discord connection
- `POST /api/discord/send` - Send message to Discord

### Health
- `GET /management/health/readiness` - Readiness probe
- `GET /management/health/liveness` - Liveness probe

## Containerization

Build the docker image: `docker build -t receipto:latest .`

Start the container: `docker run -d -p 5000:5000 receipto:latest`


-----------------------------------------------------------------------
1. System-Level Certificate Installation
You likely ran the certificate installation command earlier:

```
/Applications/Python\ 3.12/Install\ Certificates.command
```

This command installed proper SSL certificates at the system level for Python 3.12, which means:
✅ Python now has valid SSL certificates
✅ All Python SSL connections work properly
✅ discord.py can connect to Discord servers
✅ No code-level SSL workarounds needed


https://discordpy.readthedocs.io/en/latest/api.html#messages




------- Look Back --------

-  dump url : https://docs.google.com/spreadsheets/d/1YSgdqLgidZzbO8BWTFKv2UXTJoGg0mJztojwqfLKDEI/edit?gid=1567367503#gid=1567367503

- Google cloud service account: https://console.cloud.google.com/iam-admin/serviceaccounts/details/116513248936289155545/keys?invt=Ab66Tg&project=wedaa-dev


- Discord Resources:
   - https://discordpy.readthedocs.io/en/latest/api.html#messages
   - https://discord.com/developers/docs/resources/message#message-object
   - https://dev.to/mannu/3events-in-discordpy-5gcb
   - https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID#h_01HRSTXPS5WGDKT73WADV2HGCH
   - https://discord.com/developers/applications/1398454188849102948/bot
   - https://discord.com/developers/docs/events/gateway
