# Reddit AI Analyzer 🤖

An intelligent Reddit data fetcher and analyzer that uses AI to extract insights from Reddit posts and comments. Runs as a web application with manual and scheduled analysis, plus Telegram integration.

## 📋 Features

- **Manual & Scheduled Analysis**: Run on-demand or set daily automatic analysis
- **Multi-Subreddit Fetching**: Analyze multiple subreddits in one run
- **Intelligent Comment Analysis**: Collect and analyze top comments and replies
- **Email Newsletter Integration**: Include AI newsletters from Gmail in analysis
- **AI-Powered Insights**: Use Gemini or OpenAI models for deep analysis
- **Advanced Generation Control**: Fine-tune temperature, tokens, top-p, top-k, and reasoning budget
- **Text-to-Speech**: Generate audio narration with multiple ElevenLabs voices and custom tones
- **Telegram Integration**: Get results delivered directly to Telegram
- **Docker Containerized**: Easy deployment with Docker Compose
- **Modern Web UI**: Clean Gradio interface with scrollable prompts
- **Persistent Scheduling**: Survives container restarts
- **Comprehensive Logging**: Integrated with Logfire for debugging
- **LLM Input Tracking**: Saves exact prompts sent to AI for transparency

## 🚀 What This Tool Does

The Reddit AI Analyzer provides two main workflows:

### Manual Analysis (On-Demand)
1. **📝 Configure**: Set subreddits, time filter, and AI parameters in UI
2. **▶️ Run**: Click "Run Analysis Now"
3. **⏳ Fetch**: Retrieves posts and comments from Reddit
4. **📧 Email** (Optional): Fetches AI newsletters from Gmail
5. **🧠 Analyze**: AI processes data based on your criteria
6. **🎙️ Audio** (Optional): Generates TTS narration
7. **💾 Save**: Creates timestamped analysis files in run folders
8. **📱 Notify**: Optionally sends to Telegram

### Scheduled Analysis (Automated)
1. **⏰ Configure**: Set daily time and analysis parameters
2. **✅ Enable**: Activate the schedule
3. **🤖 Automatic**: Runs daily at specified time
4. **📱 Deliver**: Always sends results to Telegram

### Target Use Cases
- Stay updated on AI/ML trends and research
- Monitor specific subreddit discussions daily
- Feed insights into NotebookLM or other tools
- Track community sentiment and emerging topics
- Analyze AI newsletters alongside community discussions

## 🛠️ Installation Guide

### Prerequisites

- **Docker & Docker Compose** (Required)
- **Reddit API credentials** (Required)
- **Telegram Bot Token & Chat ID** (Required)
- **AI API Key** (Gemini or OpenAI - Required)
- **Gmail credentials** (Optional - for email newsletters)

### Step 1: Install Docker

#### On Linux:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER
```

#### On macOS:
Download and install Docker Desktop from https://www.docker.com/products/docker-desktop

#### On Windows:
Download and install Docker Desktop from https://www.docker.com/products/docker-desktop

### Step 2: Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/lukaLLM/RedditPodcast.git
cd RedditPodcast/Agent_1/News_agent

# Create necessary directories
mkdir -p outputs data

# Create .env file
touch .env
```

## 🔑 API Keys Setup

### Reddit API Credentials

1. **Go to Reddit Apps**: https://www.reddit.com/prefs/apps
2. **Create New App**:
   - Click "Create App" or "Create Another App"
   - Choose "script" type
   - Name: `reddit-ai-analyzer`
   - Description: `AI-powered Reddit analyzer`
   - Redirect URI: `http://localhost:8080` (required but not used)
3. **Get Credentials**:
   - **Client ID**: String under app name (e.g., `abc123xyz`)
   - **Client Secret**: Secret key shown after creation

### Telegram Bot Setup

#### Create Bot
1. Open Telegram, search for **@BotFather**
2. Send: `/newbot`
3. Follow prompts to choose name and username
4. Copy the **bot token** (e.g., `123456789:ABCdefGHIjklMNOpqr`)

#### Get Chat ID
1. Search for **@userinfobot** on Telegram
2. Send any message
3. Copy your **chat ID** (a number like `123456789`)

### AI API Keys

#### For Gemini (Google):
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

#### For OpenAI:
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key

### Logfire Token (Optional - For Debugging)

