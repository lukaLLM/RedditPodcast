# Reddit AI Analyzer 🤖

An intelligent Reddit data fetcher and analyzer that uses AI to extract insights from Reddit posts and comments. This repository contains multiple versions of the tool, from simple command-line scripts to a full-featured web application.

## 📖 What This Tool Does

The Reddit AI Analyzer helps you stay updated on trends and discussions across your favorite subreddits by:

- 🔍 **Fetching** top posts and comments from multiple subreddits
- 🧠 **Analyzing** content using advanced AI models (Gemini, OpenAI)
- 📊 **Extracting** insights, trends, and key information based on your criteria
- 💾 **Saving** analysis results for use with tools like NotebookLM
- 📱 **Delivering** results via Telegram (v2 & v3)
- 🎙️ **Narrating** insights with text-to-speech (v3)
- 📧 **Integrating** AI newsletters from email (v3)

## 🎯 Choose Your Version

This repository contains **three versions** of the Reddit AI Analyzer, each with different capabilities and complexity levels. Choose the one that best fits your needs:

### 📦 Version 1: Basic Analyzer
**Location:** [`News_agent_v1_v2/reddit_search_podcast_v1.py`](./News_agent_v1_v2/)

A simple, standalone Python script for quick Reddit analysis.

**Features:**
- ✅ Fetch posts and comments from multiple subreddits
- ✅ AI-powered analysis using Gemini models
- ✅ Save results to timestamped text files
- ✅ Minimal setup - just needs Reddit and AI API keys

**Best for:** Quick one-time analysis, learning how the tool works, simple scripting

**[→ View v1 Documentation](./News_agent_v1_v2/README.md)**

---

### 📦 Version 2: Telegram-Enabled Analyzer
**Location:** [`News_agent_v1_v2/reddit_search_podcast_v2.py`](./News_agent_v1_v2/)

Enhanced version with Telegram notifications for convenient delivery.

**Features:**
- ✅ All features from Version 1
- ✅ **Telegram bot integration** for result notifications
- ✅ Send analysis directly to your Telegram chat
- ✅ Still a simple standalone script

**Best for:** Regular monitoring with mobile notifications, staying updated on-the-go

**[→ View v2 Documentation](./News_agent_v1_v2/README.md)**

---

### 📦 Version 3: Full-Featured Web Application
**Location:** [`News_agent_v3/`](./News_agent_v3/)

A complete web application with scheduling, email integration, and advanced features.

**Features:**
- ✅ **Web UI** with Gradio interface
- ✅ **Manual & Scheduled Analysis** - run on-demand or set daily automatic runs
- ✅ **Telegram Integration** - get results delivered automatically
- ✅ **Email Newsletter Integration** - fetch and analyze AI newsletters from Gmail
- ✅ **Text-to-Speech** - generate audio narration with ElevenLabs voices
- ✅ **Docker Containerized** - easy deployment with Docker Compose
- ✅ **Persistent Scheduling** - survives container restarts
- ✅ **Advanced AI Controls** - fine-tune temperature, tokens, reasoning budget
- ✅ **Multi-Model Support** - Gemini and OpenAI models
- ✅ **Comprehensive Logging** - integrated with Logfire for debugging

**Best for:** Production use, daily automated monitoring, teams, advanced AI workflows

**[→ View v3 Documentation](./News_agent_v3/docs/README.md)**

---

## 🚀 Quick Start Guide

### For Version 1 (Basic)

```bash
# Clone the repository
git clone https://github.com/lukaLLM/RedditPodcast.git
cd RedditPodcast/News_agent_v1_v2

# Install dependencies
pip install uv
uv sync

# Configure environment variables
cp .env.example .env
# Edit .env with your Reddit API keys

# Run the analyzer
python reddit_search_podcast_v1.py
```

### For Version 2 (Telegram-Enabled)

```bash
# Same as Version 1, but also add Telegram credentials to .env
# TELEGRAM_BOT_TOKEN=your_bot_token
# TELEGRAM_CHAT_ID=your_chat_id

# Run the analyzer
python reddit_search_podcast_v2.py
```

### For Version 3 (Web Application)

```bash
# Clone and navigate to v3
git clone https://github.com/lukaLLM/RedditPodcast.git
cd RedditPodcast/News_agent_v3

# Configure environment
cp .env.example .env
# Edit .env with all required API keys

# Start with Docker
docker compose -f docker/docker-compose.yml up -d

# Access the web interface
# Open browser: http://localhost:7860
```

## 📋 Requirements Overview

