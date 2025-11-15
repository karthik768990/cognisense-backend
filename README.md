# CogniSense Backend

**Digital Footprint Tracking & Analysis API** - MVP Phase 1

A FastAPI-based backend service that powers the CogniSense platform for tracking, analyzing, and providing insights into users' digital footprint and online content consumption patterns.

---

## 🚀 Features (Phase 1)

### Core Functionality
- **Content Ingestion API**: Receives text data from browser extension
- **ML-Powered Analysis**:
  - Sentiment Analysis (Positive/Negative/Neutral)
  - Content Categorization (Productivity/Social/Entertainment/News/etc.)
  - Emotion Detection (Joy, Anger, Sadness, Fear, etc.)
  - Emotional Balance Tracking
- **Time Tracking**: Store and aggregate browsing session data
- **User Categorization**: Custom site classifications

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|-------|
| **Framework** | FastAPI | High-performance async web framework |
| **Server** | Uvicorn | ASGI server |
| **Database** | Supabase (PostgreSQL) | Managed PostgreSQL with real-time features |
| **ORM** | SQLModel | Type-safe ORM with Pydantic integration |
| **ML Library** | Hugging Face Transformers | Pre-trained NLP models |
| **Authentication** | FastAPI-Users + JWT | User management and auth |
| **Validation** | Pydantic | Data validation and settings |
| **Testing** | Pytest | Unit and integration tests |
| **Dependency Mgmt** | Poetry | Python package management |
| **Containerization** | Docker | Application containerization |

---

## 📁 Project Structure

```
cognisense-backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── core/                      # Core configuration
│   │   ├── config.py             # Pydantic settings
│   │   ├── security.py           # JWT & password hashing
│   │   └── logging.py            # Loguru configuration
│   ├── ml/                        # Machine Learning
│   │   ├── model_manager.py      # Singleton model loader
│   │   ├── sentiment_analyzer.py # Sentiment analysis
│   │   ├── zero_shot_classifier.py # Content categorization
│   │   └── emotion_detector.py   # Emotion detection
│   ├── api/v1/                    # API endpoints
│   │   ├── router.py             # Main router
│   │   ├── content.py            # Content analysis endpoints
│   │   ├── tracking.py           # Time tracking endpoints (TODO)
│   │   └── dashboard.py          # Dashboard stats (TODO)
│   ├── models/                    # SQLModel database models (TODO)
│   ├── schemas/                   # Pydantic request/response schemas (TODO)
│   └── services/                  # Business logic layer (TODO)
├── tests/                         # Test suite
├── docker-compose.yml            # Local dev environment
├── Dockerfile                     # Production container
├── pyproject.toml                # Poetry dependencies
└── .env.example                   # Environment variables template
```

---

## 🔧 Setup Instructions

### Prerequisites
- Python 3.12+
- Poetry (for dependency management)
- Supabase account (for database)
- Docker (optional, for containerized deployment)

### 1. Clone Repository
```bash
git clone https://github.com/DhruvPokhriyal/cognisense-backend.git
cd cognisense-backend
```

### 2. Install Dependencies
```bash
poetry install
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

**Key environment variables:**
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/service key
- `SECRET_KEY`: JWT secret (generate with `openssl rand -hex 32`)
- `ALLOWED_ORIGINS`: CORS origins for browser extension

### 4. Set up Supabase Database
1. Create a new project at [supabase.com](https://supabase.com)
2. Copy your project URL and anon key to `.env`
3. Set up your database schema using Supabase dashboard or SQL editor

### 5. Start Development Server
```bash
poetry run uvicorn app.main:app --reload
```

Server will be available at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

---

## 🐳 Docker Setup (Alternative)

Run the API in a container (database is managed by Supabase):

```bash
docker build -t cognisense-backend .
docker run -p 8000:8000 --env-file .env cognisense-backend
```

This starts the API at: http://localhost:8000

---

## 🧪 Testing

Run tests with pytest:

```bash
poetry run pytest

# With coverage
poetry run pytest --cov=app --cov-report=html
```

---

## 📡 API Endpoints (Current)

### Health Check
```
GET /
GET /health
```

### Content Analysis (MVP Core)
```
POST /api/v1/content/analyze
```

**Request Body:**
```json
{
  "text": "Your webpage content here...",
  "url": "https://example.com",
  "analyze_sentiment": true,
  "analyze_category": true,
  "analyze_emotions": true
}
```

**Response:**
```json
{
  "text_length": 1234,
  "word_count": 200,
  "url": "https://example.com",
  "sentiment": {
    "label": "POSITIVE",
    "score": 0.9998
  },
  "category": {
    "primary": "Technology",
    "confidence": 0.95,
    "all_categories": [...]
  },
  "emotions": {
    "dominant": {"label": "joy", "score": 0.85},
    "all_emotions": [...],
    "balance": {
      "positive_score": 0.85,
      "negative_score": 0.15,
      "balance": 0.85,
      "is_balanced": false
    }
  }
}
```

---

## 📋 Development Roadmap

For detailed development tasks and roadmap, see [TODO.md](TODO.md).

---

## 📖 Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test**
   ```bash
   poetry run pytest
   ```

3. **Format code with ruff**
   ```bash
   poetry run ruff check --fix .
   poetry run ruff format .
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin feature/your-feature-name
   ```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📝 License

MIT License

---

## 👥 Authors

- **Dhruv Pokhriyal** - [GitHub](https://github.com/DhruvPokhriyal)

---

## 🙏 Acknowledgments

- Hugging Face for pre-trained models
- FastAPI framework
- SQLModel and Pydantic teams
