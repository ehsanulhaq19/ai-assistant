# VexaCore AI - Smart AI Routing System

A FastAPI-based AI routing system that intelligently selects the best AI model based on query complexity, content type, and user requirements.

## Features

- **Smart Model Selection**: Automatically chooses optimal AI model based on query complexity and content type
- **Rate Limiting**: 5 requests/minute for free users, unlimited for pro
- **Fallback System**: Automatic fallback to reliable models if primary fails
- **Cost Tracking**: Real-time cost calculation and usage monitoring
- **Session Management**: Track user sessions and query history

### Supported Models
- **GPT-4o-mini**: Cost-effective for simple queries (< 50 words)
- **GPT-4o**: Advanced model for complex queries and code-related tasks
- **Claude Sonnet**: Specialized for creative writing and complex reasoning

### Model Selection Logic
```
Simple queries (< 50 words) → GPT-4o-mini
Code-related queries → GPT-4o
Creative writing → Claude Sonnet
Complex queries (50+ words) → Claude Sonnet
Fallback → GPT-4o-mini
```

## Quick Start

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+
- OpenAI API key
- Anthropic API key

### 1. Setup
```bash
git clone <repository-url>
cd ai-assistant
pip install -r requirements.txt
cp env.example .env
# Edit .env with your API keys
```

### 2. Start Services
```bash
# Using Docker (recommended)
docker-compose up -d mysql redis

# Or locally
redis-server
mysql -u root -p  # Create database: CREATE DATABASE vexacore_ai;

# Start application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Verify
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

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

# Model Pricing (per 1K tokens)
GPT4O_MINI_COST=0.00015
GPT4O_COST=0.005
CLAUDE_SONNET_COST=0.003
```

## API Usage

### Main Endpoint
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

### Other Endpoints
- `GET /api/v1/ai/models` - Available models and selection logic
- `GET /api/v1/ai/usage/{user_id}` - User usage statistics
- `GET /health` - Health check

## Testing

### Sample Users
- **Free User**: `free@example.com` (5 requests/minute)
- **Pro User**: `pro@example.com` (unlimited)
- **Password**: `password123` for all

### Test Examples

**Simple Query (GPT-4o-mini):**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather like?", "user_id": 1, "session_id": "test123"}'
```

**Code Query (GPT-4o):**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Write a Python function to sort a list", "user_id": 1, "session_id": "test123"}'
```

**Creative Writing (Claude Sonnet):**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Write a short story about a robot", "user_id": 1, "session_id": "test123"}'
```

## Project Structure
```
vexacore-ai/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Configuration
│   ├── models/          # Database models
│   ├── repository/      # Data access layer
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── main.py
├── scripts/             # Database initialization
├── requirements.txt
├── docker-compose.yml
└── README.md
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

## Configuration

### Rate Limiting
- Free users: 5 requests per minute
- Pro/Expert users: Unlimited

### Model Pricing (per 1K tokens)
- GPT-4o-mini: $0.00015
- GPT-4o: $0.005
- Claude Sonnet: $0.003

## Architecture

The system uses a service-oriented architecture with:
- **Repository Pattern**: Centralized database operations
- **Service Layer**: Business logic and AI model management
- **Rate Limiting**: Redis-based request limiting
- **Cost Tracking**: Real-time usage monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

---

**VexaCore AI** - Intelligent AI routing for the future