1. **Visit**: https://logfire.pydantic.dev/
2. **Sign up/Login** with GitHub
3. **Create Project**: Name it `reddit-analyzer`
4. **Get Token**: Copy the write token

### Environment Variables Setup

Create a `.env` file in the project root:

```env
# Reddit API Credentials (REQUIRED)
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here

# Telegram (REQUIRED)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# AI API Key (REQUIRED - choose one or both)
GOOGLE_API_KEY=your_google_api_key_here      # For Gemini models
OPENAI_API_KEY=your_openai_api_key_here      # For OpenAI models

# ElevenLabs (OPTIONAL - for Text-to-Speech)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Email Integration (OPTIONAL - for newsletters)
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993

# Logfire Token (OPTIONAL - for debugging)
LOGFIRE_TOKEN=your_logfire_token_here
```

## ⚙️ Configuration

### TimeFilter Options

Controls the time period for fetching top posts:

| Filter | Description |
|--------|-------------|
| `hour` | Top posts from last hour |
| `day` | Top posts from last 24 hours |
| `week` | Top posts from last 7 days |
| `month` | Top posts from last 30 days |
| `year` | Top posts from last year |
| `all` | Top posts of all time |

### Subreddit Configuration Format

```
SubredditName:PostLimit, SubredditName2:PostLimit, ...
```

**Examples:**
```
LocalLLaMA:10, artificial:5, MachineLearning:2
```
- Fetches 10 posts from r/LocalLLaMA
- Fetches 5 posts from r/artificial
- Fetches 2 posts from r/MachineLearning

### Default Configuration (in config.py)

```python
# Subreddit configuration: {subreddit_name: post_limit}
DEFAULT_SUBREDDIT_CONFIG = {
    "LocalLLaMA": 10,
    "artificial": 5,
    "MachineLearning": 2,
    "OpenAI": 2,
    "AI_Agents": 2,
    "ArtificialInteligence": 5
}

# Comment and reply limits
DEFAULT_TOP_COMMENTS = 10       # Max comments per post
DEFAULT_REPLIES_PER_COMMENT = 5 # Max replies per comment

# Time filter
DEFAULT_TIME_FILTER = TimeFilter.DAY

# AI Model
DEFAULT_MODEL = "gemini-2.5-pro"

# TTS Settings
DEFAULT_TTS_MODEL = "gemini-2.5-flash-preview-tts"
DEFAULT_VOICE = "Sadaltager"  # Available: Jessica, Rachel, Callum, Charlie

# Schedule defaults
DEFAULT_SCHEDULE_HOUR = 7    # 7 AM
DEFAULT_SCHEDULE_MINUTE = 0  # :00

# Email defaults
DEFAULT_EMAIL_HOURS = 48     # Look back 2 days
DEFAULT_MAX_EMAILS = 10      # Max per sender
```

### Custom Analysis Criteria

Default prompts in `config.py`:

You can also change them there and model parameters

**Customize these in the UI or modify defaults in config.py**

### Email Newsletter Integration

Analyze AI newsletters alongside Reddit data for comprehensive insights.

**Setup Steps:**

1. **Enable IMAP** in Gmail:
   - Go to Gmail Settings → Forwarding and POP/IMAP
   - Enable IMAP access

2. **Create App Password**:
   - Visit: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password
   - Use this as `EMAIL_PASSWORD` (NOT your regular password)

3. **Add to .env**:
```env
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
```

4. **Configure in UI**:
   - Check "📬 Fetch & Analyze AI News Emails"
   - Enter allowed senders (comma-separated):
     ```
     thebatch@deeplearning.ai, newsletter@openai.com, news@anthropic.com
     ```
   - Set max emails per sender (1-200)
   - Set hours back to search (24-8760)

**Features:**
- Fetches from specific senders only
- Cleans HTML and removes URLs/navigation
- Combines with Reddit data for unified analysis
- Saves raw emails to separate JSON file

## 🎯 Usage

### Step 1: Start the Application

