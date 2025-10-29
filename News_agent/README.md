# Reddit AI Analyzer 🤖

An intelligent Reddit data fetcher and analyzer that uses AI to extract insights from Reddit posts and comments. Runs as a web application with manual and scheduled analysis, plus Telegram integration.

## 📋 Features

- **Manual & Scheduled Analysis**: Run on-demand or set daily automatic analysis
- **Multi-Subreddit Fetching**: Analyze multiple subreddits in one run
- **Intelligent Comment Analysis**: Collect and analyze top comments and replies
- **AI-Powered Insights**: Use Gemini or OpenAI models for deep analysis
- **Telegram Integration**: Get results delivered directly to Telegram
- **Docker Containerized**: Easy deployment with Docker Compose
- **Modern Web UI**: Clean Gradio interface for configuration
- **Persistent Scheduling**: Survives container restarts
- **Comprehensive Logging**: Integrated with Logfire for debugging

## 🚀 What This Tool Does

The Reddit AI Analyzer provides two main workflows:

### Manual Analysis (On-Demand)
1. **📝 Configure**: Set subreddits, time filter, and AI parameters in UI
2. **▶️ Run**: Click "Run Analysis Now"
3. **⏳ Fetch**: Retrieves posts and comments from Reddit
4. **🧠 Analyze**: AI processes data based on your criteria
5. **💾 Save**: Creates timestamped analysis files
6. **📱 Notify**: Optionally sends to Telegram

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

## 🛠️ Installation Guide

### Prerequisites

- **Docker & Docker Compose** (Required)
- **Reddit API credentials** (Required)
- **Telegram Bot Token & Chat ID** (Required)
- **AI API Key** (Gemini or OpenAI)

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
cd RedditPodcast

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

### Logfire Token (Optional)

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

# AI API Key (REQUIRED - choose one)
GOOGLE_API_KEY=your_google_api_key_here      # For Gemini
OPENAI_API_KEY=your_openai_api_key_here      # For GPT-4

# Logfire Token (OPTIONAL - for debugging)
LOGFIRE_TOKEN=your_logfire_token_here
```

### Environment File Example

```env
# Example .env file
REDDIT_CLIENT_ID=abc123xyz789
REDDIT_CLIENT_SECRET=def456uvw012-XyZ789AbC
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321
GOOGLE_API_KEY=AIzaSyD1234567890abcdefghij
LOGFIRE_TOKEN=lf_1234567890abcdef
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
DEFAULT_MODEL = "gemini-2.5-pro"  # Options: gemini-2.5-pro, openai:gpt-4o, etc.

# Schedule defaults
DEFAULT_SCHEDULE_HOUR = 7    # 7 AM
DEFAULT_SCHEDULE_MINUTE = 0  # :00
```

### Custom Analysis Criteria

Default prompts in `config.py`:

```python
DEFAULT_SYSTEM_PROMPT = """You are a Reddit research analyst...
1. Topic Analysis: Identify the most interesting topics
2. Comments: Select the best comments
3. Key Insights: Extract notable insights and trends
4. Highlight conflicting opinions
5. Summarize concisely with URL links
"""

DEFAULT_USER_PROMPT = """Look for most insightful posts and comments 
that would enrich my knowledge as AI Engineer. Look for New AI models, 
performance benchmarks, ideas for projects, novel ideas/techniques around AI."""
```

**Customize these in the UI or modify defaults in config.py**

## 🎯 Usage

### Step 1: Start the Application

```bash

docker compose -f 'News_agent/docker-compose.yml' up -d --build 'reddit-analyzer' 

# Or inside the News_agent
# Build and start containers
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
2. Configure settings:
   - **Subreddit Configuration**: `LocalLLaMA:10, artificial:5`
   - **Time Filter**: Choose period (day, week, etc.)
   - **Top Comments**: Number per post (1-10)
   - **Replies per Comment**: Number per comment (1-5)
   - **AI Model**: Select model (gemini-2.5-pro, gpt-4o, etc.)
   - **What to Look For**: Your analysis criteria
3. Optional: Enable **📱 Send results to Telegram**
4. Click: **▶️ Run Analysis Now**
5. Wait for completion (2-5 minutes)
6. View results in UI or check `outputs/` folder

### Scheduled Analysis (Automated)

1. Go to **⏰ Scheduler** tab
2. Configure schedule:
   - **Hour**: 24-hour format (0-23)
   - **Minute**: 0-59
   - **Timezone**: Your timezone (e.g., `America/New_York`)
3. Configure analysis settings (same as manual)
4. Click: **✅ Enable Schedule**
5. Check status to see next run time
6. Results automatically sent to Telegram

**Important**: Container must be running for scheduled jobs!

### Advanced Usage Examples

