import random
from datetime import datetime

class AICreativeSuggestor:
    def __init__(self):
        self.creative_templates = self.load_templates()
        self.color_palettes = self.load_color_palettes()
    
    def load_templates(self):
        """Load AI-generated creative templates"""
        return {
            "premium": {
                "name": "Premium Layout",
                "description": "Clean, professional layout with premium styling",
                "best_for": ["alcohol", "luxury", "premium"],
                "engagement_score": 88
            },
            "minimal": {
                "name": "Minimal Layout", 
                "description": "Simple, clean design with focus on product",
                "best_for": ["general", "electronics", "fashion"],
                "engagement_score": 85
            },
            "vibrant": {
                "name": "Vibrant Layout",
                "description": "Eye-catching design with bold colors",
                "best_for": ["youth", "entertainment", "events"],
                "engagement_score": 92
            }
        }
    
    def load_color_palettes(self):
        """Load brand-compliant color palettes"""
        return {
            "tesco_blue": {
                "primary": "#00539F",
                "secondary": "#BFE0F5", 
                "accent": "#FFFFFF",
                "text": "#333333",
                "background": "#F8F9FA"
            },
            "premium_gold": {
                "primary": "#FFD700",
                "secondary": "#000000",
                "accent": "#FFFFFF", 
                "text": "#333333",
                "background": "#1A1A1A"
            },
            "fresh_green": {
                "primary": "#228B22",
                "secondary": "#90EE90",
                "accent": "#FFFFFF",
                "text": "#333333",
                "background": "#F0FFF0"
            }
        }
    
    def generate_variations(self, headline, subhead, packshot, value_tile_type):
        """Generate creative variations with AI suggestions"""
        variations = []
        
        templates = list(self.creative_templates.keys())
        
        for i, template in enumerate(templates[:3]):  # Limit to 3 variations
            variation = {
                'id': f"var_{i+1}",
                'template': template,
                'description': self.creative_templates[template]['description'],
                'confidence_score': 80 + (i * 5),
                'performance_prediction': self._predict_performance(template),
                'ai_suggestions': self._get_template_suggestions(template),
                'timestamp': datetime.now()
            }
            variations.append(variation)
        
        return variations
    
    def suggest_copy_improvements(self, headline, subhead, product_type):
        """Suggest copy improvements based on guidelines"""
        suggestions = []
        
        # Length optimization
        headline_length = len(headline)
        if headline_length > 60:
            suggestions.append("Consider shortening headline to under 60 characters for better readability")
        elif headline_length < 10:
            suggestions.append("Headline might be too short - consider adding more descriptive text")
        
        # Product-type specific suggestions
        if product_type.lower() == "alcohol":
            suggestions.append("Ensure no health claims or promotional language")
            suggestions.append("Include Drinkaware logo and maintain minimum 20px font size")
        
        elif product_type.lower() == "electronics":
            suggestions.append("Focus on features and specifications rather than promotional language")
        
        # General best practices
        suggestions.append("Use clear, benefit-oriented language")
        suggestions.append("Avoid complex claims or asterisks")
        suggestions.append("Ensure high contrast between text and background")
        
        return suggestions
    
    def predict_performance(self, creative_elements, target_platform):
        """Predict performance metrics for the creative"""
        base_score = 75
        
        # Factor adjustments
        factors = {
            "headline_optimization": self._score_headline(creative_elements.get('headline', '')),
            "value_tile_presence": 10 if creative_elements.get('has_value_tile') else 0,
            "image_quality": 8,
            "platform_optimization": 5
        }
        
        final_score = base_score + sum(factors.values())
        
        return {
            "engagement_score": min(100, int(final_score)),
            "click_through_prediction": f"{min(10, final_score/10):.1f}%",
            "conversion_likelihood": "High" if final_score > 85 else "Medium" if final_score > 70 else "Low",
            "performance_grade": self._get_performance_grade(final_score)
        }
    
    def _predict_performance(self, template):
        """Predict performance for template"""
        performance_scores = {
            "premium": 88,
            "minimal": 85,
            "vibrant": 92
        }
        return performance_scores.get(template, 85)
    
    def _get_template_suggestions(self, template):
        """Get AI suggestions for template"""
        suggestions = {
            "premium": [
                "Use high-quality product imagery",
                "Maintain generous white space",
                "Focus on premium color schemes"
            ],
            "minimal": [
                "Keep design clean and uncluttered",
                "Use minimal color palette",
                "Focus on essential elements only"
            ],
            "vibrant": [
                "Use bold, contrasting colors",
                "Incorporate dynamic elements",
                "Focus on emotional appeal"
            ]
        }
        return suggestions.get(template, [])
    
    def _score_headline(self, headline):
        """Score headline quality"""
        if not headline:
            return 0
        
        score = 0
        length = len(headline)
        
        # Length scoring
        if 20 <= length <= 60:
            score += 8
        elif 10 <= length < 20 or 60 < length <= 80:
            score += 5
        else:
            score += 2
        
        return score
    
    def _get_performance_grade(self, score):
        """Convert score to performance grade"""
        if score >= 90: return "A+"
        elif score >= 85: return "A"
        elif score >= 80: return "A-"
        elif score >= 75: return "B+"
        elif score >= 70: return "B"
        elif score >= 65: return "B-"
        else: return "C"
    
    def get_trending_designs(self, product_category):
        """Get trending design patterns"""
        trends = {
            "Alcohol": {
                "styles": ["Premium aesthetic", "Clean layouts", "Sophisticated typography"],
                "colors": ["Deep tones", "Metallic accents", "Rich backgrounds"],
                "recommendations": ["Focus on quality messaging", "Use premium imagery"]
            },
            "Electronics": {
                "styles": ["Modern tech", "Feature highlights", "Minimalist"],
                "colors": ["Blue gradients", "Dark themes", "Metallic accents"],
                "recommendations": ["Highlight specifications", "Use lifestyle context"]
            },
            "General": {
                "styles": ["Professional", "Clean", "Engaging"],
                "colors": ["Brand colors", "High contrast", "Accessible"],
                "recommendations": ["Clear value propositions", "Strong visual hierarchy"]
            }
        }
        
        return trends.get(product_category, trends["General"])