```bash
# From project root
docker compose -f docker/docker-compose.yml up -d --build

# Or from docker directory
cd docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Step 2: Access the Web Interface

Open your browser: **http://localhost:7860**

### Manual Analysis (One-Time)

1. Go to **📊 Manual Analysis** tab
2. Configure Reddit settings:
   - **Subreddit Configuration**: `LocalLLaMA:10, artificial:5`
   - **Time Filter**: Choose period (day, week, etc.)
   - **Top Comments**: Number per post (1-10)
   - **Replies per Comment**: Number per comment (1-5)
3. Configure AI settings:
   - **AI Model**: Select model (gemini-2.0-flash-thinking-exp-01-21, openai:gpt-4o, etc.)
   - **System Prompt**: Analysis framework (scrollable textbox)
   - **User Prompt**: What to look for (scrollable textbox)
   - **Advanced**: Adjust tokens, temperature, top-p, top-k, thinking budget
4. Optional features:
   - **📱 Send to Telegram**: Get results in Telegram
   - **🎙️ Generate Audio**: TTS narration with voice/tone controls
   - **📧 Fetch Emails**: Include newsletters (configure senders, hours, max emails)
5. Click: **▶️ Run Analysis Now**
6. Wait for completion (2-5 minutes)
7. Download files or view in UI

### Scheduled Analysis (Automated)

1. Go to **⏰ Scheduler** tab
2. Configure schedule:
   - **Hour**: 24-hour format (0-23)
   - **Minute**: 0-59
   - **Timezone**: Your timezone (e.g., `America/New_York`)
3. Configure all analysis settings (same options as Manual)
4. Click: **✅ Enable Schedule**
5. Check status to see next run time
6. Results automatically sent to Telegram

**Important**: Container must be running for scheduled jobs!

## 🏗️ Project Structure

```
News_agent/
├── app.py                      # Gradio web interface
├── scheduler.py                # Background scheduler with persistence
├── workflow.py                 # Main analysis orchestration
├── reddit_fetcher.py           # Reddit API integration
├── ai_analyzer.py              # AI analysis with PydanticAI
├── telegram_sender.py          # Telegram bot integration
├── email_fetcher.py            # Gmail IMAP email fetcher
├── tts_generator.py            # ElevenLabs TTS generation
├── config.py                   # Configuration and defaults
├── utils.py                    # Helper functions
├── pyproject.toml              # Python dependencies (uv package manager)
├── .env                        # Environment variables (git ignored)
├── docker/
│   ├── Dockerfile              # Docker image definition
│   └── docker-compose.yml      # Docker Compose configuration
├── docs/
│   └── README.md               # This file
├── outputs/                    # Analysis output folders
│   └── run_YYYY-MM-DD_HH-MM-SS/
│       ├── analysis.txt
│       ├── raw_data.txt
│       ├── llm_input.txt
│       ├── emails.json
│       └── audio.wav
└── data/
    └── schedule_config.json    # Persistent schedule state
```

### Component Overview

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `app.py` | Web UI | Gradio interface with Manual & Scheduler tabs, scrollable prompts |
| `scheduler.py` | Automation | APScheduler, timezone support, JSON persistence |
| `workflow.py` | Orchestration | Coordinates Reddit → Email → AI → TTS → Telegram pipeline |
| `reddit_fetcher.py` | Reddit | AsyncPRAW, rate limiting, comment/reply fetching |
| `ai_analyzer.py` | AI Analysis | PydanticAI with Gemini/OpenAI, Logfire instrumentation |
| `email_fetcher.py` | Emails | IMAP connection, HTML cleaning, sender filtering |
| `tts_service.py` | Audio | Gemini TTS with multiple voices and tone control |
| `telegram_sender.py` | Notifications | Messages, file uploads, error handling |
| `config.py` | Settings | Defaults, enums (TimeFilter, TTSModel, Voice) |
| `utils.py` | Utilities | File I/O, parsing, run folder management |

### Key Dependencies (pyproject.toml)


## 🐛 Troubleshooting

### Common Issues

#### Container won't start
```bash
# View logs
docker-compose logs

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🙋‍♂️ Support

- **Issues**: Open a GitHub issue for bugs or feature requests
- **YouTube**: AI tech tutorials at https://www.youtube.com/@LukaszGawendaAI
- **Documentation**: This README and inline code comments
- **Logs**: Check `docker-compose logs -f` for troubleshooting

## 📝 License

MIT License - See LICENSE file for details

---

**Built with ❤️ by Lukasz Gawenda** | Powered by PydanticAI, Gemini