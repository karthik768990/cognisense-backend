# CogniSense Backend - Technical Architecture

## Overview

CogniSense is a digital footprint tracking and analysis platform that helps users understand their online consumption patterns and emotional impact of content. This document outlines the technical architecture for the MVP Phase 1 backend.
- User authentication and personalization

### Technical Constraints
- **Backend:** Python + FastAPI (Required)
- **ML:** Hugging Face Transformers (Required)
- **Priority:** Speed to market > Premature optimization
- **Team:** Small development team, limited DevOps resources

---

## 🛠️ COMPLETE TECH STACK

### **Backend Framework Layer**

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Web Framework** | **FastAPI 0.121+** | • Async/await native<br>• Auto API docs<br>• Pydantic integration<br>• High performance (comparable to Node.js/Go) |
| **ASGI Server** | **Uvicorn** | • Standard for FastAPI<br>• Excellent performance<br>• Built-in with `fastapi[standard]` |
| **Python Version** | **3.12+** | • Latest stable features<br>• Performance improvements<br>• Better type hints |

---

### **Database Layer**

| Component | Choice | Rationale | Alternatives Considered |
|-----------|--------|-----------|------------------------|
| **Database** | **PostgreSQL 16** | ✅ **WINNER**<br>• Concurrent write support<br>• JSONB for flexible metadata<br>• Production-ready<br>• Free tier on Railway/Render<br>• Great for time-series data | ❌ **SQLite**: Bad for concurrent writes from extension<br>❌ **MongoDB**: Overkill for MVP, harder to query relations |
| **ORM** | **SQLModel 0.0.25** | ✅ **WINNER**<br>• Pydantic models = DB models<br>• Type safety<br>• FastAPI creator's library<br>• Less boilerplate | ❌ **Pure SQLAlchemy**: Too much boilerplate<br>❌ **Django ORM**: Requires Django<br>❌ **Tortoise ORM**: Less mature |
| **Migrations** | **Alembic 1.14+** | • Industry standard<br>• SQLModel uses SQLAlchemy under hood<br>• Auto-generate migrations | N/A - No real alternative |

---

### **Authentication & Security**

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Auth Framework** | **FastAPI-Users 13.0+** | • Saves 2-3 weeks of development<br>• Production-tested patterns<br>• Email verification, password reset<br>• SQLModel compatible |
| **Password Hashing** | **passlib + bcrypt** | • Industry standard<br>• Included with FastAPI-Users |
| **JWT Handling** | **python-jose[cryptography]** | • Standard JWT library<br>• Cryptography support |
| **Secrets** | **pydantic-settings** | • Type-safe environment variables<br>• Built-in .env support |

---

### **Machine Learning Stack**

| Component | Choice | Purpose |
|-----------|--------|---------|
| **ML Framework** | **Hugging Face Transformers 4.57+** | Pre-trained NLP models |
| **Backend** | **PyTorch 2.5+** | Required by Transformers |
| **Embeddings** | **sentence-transformers 3.3+** | For topic clustering (bubble detection) |
| **Model Management** | **Custom Singleton Pattern** | Load once at startup, cache in memory |

#### ML Models Selected

```python
MODELS = {
    "sentiment": "distilbert-base-uncased-finetuned-sst-2-english",
    # Fast, accurate, 67M parameters
    
    "zero_shot": "facebook/bart-large-mnli",
    # Best for category classification without training
    
    "emotion": "j-hartmann/emotion-english-distilroberta-base",
    # 7 emotions: joy, anger, sadness, fear, surprise, disgust, neutral
}
```

**Model Management Strategy:**
```
1. Development: Lazy loading (download on first request)
2. Production: Pre-download during Docker build
3. Caching: In-memory singleton (no Redis for MVP)
4. Future: Add model versioning and A/B testing
```

---

### **Data Processing**

| Component | Choice | MVP Approach | Phase 2 Plan |
|-----------|--------|-------------|--------------|
| **Task Queue** | **None** | Process synchronously | Celery + Redis for heavy tasks |
| **Caching** | **In-memory dict** | Simple Python dict | Redis for distributed caching |
| **Text Processing** | **Custom utils** | Simple string operations | Add spaCy if needed |

---

### **Development & Code Quality**

