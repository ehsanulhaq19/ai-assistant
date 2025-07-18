# VexaCore AI - Smart AI Routing System

A FastAPI-based AI routing system that intelligently selects the best AI model based on query complexity and content type.

## App Purpose

VexaCore AI automatically routes user queries to the most appropriate AI model based on:
- Query complexity (word count)
- Content type (code, creative writing, general)
- Cost optimization
- Performance requirements

## App Structure

```
ai-assistant/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Configuration and settings
│   ├── models/          # Database models
│   ├── repository/      # Data access layer
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic and AI model management
│   └── main.py          # FastAPI application entry point
├── scripts/             # Database initialization scripts
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker services configuration
└── README.md
```

## App Setup Flow

### 1. Prerequisites
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+
- OpenAI API key
- Anthropic API key

### 2. Installation
```bash
# Clone and setup
git clone <repository-url>
cd ai-assistant
pip install -r requirements.txt

# Environment configuration
cp env.example .env
# Edit .env with your API keys and database settings
```

### 3. Start Services
```bash
# Using Docker (recommended)
docker-compose up -d mysql redis

# Or start locally
redis-server
mysql -u root -p  # Create database: CREATE DATABASE vexacore_ai;

# Start application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Setup
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Rate Limit Logic

### Free Users
- **Limit**: 5 requests per minute
- **Window**: 60 seconds
- **Storage**: Redis-based tracking

### Pro Users
- **Limit**: Unlimited requests
- **No restrictions**

### Implementation
- Rate limiting is enforced at the API level
- User type is determined by database user record
- Exceeded limits return HTTP 429 (Too Many Requests)

## Models Being Used

### Available Models

| Model | Use Case | Cost per 1K tokens |
|-------|----------|-------------------|
| **GPT-4o-mini** | Simple queries (< 50 words) | $0.00015 |
| **GPT-4o** | Code-related tasks, complex queries | $0.005 |
| **Claude Sonnet** | Creative writing, complex reasoning | $0.003 |

### Model Selection Logic

```
Query Analysis:
├── Simple queries (< 50 words) → GPT-4o-mini
├── Code-related queries → GPT-4o
├── Creative writing → Claude Sonnet
├── Complex queries (50+ words) → Claude Sonnet
└── Fallback (if primary fails) → GPT-4o-mini
```

### API Usage

**Main Endpoint:**
```http
POST /api/v1/ai/query
Content-Type: application/json

{
  "query": "Your question here",
  "user_id": 1,
  "session_id": "abc123"
}
```

**Response:**
```json
{
  "response": "AI generated response",
  "model_used": "gpt-4o",
  "tokens_used": 245,
  "cost_usd": 0.00123,
  "processing_time": 1.2,
  "session_id": "abc123",
  "remaining_queries": 95
}
```

## Environment Variables

Required in `.env`:
```env
# Database
DATABASE_URL=mysql://vexacore:vexacorepass@mysql:3306/vexacore_ai
REDIS_URL=redis://redis:6379/0

# API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# JWT
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
FREE_USER_RATE_LIMIT=5
FREE_USER_RATE_LIMIT_WINDOW=60

# Model Pricing
GPT4O_MINI_COST=0.00015
GPT4O_COST=0.005
CLAUDE_SONNET_COST=0.003
```

## Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```