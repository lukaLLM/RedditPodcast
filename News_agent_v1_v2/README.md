# Reddit AI Analyzer 🤖

An intelligent Reddit data fetcher and analyzer that uses AI to extract insights from Reddit posts and comments. This tool fetches top posts from specified subreddits, collects comments, and provides AI-powered analysis based on your custom criteria.

## 📋 Features

- **Multi-Subreddit Fetching**: Fetch top posts from multiple AI-related subreddits
- **Intelligent Comment Analysis**: Collect and analyze top comments and replies
- **AI-Powered Insights**: Use Gemini 2.5 Pro to analyze content for trends and insights
- **Flexible Time Filters**: Analyze posts from different time periods (hour, day, week, month, year)
- **Data Export**: Save raw data and AI analysis to timestamped files
- **Rate Limiting**: Built-in delays to respect Reddit API limits
- **Comprehensive Logging**: Integrated with Logfire for debugging and monitoring

## 🚀 What This Tool Does

The Reddit AI Analyzer follows a structured 5-step workflow:

1. **📝 STEP 1**: Fetches top posts from configured subreddits
2. **📝 STEP 2**: Collects comments and replies for each post
3. **📝 STEP 3**: Saves raw data to timestamped files
4. **🧠 STEP 4**: Runs AI analysis using your custom criteria
5. **📝 STEP 5**: Saves AI analysis to separate files

### Target Use Cases
- Anybody seeking latest trends and insights from his favourtie reddits to feed into the [notebook](https://notebooklm.google/)

## 🛠️ Installation Guide

### Prerequisites

- **Python 3.12+** (Required)
- **uv** (Modern Python package manager)
- **Reddit API credentials**
- **Logfire token** (optional, for logging)

### Step 1: Install uv (Python Package Manager)

#### On Linux/macOS:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### On Windows:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Alternative installation methods:
```bash
# Using pip
pip install uv

# Using pipx
pipx install uv

# Using Homebrew (macOS)
brew install uv
```

### Step 2: Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/lukaLLM/RedditPodcast.git

# Create virtual environment and install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
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

### Logfire Token (Optional)

1. **Visit**: https://logfire.pydantic.dev/
2. **Sign up/Login** with GitHub
3. **Create Project**: Name it `reddit-analyzer`
4. **Get Token**: Copy the write token from project settings

### Environment Variables Setup

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env
```

Add the following content to `.env`:

```env
# Reddit API Credentials (REQUIRED)
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here

# Logfire Token (OPTIONAL - for debugging/monitoring)
LOGFIRE_TOKEN=your_logfire_token_here
```

### Environment File Example

```env
# Example .env file
REDDIT_CLIENT_ID=abc123xyz789
REDDIT_CLIENT_SECRET=def456uvw012-XyZ789AbC
LOGFIRE_TOKEN=lf_1234567890abcdef
```

## ⚙️ Configuration

### TimeFilter Enum Options

The `TimeFilter` enum controls the time period for fetching top posts:

```python
class TimeFilter(Enum):
    HOUR = "hour"     # Top posts from last hour
    DAY = "day"       # Top posts from last 24 hours  
    WEEK = "week"     # Top posts from last 7 days
    MONTH = "month"   # Top posts from last 30 days
    YEAR = "year"     # Top posts from last year
    ALL = "all"       # Top posts of all time
```

### Customizable Parameters

Edit these variables in `reddit_search_podcast.py`:

```python
# Time filter for posts
TIME_FILTER = TimeFilter.WEEK  # Change to any TimeFilter option

# Subreddit configuration: {subreddit_name: post_limit}
SUBREDDIT_CONFIG = {
    "LocalLLaMA": 7,              # Fetch 7 posts from r/LocalLLaMA
    "artificial": 5,              # Fetch 5 posts from r/artificial
    "MachineLearning": 2,         # Fetch 2 posts from r/MachineLearning
    "OpenAI": 5,                  # Fetch 5 posts from r/OpenAI
    "AI_Agents": 2,               # Fetch 2 posts from r/AI_Agents
    "ArtificialInteligence": 5    # Fetch 5 posts from r/ArtificialInteligence
}

# Comment and reply limits
TOP_COMMENTS_LIMIT = 10       # Max comments per post we fetch
REPLIES_PER_COMMENT = 5       # Max replies per comment we fetch 
LIMIT_FETCH_POSTS = 10        # Global post limit per subreddit

# AI Model
MODEL = "gemini-2.5-pro"      # Currently supports Gemini models
```

### Custom Analysis Criteria

Modify the `USER_PROMPT` to change what the AI looks for:

```python
USER_PROMPT = """
Look for most insightful posts and comments that would enrich my knowledge as AI Engineer. 
Look for New AI models, performance benchmarks, ideas for projects, novel ideas/techniques around AI.
"""
```

**Example customizations**:
- Research focus: `"Focus on academic papers and research breakthroughs"`
- Business focus: `"Look for commercial AI applications and startup news"`
- Technical focus: `"Find implementation details, code examples, and technical tutorials"`

## 🎯 Usage

### Basic Usage

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the analyzer
python agent_pydantic_1.py
```

### Advanced Usage Examples

#### 1. Quick Daily Analysis
```python
# In agent_pydantic_1.py, set:
TIME_FILTER = TimeFilter.DAY
SUBREDDIT_CONFIG = {"LocalLLaMA": 3, "OpenAI": 3}
```

#### 2. Deep Weekly Research
```python
# In agent_pydantic_1.py, set:
TIME_FILTER = TimeFilter.WEEK
SUBREDDIT_CONFIG = {
    "LocalLLaMA": 10,
    "MachineLearning": 8,
    "artificial": 7,
    "OpenAI": 5,
    "AI_Agents": 5
}
```

#### 3. Custom Subreddit Analysis
```python
# Add your own subreddits:
SUBREDDIT_CONFIG = {
    "ChatGPT": 5,
    "singularity": 3,
    "compsci": 2,
    "Programming": 3
}
```

### Output Files

The tool generates two types of files:

1. **Raw Data**: `reddit_data_YYYY-MM-DD_HH-MM-SS.txt`
   - Contains all fetched posts and comments
   - Useful for manual analysis or reprocessing

2. **AI Analysis**: `reddit_analysis_YYYY-MM-DD_HH-MM-SS.txt`
   - Contains AI-generated insights and trends
   - Ready for content creation or research

### Rate Limiting

Reddit has strict rate limits. The tool includes:
- 1-second delays between comment fetches
- Limited post counts per subreddit
- Error handling for rate limit responses

If you hit rate limits:
1. Reduce `SUBREDDIT_CONFIG` limits
2. Increase delays in the code
3. Use longer `TIME_FILTER` periods (WEEK vs DAY)

### Memory Usage

For large analyses:
- Monitor memory usage with many subreddits
- Consider reducing `TOP_COMMENTS_LIMIT` and `REPLIES_PER_COMMENT`
- Process subreddits individually if needed

## 🙋‍♂️ Support

- **Issues**: Open a GitHub issue for bugs or feature requests
- **YouTube**: Check out my AI tech channel for tutorials and insights: https://www.youtube.com/@LukaszGawendaAI
