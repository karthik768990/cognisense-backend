# API Documentation

## CogniSense Backend API

### Overview
CogniSense Backend is a FastAPI service that provides comprehensive digital footprint tracking with ML-powered content analysis. The system tracks user activity, analyzes content sentiment and emotions, categorizes browsing behavior, and provides dashboard analytics for insights.

### Base URL
```
http://localhost:8000
```

### API Version
All endpoints are versioned under `/api/v1/`

## Core Features

### 🔍 **Content Analysis**
- Real-time sentiment analysis with 99%+ confidence
- Emotion detection across 7 emotional states
- Zero-shot content categorization with 54 detailed categories

### 📊 **Activity Tracking** 
- Browser extension integration for seamless data collection
- Engagement metrics (clicks, keypresses, time spent)
- Automatic ML analysis pipeline

### 🎯 **Category Management**
- 54 comprehensive content categories organized into 8 groups
- User-customizable site preferences
- Intelligent content classification

### 📈 **Dashboard Analytics**
- Time-based activity summaries (daily/weekly)
- Site usage breakdowns
- Sentiment and category distributions

---

## Endpoints Reference

### Health Check

#### GET /api/v1/ping

Simple health check endpoint to verify API availability.

**Request:**
- No parameters required
- No authentication required

**Response:**
```json
{
    "message": "pong",
    "api_version": "v1"
}
```

**Status Codes:**
- `200`: API is healthy and running

---

### Authentication

#### POST /api/v1/auth/signup

Register a new user account with email and password.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string (EmailStr) | Yes | Valid email address |
| password | string | Yes | User password |

**Response:**
```json
{
    "user": {
        "id": "uuid-string",
        "email": "user@example.com",
        "created_at": "2025-11-16T12:00:00Z",
        "email_confirmed_at": null,
        "last_sign_in_at": null,
        "role": "authenticated",
        "updated_at": "2025-11-16T12:00:00Z"
    },
    "session": {
        "access_token": "jwt-token-string",
        "refresh_token": "refresh-token-string",
        "expires_in": 3600,
        "token_type": "bearer"
    }
}
```

**Status Codes:**
- `200`: User created successfully
- `400`: Invalid request data or signup failed
- `500`: Server configuration error

#### POST /api/v1/auth/login