| Component | Choice | Purpose |
|-----------|--------|---------|
| **Dependency Mgmt** | **Poetry 1.8+** | Deterministic builds, better than pip |
| **Linting/Formatting** | **Ruff 0.9+** | 10-100x faster than black+flake8+isort |
| **Testing** | **pytest 8.3+** | Industry standard |
| **Async Testing** | **pytest-asyncio** | Test FastAPI endpoints |
| **HTTP Testing** | **httpx** | Async HTTP client for tests |
| **Coverage** | **pytest-cov** | Code coverage reports |
| **Interactive Shell** | **IPython** | Better REPL for debugging |

---

### **Deployment Stack (MVP)**

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Containerization** | **Docker + Docker Compose** | • One-command local dev<br>• Production parity<br>• Easy CI/CD |
| **Hosting** | **Railway.app** or **Render.com** | ✅ **WINNER**<br>• Free tier available<br>• Auto-deploy from Git<br>• Managed PostgreSQL<br>• Zero DevOps setup<br>• Easy scaling later |
| **CI/CD** | **GitHub Actions** | • Free for public repos<br>• Easy integration |

**Deployment Strategy:**
```
1. Local Dev: Docker Compose (API + PostgreSQL)
2. Staging: Railway.app free tier
3. Production: Railway Pro or Render
4. Future: Kubernetes when scale demands it
```

---

### **Observability (MVP)**

| Component | Choice | Approach |
|-----------|--------|----------|
| **Logging** | **Loguru** | Better than stdlib logging, colorized output |
| **Monitoring** | **None for MVP** | Add Sentry in Phase 2 |
| **Metrics** | **None for MVP** | Add Prometheus/Grafana later |
| **Tracing** | **None for MVP** | Add OpenTelemetry if needed |

---

## 📂 PROJECT SCAFFOLDING

### Complete Directory Structure

```
cognisense-backend/
│
├── .env.example                    # Environment variables template
├── .env                           # Actual secrets (gitignored)
├── .gitignore                     # Git ignore rules
├── README.md                      # Project documentation
├── pyproject.toml                 # Poetry dependencies
├── poetry.lock                    # Locked versions
│
├── docker-compose.yml             # Local dev environment
├── Dockerfile                     # Production container
│
├── alembic/                       # Database migrations
│   ├── env.py                    # Alembic configuration
│   ├── script.py.mako            # Migration template
│   └── versions/                 # Migration files (auto-generated)
│
├── scripts/                       # Utility scripts
│   ├── run_dev.sh                # Development startup
│   ├── download_models.py        # Pre-download ML models
│   └── seed_db.py                # Seed test data
│
├── docs/                          # Documentation
│   ├── API.md                    # API documentation
│   ├── ARCHITECTURE.md           # This file
│   └── DEPLOYMENT.md             # Deployment guide
│
├── app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   │
│   ├── core/                     # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py            # Pydantic Settings (environment)
│   │   ├── security.py          # JWT, password hashing
│   │   └── logging.py           # Loguru setup
│   │
│   ├── db/                       # Database setup
│   │   ├── __init__.py
│   │   ├── session.py           # SQLModel engine & session
│   │   ├── base.py              # Model registry (for Alembic)
│   │   └── init_db.py           # Database initialization
│   │
│   ├── models/                   # SQLModel database models
│   │   ├── __init__.py
│   │   ├── user.py              # User model (FastAPI-Users)
│   │   ├── browsing_session.py # BrowsingSession (time tracking)
│   │   ├── content_snapshot.py # ContentSnapshot (extracted text)
│   │   ├── site_category.py    # SiteCategory (user classifications)
│   │   └── analysis_result.py  # AnalysisResult (ML results)
│   │
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── user.py              # UserRead, UserCreate
│   │   ├── tracking.py          # TrackingEvent, SessionSummary
│   │   ├── content.py           # ContentSubmission, AnalysisResponse
│   │   ├── dashboard.py         # DashboardStats, WeeklySummary
│   │   └── categorization.py   # SiteCategoryCreate
│   │
│   ├── api/                      # API layer
│   │   ├── __init__.py
│   │   ├── deps.py              # Dependency injection (get_db, get_user)
│   │   │
│   │   └── v1/                  # API version 1
│   │       ├── __init__.py
│   │       ├── router.py        # Aggregates all v1 routers
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── tracking.py      # POST /track (time logs)
│   │       ├── content.py       # POST /content/analyze
│   │       ├── categories.py   # GET/POST /categories
│   │       └── dashboard.py     # GET /dashboard/stats
│   │
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── tracking_service.py  # Process browsing sessions
│   │   ├── content_service.py   # Orchestrate content analysis
│   │   ├── categorization_service.py # Apply categorization
│   │   ├── aggregation_service.py    # Compute summaries
│   │   └── recommendation_service.py # Generate suggestions
│   │
│   ├── ml/                       # Machine Learning
│   │   ├── __init__.py
│   │   ├── model_manager.py     # Singleton: load & cache models
│   │   ├── sentiment_analyzer.py # Sentiment analysis service
│   │   ├── zero_shot_classifier.py # Category classification
│   │   ├── emotion_detector.py  # Emotion detection
│   │   ├── topic_extractor.py   # Topic extraction (for bubbles)
│   │   └── bias_detector.py     # Bias detection (optional)
│   │
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   ├── text_processing.py   # Text cleaning, chunking
│   │   ├── date_helpers.py      # Date calculations
│   │   └── validators.py        # Custom validators
│   │
│   └── middleware/               # Custom middleware
│       ├── __init__.py
│       ├── cors.py              # CORS for browser extension
│       └── rate_limiting.py     # Simple rate limiting
│
└── tests/                        # Test suite
    ├── __init__.py
    ├── conftest.py              # Pytest fixtures (test DB, client)
    │
    ├── unit/                    # Unit tests
    │   ├── __init__.py
    │   ├── test_ml_services.py # Test ML in isolation
    │   └── test_utils.py
    │
    ├── integration/             # Integration tests
    │   ├── __init__.py
    │   ├── test_tracking_flow.py
    │   └── test_content_analysis.py
    │
    └── api/                     # API endpoint tests
        ├── __init__.py
        ├── test_auth.py
        ├── test_tracking_endpoints.py
        └── test_dashboard_endpoints.py
```

