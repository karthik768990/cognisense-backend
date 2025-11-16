"""
ML Model Manager - Singleton pattern for loading and caching Hugging Face models
Models are loaded once at startup and kept in memory for the application lifecycle
"""

from typing import Optional
from transformers import pipeline
from loguru import logger

from app.core.config import settings


class ModelManager:
    """
    Singleton class to manage ML models
    Uses lazy loading - models are loaded on first use
    """
    
    _instance: Optional['ModelManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize model placeholders"""
        self.sentiment_analyzer = None
        self.zero_shot_classifier = None
        self.emotion_detector = None
        self._sentiment_loading = False
        self._zero_shot_loading = False
        self._emotion_loading = False
    
    async def load_models(self):
        """
        Placeholder for compatibility - actual loading happens on-demand
        """
        logger.info("Models will be loaded on first use (lazy loading)")
    
    def _load_sentiment_model(self):
        """Load sentiment model on first use"""
        if self.sentiment_analyzer is None and not self._sentiment_loading:
            self._sentiment_loading = True
            try:
                logger.info("Loading default sentiment model")
                # Use the default small sentiment model
                self.sentiment_analyzer = pipeline("sentiment-analysis", device=-1)
                logger.info("✓ Sentiment model loaded")
            except Exception as e:
                logger.error(f"Failed to load sentiment model: {e}")
                raise e
            finally:
                self._sentiment_loading = False
    
    def _load_zero_shot_model(self):
        """Load zero-shot classifier on first use"""
        if self.zero_shot_classifier is None and not self._zero_shot_loading:
            self._zero_shot_loading = True
            try:
                logger.info("Loading zero-shot classifier: typeform/distilbert-base-uncased-mnli")
                # Use a smaller zero-shot model
                self.zero_shot_classifier = pipeline(
                    "zero-shot-classification",
                    model="typeform/distilbert-base-uncased-mnli",
                    device=-1
                )
                logger.info("✓ Zero-shot classifier loaded")
            except Exception as e:
                logger.error(f"Failed to load zero-shot classifier: {e}")
                raise e
            finally:
                self._zero_shot_loading = False
    
    def _load_emotion_model(self):
        """Load emotion detector on first use"""
        if self.emotion_detector is None and not self._emotion_loading:
            self._emotion_loading = True
            try:
                logger.info("Loading emotion detection model: j-hartmann/emotion-english-distilroberta-base")
                self.emotion_detector = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    device=-1,
                    top_k=5  # Return top 5 emotion scores for efficiency
                )
                logger.info("✓ Emotion detector loaded")
            except Exception as e:
                logger.error(f"Failed to load emotion detector: {e}")
                # Fallback to default sentiment as emotion proxy
                try:
                    logger.info("Falling back to sentiment analysis for emotions")
                    self.emotion_detector = pipeline("sentiment-analysis", device=-1)
                    logger.info("✓ Using sentiment as emotion fallback")
                except Exception:
                    raise e
            finally:
                self._emotion_loading = False
    
    def is_loaded(self) -> bool:
        """Check if any models are loaded"""
        return any([
            self.sentiment_analyzer is not None,
            self.zero_shot_classifier is not None,
            self.emotion_detector is not None
        ])
    
    def get_sentiment_analyzer(self):
        """Get sentiment analyzer, loading if necessary"""
        self._load_sentiment_model()
        return self.sentiment_analyzer
    
    def get_zero_shot_classifier(self):
        """Get zero-shot classifier, loading if necessary"""
        self._load_zero_shot_model()
        return self.zero_shot_classifier
    
    def get_emotion_detector(self):
        """Get emotion detector, loading if necessary"""
        self._load_emotion_model()
        return self.emotion_detector
