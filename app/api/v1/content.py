"""
Content Analysis API Endpoints
Receives text content from browser extension and performs ML analysis
"""

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from app.ml.sentiment_analyzer import SentimentAnalyzer
from app.ml.zero_shot_classifier import ZeroShotClassifier
from app.ml.emotion_detector import EmotionDetector

router = APIRouter()

# Initialize ML services
sentiment_analyzer = SentimentAnalyzer()
zero_shot_classifier = ZeroShotClassifier()
emotion_detector = EmotionDetector()


@router.post("/analyze")
async def analyze_content(
    text: str,
    url: str = None,
    analyze_sentiment: bool = True,
    analyze_category: bool = True,
    analyze_emotions: bool = True
):
    """
    Analyze text content from a webpage
    
    Args:
        text: Text content extracted from webpage
        url: Optional URL of the webpage
        analyze_sentiment: Whether to perform sentiment analysis
        analyze_category: Whether to classify content category
        analyze_emotions: Whether to detect emotions
    
    Returns:
        Dictionary with analysis results
    """
    if not text or len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text content is required")
    
    logger.info(f"Analyzing content from {url or 'unknown URL'} ({len(text)} chars)")
    
    results = {
        "text_length": len(text),
        "word_count": len(text.split()),
        "url": url
    }
    
    try:
        # Sentiment Analysis
        if analyze_sentiment:
            sentiment = sentiment_analyzer.analyze(text)
            results["sentiment"] = sentiment
        
        # Category Classification
        if analyze_category:
            category = zero_shot_classifier.classify(text)
            results["category"] = {
                "primary": category["labels"][0],
                "confidence": category["scores"][0],
                "all_categories": [
                    {"label": label, "score": score}
                    for label, score in zip(category["labels"][:3], category["scores"][:3])
                ]
            }
        
        # Emotion Detection
        if analyze_emotions:
            emotions = emotion_detector.detect(text)
            results["emotions"] = {
                "dominant": emotions[0],
                "all_emotions": emotions[:5],  # Top 5
                "balance": emotion_detector.calculate_emotional_balance(emotions)
            }
        
        logger.info(f"Analysis complete for {url or 'unknown URL'}")
        return results
        
    except Exception as e:
        logger.error(f"Content analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/batch")
async def analyze_content_batch(texts: list[str]):
    """
    Analyze multiple text contents in batch
    
    Args:
        texts: List of text contents
    
    Returns:
        List of analysis results
    """
    if not texts:
        raise HTTPException(status_code=400, detail="At least one text required")
    
    logger.info(f"Batch analyzing {len(texts)} texts")
    
    results = []
    for text in texts:
        try:
            result = await analyze_content(text)
            results.append(result)
        except Exception as e:
            logger.error(f"Batch item failed: {e}")
            results.append({"error": str(e)})
    
    return results