---

## 🔑 KEY ARCHITECTURAL DECISIONS

### 1. **Layered Architecture**

```
┌─────────────────────────────────────────┐
│         Browser Extension               │ (Client)
└─────────────────┬───────────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────────┐
│         API Layer (FastAPI)             │ (Endpoints)
│   ├── Request validation (Pydantic)     │
│   ├── Authentication (JWT)              │
│   └── Response formatting               │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Services Layer (Business Logic)    │
│   ├── Content analysis orchestration    │
│   ├── Time tracking logic               │
│   └── Aggregation & recommendations     │
└─────────┬───────────────┬───────────────┘
          │               │
┌─────────▼─────┐   ┌────▼──────────────┐
│  ML Services  │   │  Database (ORM)   │
│  (Transformers)│   │  (SQLModel)       │
└───────────────┘   └───────────────────┘
```

### 2. **Separation of Concerns**

| Layer | Responsibility | No Knowledge Of |
|-------|---------------|-----------------|
| **API** | HTTP handling, validation | Database details, ML internals |
| **Services** | Business logic, orchestration | HTTP details, model implementations |
| **ML** | Model inference | Database, HTTP |
| **Models** | Data structure | Business logic, API |

### 3. **ML Model Management Strategy**

**Singleton Pattern:**
```python
# Only ONE instance of ModelManager exists
# Models loaded ONCE at startup
# Cached in memory for entire app lifecycle

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    model_manager = ModelManager()
    await model_manager.load_models()  # Load once
    
    yield  # App runs
    
    # Shutdown (automatic cleanup)
```

**Benefits:**
- Fast inference (no reload per request)
- Memory efficient (single copy of models)
- Simple for MVP (no distributed caching needed)

**Trade-offs:**
- Models consume ~2-3 GB RAM
- No horizontal scaling without external model service (Phase 2 concern)

---

## 🎯 PERFORMANCE CONSIDERATIONS (MVP)

### Expected Load (MVP)
- **Users:** 10-100 concurrent users
- **Requests:** ~10-50 req/sec
- **Response Time Target:** < 2 seconds for analysis

### Bottlenecks & Mitigations

| Potential Bottleneck | MVP Solution | Phase 2 Solution |
|---------------------|--------------|------------------|
| ML inference time | Use lightweight models (DistilBERT) | Add model serving (TorchServe/BentoML) |
| Database writes | PostgreSQL connection pooling | Read replicas, sharding |
| Concurrent requests | Uvicorn workers (4-8) | Load balancer + multiple instances |
| Text processing | Truncate long texts | Background job queue (Celery) |

