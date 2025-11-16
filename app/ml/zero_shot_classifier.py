"""
Zero-Shot Classification Service
Classifies content into categories without training data
Used for categorizing browsing content (Productivity, Social, Entertainment, etc.)
"""

from typing import List, Dict
from loguru import logger

from app.ml.model_manager import ModelManager


class ZeroShotClassifier:
    """Service for zero-shot classification of content"""
    
    # Default categories for content classification
    DEFAULT_CATEGORIES = [
        # Productivity & Work
        "Productivity",
        "Work",
        "Professional Development",
        "Business",
        "Documentation",
        
        # Social & Communication
        "Social Media",
        "Communication",
        "Forums & Discussion",
        "Dating",
        
        # Entertainment & Media
        "Entertainment",
        "Music",
        "Movies & TV",
        "Gaming",
        "Sports",
        "Humor & Memes",
        "Podcasts",
        "Streaming",
        
        # News & Information
        "News",
        "Politics",
        "World Events",
        "Science",
        "Technology",
        "Research",
        
        # Education & Learning
        "Education",
        "Online Courses",
        "Tutorials",
        "Academic",
        "Programming",
        "Self-Improvement",
        
        # Lifestyle & Personal
        "Health & Wellness",
        "Fitness",
        "Food & Cooking",
        "Travel",
        "Hobbies",
        "DIY & Crafts",
        "Fashion & Beauty",
        "Relationships",
        "Parenting",
        
        # Finance & Commerce
        "Finance",
        "Shopping",
        "E-commerce",
        "Banking",
        "Investing",
        "Cryptocurrency",
        
        # Reference & Tools
        "Reference",
        "Tools & Utilities",
        "Software",
        "Documentation",
        "Search",
        
        # Negative/Problematic Content
        "Adult Content",
        "Violence",
        "Misinformation",
        "Harassment",
        
        # Default
        "Other"
    ]
    
    def __init__(self):
        self.model_manager = ModelManager()
    
    def classify(
        self,
        text: str,
        categories: List[str] = None,
        multi_label: bool = False
    ) -> Dict[str, any]:
        """
        Classify text into one or more categories
        
        Args:
            text: Text content to classify
            categories: List of possible categories (uses DEFAULT_CATEGORIES if None)
            multi_label: Whether to allow multiple categories (default: False)
        
        Returns:
            Dictionary with labels and scores
            Example: {"labels": ["Productivity", "Technology"], "scores": [0.95, 0.85]}
        """
        if not text or len(text.strip()) == 0:
            return {"labels": ["Other"], "scores": [1.0], "error": "Empty text"}
        
        if categories is None:
            categories = self.DEFAULT_CATEGORIES
        
        try:
            model = self.model_manager.get_zero_shot_classifier()
            
            # Truncate text if too long
            max_length = 512
            if len(text.split()) > max_length:
                text = ' '.join(text.split()[:max_length])
                logger.warning(f"Text truncated to {max_length} words for classification")
            
            result = model(
                text,
                candidate_labels=categories,
                multi_label=multi_label
            )
            
            logger.debug(f"Classification: {result['labels'][0]} ({result['scores'][0]:.2f})")
            
            return {
                "labels": result['labels'],
                "scores": result['scores']
            }
            
        except Exception as e:
            logger.error(f"Zero-shot classification failed: {e}")
            return {"labels": ["Other"], "scores": [1.0], "error": str(e)}
    
    def classify_productivity(self, text: str) -> Dict[str, any]:
        """
        Classify if content is productive or distracting
        
        Args:
            text: Text content to classify
        
        Returns:
            Dictionary with productivity classification
        """
        categories = ["Productive", "Distracting"]
        return self.classify(text, categories=categories)
    
    def get_category_groups(self) -> Dict[str, List[str]]:
        """
        Return categories organized by broad groups for dashboard analytics
        
        Returns:
            Dictionary mapping group names to lists of categories
        """
        return {
            "Productive": [
                "Productivity", "Work", "Professional Development", "Business", 
                "Documentation", "Education", "Online Courses", "Tutorials", 
                "Academic", "Programming", "Research", "Reference", "Tools & Utilities"
            ],
            "Social": [
                "Social Media", "Communication", "Forums & Discussion", "Dating"
            ],
            "Entertainment": [
                "Entertainment", "Music", "Movies & TV", "Gaming", "Sports", 
                "Humor & Memes", "Podcasts", "Streaming"
            ],
            "Information": [
                "News", "Politics", "World Events", "Science", "Technology"
            ],
            "Lifestyle": [
                "Health & Wellness", "Fitness", "Food & Cooking", "Travel", 
                "Hobbies", "DIY & Crafts", "Fashion & Beauty", "Relationships", 
                "Parenting", "Self-Improvement"
            ],
            "Commerce": [
                "Finance", "Shopping", "E-commerce", "Banking", "Investing", "Cryptocurrency"
            ],
            "Problematic": [
                "Adult Content", "Violence", "Misinformation", "Harassment"
            ],
            "Other": ["Other", "Search", "Software"]
        }
    
    def classify_with_group(self, text: str) -> Dict[str, any]:
        """
        Classify text and also return the broad category group
        
        Args:
            text: Text content to classify
            
        Returns:
            Dictionary with classification and group information
        """
        result = self.classify(text)
        if result.get("error"):
            return result
            
        # Find the group for the top category
        groups = self.get_category_groups()
        top_category = result["labels"][0]
        category_group = "Other"
        
        for group, categories in groups.items():
            if top_category in categories:
                category_group = group
                break
                
        result["category_group"] = category_group
        return result