| Component | v1 | v2 | v3 |
|-----------|----|----|-----|
| Python 3.12+ | ✅ | ✅ | ✅ |
| Reddit API Keys | ✅ | ✅ | ✅ |
| AI API Key (Gemini/OpenAI) | ✅ | ✅ | ✅ |
| Telegram Bot | ❌ | ✅ | ✅ |
| Docker | ❌ | ❌ | ✅ |
| ElevenLabs (TTS) | ❌ | ❌ | Optional |
| Gmail Account | ❌ | ❌ | Optional |

## 🔑 API Keys You'll Need

All versions require at minimum:

### Reddit API
1. Create app at https://www.reddit.com/prefs/apps
2. Get Client ID and Client Secret
3. Add to `.env` file

### AI API (Choose One or Both)
- **Gemini**: Get key at https://makersuite.google.com/app/apikey
- **OpenAI**: Get key at https://platform.openai.com/api-keys

### Telegram (v2 & v3)
1. Create bot with @BotFather on Telegram
2. Get bot token
3. Get your chat ID from @userinfobot

### Optional (v3 Only)
- **ElevenLabs**: For text-to-speech audio generation
- **Gmail**: For email newsletter integration

**Detailed setup instructions are in each version's README.**

## 📚 Documentation

Each version has comprehensive documentation:

- **[Version 1 & 2 Documentation](./News_agent_v1_v2/README.md)** - Setup and usage for simple scripts
- **[Version 3 Documentation](./News_agent_v3/docs/README.md)** - Complete guide for web application

## 🎓 Use Cases

### For Researchers & Engineers
- Track latest AI/ML developments and research
- Monitor technical discussions and implementations
- Feed insights into NotebookLM or other knowledge tools
- Stay updated on specific technologies or frameworks

### For Community Managers
- Monitor community sentiment and trending topics
- Track discussions across multiple related subreddits
- Automated daily briefings via Telegram

### For Content Creators
- Find trending topics for content ideas
- Generate audio summaries for podcasts
- Track community reactions and feedback
- Discover emerging themes and discussions

## 🛠️ Technology Stack

| Layer | Technologies |
|-------|-------------|
| **AI Models** | Gemini (2.0, 2.5 Flash, Pro), OpenAI (GPT-4o, o1-preview) |
| **AI Framework** | PydanticAI with structured outputs |
| **Reddit API** | AsyncPRAW for async Reddit data fetching |
| **Web Framework** | Gradio for modern web UI (v3) |
| **Scheduling** | APScheduler with timezone support (v3) |
| **Email** | IMAP for Gmail integration (v3) |
| **TTS** | ElevenLabs for audio generation (v3) |
| **Messaging** | Python Telegram Bot API |
| **Containerization** | Docker & Docker Compose (v3) |
| **Package Manager** | uv (modern Python package management) |
| **Logging** | Logfire for observability |

## 🔄 Migration Between Versions

You can easily move between versions as your needs evolve:

**v1 → v2**: Just add Telegram credentials to your `.env` file and switch scripts

**v2 → v3**: 
1. Set up Docker environment
2. Transfer your `.env` configuration
3. Access via web interface instead of command line

## 🤝 Contributing

Contributions are welcome! Whether you:
- Found a bug
- Have a feature request
- Want to improve documentation
- Want to add support for new AI models

Please open an issue or submit a pull request on GitHub.

## 🙋‍♂️ Support & Community

- **GitHub Issues**: Report bugs or request features
- **YouTube Channel**: Tutorials and AI insights at [Lukasz Gawenda AI](https://www.youtube.com/@LukaszGawendaAI)
- **Documentation**: Comprehensive guides in each version's folder

## 📝 License

MIT License - See LICENSE file for details

---

## 🗺️ Project Structure

```
RedditPodcast/
├── README.md                          # This file - main overview
├── News_agent_v1_v2/                  # Versions 1 & 2 (scripts)
│   ├── README.md                      # Detailed v1 & v2 documentation
│   ├── reddit_search_podcast_v1.py    # Version 1 script
│   ├── reddit_search_podcast_v2.py    # Version 2 script (with Telegram)
│   ├── pyproject.toml                 # Dependencies
│   └── .env.example                   # Environment template
└── News_agent_v3/                     # Version 3 (web app)
    ├── docs/
    │   └── README.md                  # Detailed v3 documentation
    ├── app.py                         # Gradio web interface
    ├── workflow.py                    # Main orchestration
    ├── scheduler.py                   # Background scheduling
    ├── docker/
    │   ├── Dockerfile
    │   └── docker-compose.yml
    ├── pyproject.toml
    └── .env.example
```

---

**Built with ❤️ by Lukasz Gawenda** | Powered by PydanticAI, Gemini, and the Reddit Community