Authenticate a user with email and password.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "user": {
        "id": "uuid-string",
        "email": "user@example.com",
        "created_at": "2025-11-16T12:00:00Z",
        "email_confirmed_at": "2025-11-16T12:05:00Z",
        "last_sign_in_at": "2025-11-16T15:30:00Z",
        "role": "authenticated",
        "updated_at": "2025-11-16T15:30:00Z"
    },
    "session": {
        "access_token": "jwt-token-string",
        "refresh_token": "refresh-token-string",
        "expires_in": 3600,
        "token_type": "bearer"
    }
}
```

**Status Codes:**
- `200`: Login successful
- `401`: Invalid credentials or login failed
- `500`: Server configuration error

#### GET /api/v1/auth/me

Retrieve the authenticated user's information.

**Authentication Required:** Yes

**Request:**
- Headers: `Authorization: Bearer <token>`

**Response:**
```json
{
    "user": {
        "id": "uuid-string",
        "email": "user@example.com",
        "created_at": "2025-11-16T12:00:00Z",
        "email_confirmed_at": "2025-11-16T12:05:00Z",
        "last_sign_in_at": "2025-11-16T15:30:00Z",
        "role": "authenticated",
        "updated_at": "2025-11-16T15:30:00Z"
    }
}
```

**Status Codes:**
- `200`: User information retrieved successfully
- `401`: Invalid or expired token
- `500`: Server configuration error

---

### Content Analysis

#### POST /api/v1/content/analyze

Analyzes provided content for sentiment, emotion, and categorization.

**Request Body:**
```json
{
    "text": "This is a sample text to analyze",
    "url": "https://example.com",
    "analyze_sentiment": true,
    "analyze_category": true,
    "analyze_emotions": true
}
```

**Parameters:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| text | string | Yes | - | Text content to analyze |
| url | string | No | null | Source URL of the content |
| analyze_sentiment | boolean | No | true | Enable sentiment analysis |
| analyze_category | boolean | No | true | Enable content categorization |
| analyze_emotions | boolean | No | true | Enable emotion detection |

**Response:**
```json
{
    "text_length": 33,
    "word_count": 7,
    "url": "https://example.com",
    "sentiment": {
        "label": "POSITIVE",
        "score": 0.9999
    },
    "category": {
        "primary": "Programming",
        "confidence": 0.8234,
        "all_categories": [
            {"label": "Programming", "score": 0.8234},
            {"label": "Documentation", "score": 0.1123},
            {"label": "Learning", "score": 0.0643}
        ]
    },
    "emotions": {
        "dominant": {"label": "joy", "score": 0.9909},
        "all_emotions": [
            {"label": "joy", "score": 0.9909},
            {"label": "optimism", "score": 0.0046},
            {"label": "love", "score": 0.0023},
            {"label": "admiration", "score": 0.0011},
            {"label": "approval", "score": 0.0006}
        ],
        "balance": {
            "positive_score": 0.99,
            "negative_score": 0.01,
            "balance": 0.99,
            "is_balanced": false
        }
    }
}
```

#### POST /api/v1/content/analyze/batch

Analyze multiple text contents in a single request.

**Request Body:**
```json
{
    "texts": [
        "I love this new productivity app!",
        "Breaking news: Major tech announcement today",
        "Checking social media updates"
    ]
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| texts | array[string] | Yes | Array of text strings to analyze |

**Response:**
Returns an array of analysis results, one for each input text. Each result follows the same structure as the single analysis endpoint. Failed analyses will include an `"error"` field instead of analysis data.

**Status Codes:**
- `200`: Batch analysis completed (individual items may have errors)
- `400`: Invalid request data (empty array)

---

### Activity Tracking

#### POST /api/v1/tracking/ingest

Ingests activity data from browser extension with real-time ML analysis.

**Request Body:**
```json
{
    "user_id": "user123",
    "url": "https://github.com/example/repo",
    "title": "GitHub Repository",
    "text": "Python machine learning project with advanced algorithms",
    "start_ts": 1704067200.0,
    "end_ts": 1704067800.0,
    "duration_seconds": 600,
    "clicks": 15,
    "keypresses": 245,
    "engagement_score": 0.85
}
```

**Response:**
```json
{
    "status": "ok",
    "ingested": 1
}
```

#### GET /api/v1/tracking/activity/{user_id}

Retrieves recent activity records for a user.

**Query Parameters:**
- `limit` (optional): Number of records to return (1-1000, default: 100)

**Example:**
```bash
curl "http://localhost:8000/api/v1/tracking/activity/user123?limit=50"
```

**Response:**
```json
{
    "user_id": "user123",
    "count": 50,
    "items": [
        {
            "user_id": "user123",
            "url": "https://github.com/example/repo",
            "title": "GitHub Repository", 
            "text": "Python machine learning project with advanced algorithms",
            "duration_seconds": 600.0,
            "clicks": 15,
            "keypresses": 245,
            "sentiment": {
                "label": "POSITIVE",
                "confidence": 0.9999
            },
            "classified_category": "Programming",
            "category_group": "Productive",
            "emotions": {
                "joy": 0.9909,
                "optimism": 0.0046
            },
            "received_at": 1704067800.0
        }
    ]
}
```

#### DELETE /api/v1/tracking/activity/{user_id}

Clears all activity data for a user (useful for testing).

**Response:**
```json
{
    "status": "ok",
    "removed": 25
}
```

---

### Category Management

#### GET /api/v1/categories/labels

Returns all 54 available content categories.

**Response:**
```json
{
    "categories": [
        "Programming", "Documentation", "Code Review", "Technical Writing",
        "Social Media", "Messaging", "Video Calls", "Forums",
        "Streaming", "Gaming", "Music", "Videos", "Reading",
        "News", "Research", "Learning", "Reference",
        "Shopping", "Finance", "Travel", "Health",
        "Email", "Calendar", "Notes", "Utilities",
        "Adult Content", "Gambling", "Excessive Gaming",
        "Uncategorized", "Personal", "Other"
    ],
    "total": 54
}
```

#### GET /api/v1/categories/groups

Returns categories organized by functional groups.

**Response:**
```json
{
    "groups": {
        "Productive": ["Programming", "Documentation", "Code Review", "Technical Writing", "Project Management", "Development Tools", "Design"],
        "Social": ["Social Media", "Messaging", "Video Calls", "Forums", "Dating", "Community"],
        "Entertainment": ["Streaming", "Gaming", "Music", "Videos", "Reading", "Sports", "Hobbies"],
        "Information": ["News", "Research", "Learning", "Reference", "Science", "Technology"],
        "Lifestyle": ["Shopping", "Finance", "Travel", "Health", "Food", "Fitness", "Fashion"],
        "Commerce": ["Business", "Marketing", "Sales", "E-commerce", "Banking", "Investment"],
        "Problematic": ["Adult Content", "Gambling", "Excessive Gaming", "Harmful Content"],
        "Other": ["Uncategorized", "Personal", "Utilities", "Email", "Calendar", "Notes"]
    }
}
```

#### GET /api/v1/categories/classify

Classifies text using zero-shot classification.

**Query Parameters:**
- `text` (required): Text to classify

**Example:**
```bash
curl "http://localhost:8000/api/v1/categories/classify?text=Building%20a%20React%20application"
```

**Response:**
```json
{
    "labels": ["Programming", "Documentation", "Learning"],
    "scores": [0.8234, 0.1123, 0.0643]
}
```

#### GET /api/v1/categories/classify/grouped

Classifies text and returns both specific category and broad group.

**Query Parameters:**
- `text` (required): Text to classify

**Response:**
```json
{
    "labels": ["Programming", "Documentation"],
    "scores": [0.8234, 0.1123],
    "category_group": "Productive",
    "top_category": "Programming",
    "confidence": 0.8234
}
```

#### POST /api/v1/categories/user/{user_id}/sites

Sets user preference for site categorization.

**Request Body:**
```json
{
    "user_id": "user123",
    "site": "github.com",
    "category": "Programming"
}
```

**Response:**
```json
{
    "status": "ok",
    "site": "github.com",
    "category": "Programming"
}
```

#### GET /api/v1/categories/user/{user_id}/sites

Retrieves user's site categorization preferences.

**Response:**
```json
{
    "user_id": "user123",
    "preferences": {
        "github.com": "Programming",
        "youtube.com": "Entertainment",
        "stackoverflow.com": "Learning"
    }
}
```

---

### Dashboard Analytics

#### GET /api/v1/dashboard/summary/{user_id}

Provides aggregated activity summary with time-based filtering.

**Query Parameters:**
- `period` (optional): "daily" or "weekly" (default: "weekly")

**Example:**
```bash
curl "http://localhost:8000/api/v1/dashboard/summary/user123?period=daily"
```

**Response:**
```json
{
    "user_id": "user123",
    "summary": {
        "period": "daily",
        "records_counted": 25,
        "total_time_seconds": 14400.0,
        "top_sites": [
            {"site": "https://github.com", "time_seconds": 7200.0},
            {"site": "https://stackoverflow.com", "time_seconds": 3600.0},
            {"site": "https://youtube.com", "time_seconds": 2400.0}
        ],
        "categories": [
            {"category": "Programming", "value": 10800.0, "proportion": 0.75},
            {"category": "Learning", "value": 2400.0, "proportion": 0.167},
            {"category": "Entertainment", "value": 1200.0, "proportion": 0.083}
        ],
        "sentiments": [
            {"sentiment": "POSITIVE", "count": 20, "proportion": 0.8},
            {"sentiment": "NEUTRAL", "count": 5, "proportion": 0.2}
        ]
    }
}
```

#### GET /api/v1/dashboard/sites/{user_id}

Returns table view of sites with aggregated metrics.

**Query Parameters:**
- `limit` (optional): Maximum sites to return (1-1000, default: 100)

**Response:**
```json
{
    "user_id": "user123",
    "sites": [
        {
            "site": "https://github.com",
            "time_seconds": 7200.0,
            "visits": 15,
            "category": "Programming"
        },
        {
            "site": "https://stackoverflow.com", 
            "time_seconds": 3600.0,
            "visits": 8,
            "category": "Learning"
        }
    ]
}
```

---

## Machine Learning Models

The API uses state-of-the-art transformer models for real-time analysis:

### **Sentiment Analysis**
- **Model**: `distilbert-base-uncased-finetuned-sst-2-english`
- **Capability**: Binary sentiment classification (POSITIVE/NEGATIVE)
- **Accuracy**: 99%+ confidence on clear sentiment expressions
- **Performance**: Optimized for real-time processing

### **Emotion Detection** 
- **Model**: `j-hartmann/emotion-english-distilroberta-base`
- **Emotions**: joy, sadness, anger, fear, surprise, disgust, optimism, love, admiration, approval, excitement, caring
- **Output**: Probability distribution across all emotions
- **Use Case**: Detailed emotional state analysis of browsing content

### **Content Categorization**
- **Model**: `typeform/distilbert-base-uncased-mnli` (Zero-shot)
- **Categories**: 54 detailed categories across 8 functional groups
- **Approach**: Zero-shot classification for maximum flexibility
- **Coverage**: Programming, Social Media, Entertainment, Learning, Shopping, etc.

## Integration Examples

### Browser Extension Integration

```javascript
// Ingest activity with content analysis
async function trackActivity(activityData) {
    const response = await fetch('http://localhost:8000/api/v1/tracking/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: 'user123',
            url: window.location.href,
            title: document.title,
            text: extractPageText(),
            start_ts: Date.now() / 1000,
            duration_seconds: getSessionDuration(),
            clicks: getClickCount(),
            keypresses: getKeypressCount()
        })
    });
    return response.json();
}

// Get dashboard summary
async function getDashboard(userId, period = 'weekly') {
    const response = await fetch(
        `http://localhost:8000/api/v1/dashboard/summary/${userId}?period=${period}`
    );
    return response.json();
}
```

### Python Client Example

```python
import requests