---

## 🔒 SECURITY CONSIDERATIONS

### Authentication Flow
```
1. User registers → FastAPI-Users creates account
2. User logs in → JWT token issued
3. Extension stores token → Sends with each request
4. API validates token → Allows/denies access
```

### Data Protection
- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens with expiration
- ✅ HTTPS only in production (enforced by host)
- ✅ CORS restricted to extension origin
- ⚠️ Rate limiting (basic, improve in Phase 2)

### Privacy
- Content analysis happens server-side (cannot be fully client-side due to model size)
- User data isolated by user ID
- No sharing between users
- TODO: Add data deletion endpoints (GDPR compliance)

---

## 🚀 DEPLOYMENT ARCHITECTURE

### Local Development
```
Docker Compose:
  ├── PostgreSQL (port 5432)
  └── FastAPI (port 8000)

OR

Manual:
  ├── Local PostgreSQL
  └── Poetry run uvicorn
```

### Production (Railway.app)
```
Railway Services:
  ├── Web Service (FastAPI)
  │   ├── Auto-deploy from GitHub
  │   ├── Environment variables from Railway
  │   └── Uvicorn with 4 workers
  │
  └── PostgreSQL Database
      ├── Managed by Railway
      ├── Automatic backups
      └── Connection pooling
```

---

## 📊 MONITORING & OBSERVABILITY (Future)

### Phase 2 Additions
- **Error Tracking:** Sentry
- **Logging:** Structured JSON logs → CloudWatch/Datadog
- **Metrics:** Prometheus + Grafana
  - Request latency
  - Model inference time
  - Database query performance
- **Alerting:** PagerDuty for critical errors

---

## ✅ DESIGN VALIDATIONS

### Why This Stack Works for MVP

| Requirement | How We Meet It |
|-------------|---------------|
| **Fast Development** | FastAPI auto-docs, SQLModel reduces boilerplate, FastAPI-Users saves weeks |
| **Type Safety** | Pydantic everywhere, Python 3.12 type hints |
| **Scalability Foundation** | Async throughout, PostgreSQL scales well, clear separation of concerns |
| **ML Integration** | Transformers ecosystem mature, models cached efficiently |
| **Cost** | Free tier hosting, open-source everything |
| **Team Size** | Simple architecture, minimal DevOps, good docs |

### Trade-offs Accepted

| Trade-off | Impact | Mitigation Plan |
|-----------|--------|-----------------|
| In-memory model caching | Can't scale horizontally easily | Add model serving in Phase 2 |
| Synchronous ML inference | Blocks request thread | Good enough for MVP load; add job queue later |
| No caching layer | Repeated queries hit DB | PostgreSQL is fast enough; add Redis in Phase 2 |
| Basic rate limiting | Vulnerable to abuse | Monitor usage, add proper rate limiting with Redis |

---

## 📖 NEXT STEPS

### Immediate (MVP Completion)
1. ✅ Core structure created
2. ⏳ Database models & migrations
3. ⏳ FastAPI-Users integration
4. ⏳ Tracking & dashboard endpoints
5. ⏳ Services layer implementation
6. ⏳ Tests

### Phase 2 (Post-MVP)
- Add Redis for caching
- Celery for background jobs
- Model serving with TorchServe
- Advanced analytics (bubble detection)
- Image/video analysis
- Mobile app support

---

## 👥 Team Recommendations

### Roles Needed
- **Backend Dev (You):** FastAPI, SQLModel, ML integration
- **Frontend Dev:** Browser extension, dashboard
- **Optional: ML Engineer:** Fine-tune models, improve accuracy

### Development Order
1. Core API + ML (Week 1-2)
2. Database models + Auth (Week 2-3)
3. Extension integration (Week 3-4)
4. Dashboard API (Week 4-5)
5. Testing + Deploy (Week 5-6)

---

## 📚 References

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLModel Docs](https://sqlmodel.tiangolo.com/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [FastAPI-Users Docs](https://fastapi-users.github.io/fastapi-users/)
- [Railway Docs](https://docs.railway.app/)

---

**Document Version:** 1.0  
**Last Updated:** November 10, 2025  
**Author:** AI Architecture Assistant