#### 1. Quick Daily AI News
```python
# In UI, set:
Subreddit Config: LocalLLaMA:3, OpenAI:3
Time Filter: day
AI Model: gemini-2.5-flash  # Faster model
Schedule: 08:00 daily
```

#### 2. Deep Weekly Research
```python
# In UI, set:
Subreddit Config: LocalLLaMA:10, MachineLearning:8, artificial:7
Time Filter: week
AI Model: openai:gpt-4o  # Higher quality
Top Comments: 10
Replies: 5
Schedule: Sunday 09:00
```

#### 3. Custom Subreddit Monitoring
```python
# In UI, set:
Subreddit Config: YourNicheSubreddit:15
Time Filter: day
User Prompt: "Focus on [your specific topic]"
```

### Output Files

The tool generates files in `outputs/` directory:

1. **Analysis**: `reddit_analysis_YYYY-MM-DD_HH-MM-SS.txt`
   - AI-generated insights and trends
   - Ready for NotebookLM or content creation

2. **Raw Data**: `reddit_raw_data_YYYY-MM-DD_HH-MM-SS.txt`
   - All fetched posts and comments
   - Useful for manual review or reprocessing

### Rate Limiting

Reddit enforces rate limits (~60 requests/minute):

**Built-in protection:**
- 1-second delays between comment fetches
- Limited post counts per subreddit

**If you hit limits:**
1. Reduce subreddit post limits
2. Use longer time filters (WEEK vs DAY)
3. Wait a few minutes before retrying

### Memory Usage

For large analyses:
- Monitor with: `docker stats reddit-ai-analyzer`
- Reduce `Top Comments` if needed
- Reduce `Replies per Comment` if needed
- Process fewer subreddits per run

## 🏗️ Project Structure

```
reddit-ai-analyzer/
├── app.py                      # Gradio web interface (420 lines)
├── scheduler.py                # Background scheduler (200 lines)
├── workflow.py                 # Orchestrates process (120 lines)
├── reddit_fetcher.py           # Reddit API calls (210 lines)
├── ai_analyzer.py              # AI integration (60 lines)
├── telegram_sender.py          # Telegram notifications (120 lines)
├── config.py                   # Configuration (90 lines)
├── utils.py                    # Helper functions (150 lines)
├── Dockerfile                  # Docker image
├── docker-compose.yml          # Docker Compose config
├── pyproject.toml              # Python dependencies
├── .env                        # Secrets (git ignored)
├── outputs/                    # Analysis files
└── data/
    └── schedule_config.json    # Persistent schedule config
```

### Component Overview

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `app.py` | Web UI | Gradio interface, two tabs (Manual/Scheduler) |
| `scheduler.py` | Automation | Background thread, timezone support, persistence |
| `workflow.py` | Orchestration | Coordinates all steps, error handling |
| `reddit_fetcher.py` | Data collection | Async fetching, rate limiting, formatting |
| `ai_analyzer.py` | AI analysis | PydanticAI integration, Logfire logging |
| `telegram_sender.py` | Notifications | Messages, files, error alerts |
| `config.py` | Configuration | Defaults, enums, constants |
| `utils.py` | Utilities | File I/O, parsing, validation |

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

#### Scheduler not running
```bash
# Check if enabled
docker exec reddit-ai-analyzer cat /app/data/schedule_config.json

# Should show "enabled": true

# Check logs
docker-compose logs -f | grep -i scheduler
```

#### Reddit API errors
```bash
# Verify credentials
docker exec reddit-ai-analyzer env | grep REDDIT

# Rate limiting: wait a few minutes, reduce subreddit limits
```

#### Telegram not sending
```bash
# Test manually
docker exec -it reddit-ai-analyzer python3 << EOF
import asyncio
import os
from telegram import Bot

async def test():
    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
    await bot.send_message(
        chat_id=os.getenv('TELEGRAM_CHAT_ID'),
        text='Test message'
    )

asyncio.run(test())
EOF
```

#### AI analysis fails
```bash
# Check API key
docker exec reddit-ai-analyzer env | grep API_KEY

# Verify model name:
# Gemini: gemini-2.5-pro
# OpenAI: openai:gpt-4o (note the prefix)
```

### Debug Commands

```bash
# View logs
docker-compose logs -f

# Execute shell in container
docker exec -it reddit-ai-analyzer bash

# Check container status
docker-compose ps

# Restart container
docker-compose restart

# Clean rebuild
docker-compose down
docker system prune -a
docker-compose up -d
```

## 🙋‍♂️ Support

- **Issues**: Open a GitHub issue for bugs or feature requests
- **YouTube**: Check out my AI tech channel for tutorials: https://www.youtube.com/@LukaszGawendaAI
- **Documentation**: This README and code comments

## 📝 License

MIT License - See LICENSE file for details