# Analyze content
def analyze_content(text, url, user_id):
    response = requests.post('http://localhost:8000/api/v1/content/analyze', json={
        'text': text,
        'url': url,
        'user_id': user_id
    })
    return response.json()

# Get available categories
def get_categories():
    response = requests.get('http://localhost:8000/api/v1/categories/labels')
    return response.json()['categories']

# Classify text
def classify_text(text):
    response = requests.get(
        'http://localhost:8000/api/v1/categories/classify', 
        params={'text': text}
    )
    return response.json()
```

## Error Responses

#### 400 Bad Request
```json
{
    "detail": "user_id and url required"
}
```

#### 422 Unprocessable Entity  
```json
{
    "detail": [
        {
            "loc": ["body", "text"],
            "msg": "field required", 
            "type": "value_error.missing"
        }
    ]
}
```

#### 500 Internal Server Error
```json
{
    "detail": "Classification failed: Model not loaded"
}
```

## Performance & Deployment

### Model Loading
- **Strategy**: Lazy loading to optimize startup time
- **Memory**: Models load on first request to minimize resource usage
- **Caching**: Models remain in memory for subsequent requests

### Scalability Considerations
- **Phase 1**: In-memory storage for rapid prototyping
- **Phase 2**: Database integration planned for production scale
- **Optimization**: Model instances are shared across requests

### Rate Limiting
Currently no rate limiting is implemented, but will be added for production deployment.

### Authentication
Optional Supabase integration available. Authentication can be enabled through environment configuration for production use.