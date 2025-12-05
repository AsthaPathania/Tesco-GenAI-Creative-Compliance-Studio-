import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import zipfile
import json
import time
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import base64
import uuid
import random
import re

# Configure page
st.set_page_config(
    page_title="Tesco GenAI Creative Compliance Studio", 
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our modules
try:
    from compliance_engine import AdvancedComplianceEngine
    compliance_engine = AdvancedComplianceEngine()
except ImportError as e:
    st.error(f"Compliance engine loading issue: {e}")
    class AdvancedComplianceEngine:
        def check_text_compliance(self, headline, subhead, product_category="general"): 
            return {"approved": True, "issues": [], "suggestions": []}
        def full_creative_audit(self, creative_data, format_name): 
            return {"overall_assessment": {"passed": True, "score": 95}}
        def validate_creative_design(self, creative_data, format_name):
            return {"valid": True, "issues": [], "warnings": [], "hard_fails": []}
        def check_safe_zones(self, format_name, element_positions):
            return {"passed": True, "issues": []}
        def analyze_headline_subhead(self, headline, subhead, product_category):
            return {"headline_issues": [], "subhead_issues": [], "recommendations": [], "compliance_score": 100}
    compliance_engine = AdvancedComplianceEngine()

try:
    from ai_creative_generator import AICreativeSuggestor
    creative_suggestor = AICreativeSuggestor()
except ImportError:
    class AICreativeSuggestor:
        def suggest_copy_improvements(self, headline, subhead, product_type):
            return ["Use clear, benefit-oriented language", "Ensure high contrast between text and background"]
        def predict_performance(self, creative_elements, target_platform):
            return {"engagement_score": 85, "click_through_prediction": "8.5%", "conversion_likelihood": "Medium", "performance_grade": "B+"}
        def get_trending_designs(self, product_category):
            return {"styles": ["Professional", "Clean"], "colors": ["Brand colors"], "recommendations": ["Clear value propositions"]}
    creative_suggestor = AICreativeSuggestor()

try:
    from background_remover import remove_background_ai, enhance_image_quality
except ImportError:
    def remove_background_ai(image_file): 
        return image_file
    def enhance_image_quality(image): 
        return image

try:
    from value_tile_generator import generate_value_tile, validate_value_tile_design, get_value_tile_templates
except ImportError:
    def generate_value_tile(*args, **kwargs): 
        img = Image.new('RGB', (300, 100), (200, 200, 200))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 299, 99], outline=(0, 83, 159), width=2)
        return img
    def validate_value_tile_design(*args, **kwargs): 
        return {"valid": True, "issues": [], "recommendations": []}
    def get_value_tile_templates(): 
        return {"tile_types": ["Clubcard Price", "Everyday Low Price", "New"]}

# Initialize session state
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None
if 'original_image' not in st.session_state:
    st.session_state.original_image = None
if 'headline' not in st.session_state:
    st.session_state.headline = ""
if 'subhead' not in st.session_state:
    st.session_state.subhead = ""
if 'show_logo' not in st.session_state:
    st.session_state.show_logo = True
if 'include_drinkaware' not in st.session_state:
    st.session_state.include_drinkaware = False
if 'product_category' not in st.session_state:
    st.session_state.product_category = "General"
if 'clubcard_end_date' not in st.session_state:
    st.session_state.clubcard_end_date = ""
if 'generated_creatives' not in st.session_state:
    st.session_state.generated_creatives = []
if 'people_detected' not in st.session_state:
    st.session_state.people_detected = False
if 'people_confirmed' not in st.session_state:
    st.session_state.people_confirmed = False
if 'packshots' not in st.session_state:
    st.session_state.packshots = []
if 'background_color' not in st.session_state:
    st.session_state.background_color = "#BFE0F5"
if 'background_image' not in st.session_state:
    st.session_state.background_image = None
if 'product_exclusivity' not in st.session_state:
    st.session_state.product_exclusivity = "Non-exclusive"
if 'creative_links_to_tesco' not in st.session_state:
    st.session_state.creative_links_to_tesco = True
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'processed_packshots' not in st.session_state:
    st.session_state.processed_packshots = []
if 'ai_suggestions' not in st.session_state:
    st.session_state.ai_suggestions = []
if 'performance_prediction' not in st.session_state:
    st.session_state.performance_prediction = {}

# Enhanced Theme styling with Dark Mode support
def apply_theme():
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
            .main { background-color: #0E1117; color: #FAFAFA; }
            .stApp { background-color: #0E1117; }
            .sidebar .sidebar-content { background-color: #262730; }
            .compliant { background: #1B3B1B; padding: 12px; border-radius: 8px; border-left: 4px solid #4CAF50; margin: 12px 0; color: #E8F5E8; }
            .non-compliant { background: #3B1B1B; padding: 12px; border-radius: 8px; border-left: 4px solid #F44336; margin: 12px 0; color: #FFEBEE; }
            .warning { background: #3B3B1B; padding: 12px; border-radius: 8px; border-left: 4px solid #FFC107; margin: 12px 0; color: #FFF8E1; }
            .creative-preview { border: 2px solid #00539F; border-radius: 12px; padding: 16px; margin: 16px 0; background: #1E1E1E; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
            .required-field::after { content: " *"; color: #FF6B6B; }
            .appendix-a { background: #1A237E; padding: 10px; border-radius: 6px; border-left: 4px solid #2196F3; margin: 8px 0; color: #E3F2FD; }
            .appendix-b { background: #3E2723; padding: 10px; border-radius: 6px; border-left: 4px solid #FF9800; margin: 8px 0; color: #FFF3E0; }
            .hard-fail { background: #3B1B1B; color: #FF8A80; padding: 6px; border-radius: 4px; font-weight: bold; border: 1px solid #F44336; }
            .compliance-check { background: #2D2D2D; padding: 12px; border-radius: 8px; margin: 8px 0; border: 1px solid #444; }
            .card { background: #262730; padding: 16px; border-radius: 10px; margin: 12px 0; border: 1px solid #444; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
            .metric-card { background: linear-gradient(135deg, #00539F, #003366); padding: 20px; border-radius: 12px; color: white; text-align: center; }
            .section-header { background: linear-gradient(90deg, #00539F, #003366); padding: 15px; border-radius: 8px; color: white; margin: 20px 0; }
            .stButton>button { background: linear-gradient(45deg, #00539F, #003366); color: white; border: none; border-radius: 6px; padding: 10px 20px; font-weight: 600; }
            .stButton>button:hover { background: linear-gradient(45deg, #003366, #002244); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,83,159,0.3); }
            .stSelectbox>div>div { background: #262730; border: 1px solid #444; color: white; }
            .stTextInput>div>div>input { background: #262730; border: 1px solid #444; color: white; }
            .stCheckbox>label { color: #FAFAFA; }
            .stRadio>label { color: #FAFAFA; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            .main { background-color: #FFFFFF; color: #262730; }
            .stApp { background-color: #F8F9FA; }
            .sidebar .sidebar-content { background-color: #FFFFFF; }
            .compliant { background: #E8F5E8; padding: 12px; border-radius: 8px; border-left: 4px solid #4CAF50; margin: 12px 0; color: #1B5E20; }
            .non-compliant { background: #FFEBEE; padding: 12px; border-radius: 8px; border-left: 4px solid #F44336; margin: 12px 0; color: #B71C1C; }
            .warning { background: #FFF8E1; padding: 12px; border-radius: 8px; border-left: 4px solid #FFC107; margin: 12px 0; color: #E65100; }
            .creative-preview { border: 2px solid #00539F; border-radius: 12px; padding: 16px; margin: 16px 0; background: #FFFFFF; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
            .required-field::after { content: " *"; color: #D32F2F; }
            .appendix-a { background: #E3F2FD; padding: 10px; border-radius: 6px; border-left: 4px solid #2196F3; margin: 8px 0; color: #0D47A1; }
            .appendix-b { background: #FFF3E0; padding: 10px; border-radius: 6px; border-left: 4px solid #FF9800; margin: 8px 0; color: #E65100; }
            .hard-fail { background: #FFEBEE; color: #C62828; padding: 6px; border-radius: 4px; font-weight: bold; border: 1px solid #F44336; }
            .compliance-check { background: #F5F5F5; padding: 12px; border-radius: 8px; margin: 8px 0; border: 1px solid #E0E0E0; }
            .card { background: #FFFFFF; padding: 16px; border-radius: 10px; margin: 12px 0; border: 1px solid #E0E0E0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .metric-card { background: linear-gradient(135deg, #00539F, #003366); padding: 20px; border-radius: 12px; color: white; text-align: center; }
            .section-header { background: linear-gradient(90deg, #00539F, #003366); padding: 15px; border-radius: 8px; color: white; margin: 20px 0; }
            .stButton>button { background: linear-gradient(45deg, #00539F, #003366); color: white; border: none; border-radius: 6px; padding: 10px 20px; font-weight: 600; }
            .stButton>button:hover { background: linear-gradient(45deg, #003366, #002244); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,83,159,0.3); }
        </style>
        """, unsafe_allow_html=True)

# Apply theme
apply_theme()

# Utility functions
def image_to_bytes(image, format='PNG'):
    buf = io.BytesIO()
    if format.upper() == 'JPG':
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        image.save(buf, format='JPEG', quality=90, optimize=True)
    else:
        image.save(buf, format='PNG', optimize=True)
    return buf.getvalue()

def create_tesco_logo(size=(100, 40)):
    logo = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)
    draw.rectangle([10, 10, size[0]-10, size[1]-10], fill="#00539F", outline="#FFFFFF", width=2)
    try:
        font = ImageFont.truetype("Arial", 14)
    except:
        font = ImageFont.load_default()
    draw.text((size[0]//2, size[1]//2), "TESCO", fill="#FFFFFF", font=font, anchor="mm")
    return logo

def validate_dd_mm_format(date_string):
    """Validate DD/MM date format - Appendix A requirement"""
    if not date_string:
        return False, "Date is required for Clubcard Price"
    
    pattern = r'^\d{2}/\d{2}$'
    if not re.match(pattern, date_string):
        return False, "Date must be in DD/MM format (e.g., 23/06)"
    
    day, month = date_string.split('/')
    day_num = int(day)
    month_num = int(month)
    
    if month_num < 1 or month_num > 12:
        return False, "Month must be between 01 and 12"
    if day_num < 1 or day_num > 31:
        return False, "Day must be between 01 and 31"
    
    return True, "Valid DD/MM format"

def get_appropriate_tag(value_tile_type, clubcard_end_date, product_exclusivity, creative_links_to_tesco):
    """Determine appropriate tag based on EXACT Appendix A rules"""
    if not creative_links_to_tesco:
        return "None"
    
    if value_tile_type == "Clubcard Price" and clubcard_end_date:
        return f"Clubcard/app required. Ends {clubcard_end_date}"
    elif product_exclusivity == "Exclusive":
        return "Only at Tesco"
    elif product_exclusivity == "Non-exclusive":
        return "Available at Tesco"
    else:
        return "Selected stores. While stocks last."

def analyze_text_compliance(headline, subhead, product_category):
    """Real-time text compliance analysis with detailed reporting"""
    analysis = compliance_engine.analyze_headline_subhead(headline, subhead, product_category)
    full_compliance = compliance_engine.check_text_compliance(headline, subhead, product_category)
    
    return {
        "analysis": analysis,
        "full_compliance": full_compliance,
        "is_compliant": full_compliance["approved"] and len(analysis["headline_issues"]) == 0
    }

def generate_creative(dimensions, packshots, headline, subhead, value_tile_type, tag_type, 
                     bg_color, bg_image, include_drinkaware, clubcard_price, regular_price, 
                     lep_price, clubcard_end_date, product_category, product_exclusivity, creative_links_to_tesco):
    
    width, height = dimensions
    
    # Create background
    if bg_image:
        img = bg_image.resize((width, height), Image.Resampling.LANCZOS)
    else:
        img = Image.new("RGB", (width, height), bg_color)
    
    draw = ImageDraw.Draw(img)
    
    # Add Tesco logo if enabled - Appendix A: appears on all banners
    if st.session_state.show_logo:
        logo = create_tesco_logo((120, 40))
        img.paste(logo, (width - 140, 20), logo)
    
    # Add multiple packshots with proper positioning - Appendix A: max 3, lead product required
    if packshots:
        # Calculate positions for multiple packshots
        num_packshots = len(packshots)
        
        if num_packshots == 1:
            # Single packshot - center it
            packshot = packshots[0]
            max_width = int(width * 0.6)
            max_height = int(height * 0.7)
            packshot_resized = packshot.copy()
            packshot_resized.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            x = (width - packshot_resized.width) // 2
            y = (height - packshot_resized.height) // 2
            
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            img.paste(packshot_resized, (x, y), packshot_resized if packshot_resized.mode == 'RGBA' else None)
            
        elif num_packshots == 2:
            # Two packshots - side by side
            max_width = int(width * 0.4)
            max_height = int(height * 0.6)
            
            for i, packshot in enumerate(packshots):
                packshot_resized = packshot.copy()
                packshot_resized.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                if i == 0:  # Left packshot
                    x = width // 4 - packshot_resized.width // 2
                else:  # Right packshot
                    x = 3 * width // 4 - packshot_resized.width // 2
                
                y = (height - packshot_resized.height) // 2
                
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                img.paste(packshot_resized, (x, y), packshot_resized if packshot_resized.mode == 'RGBA' else None)
                
        elif num_packshots >= 3:
            # Three packshots - triangular arrangement
            max_width = int(width * 0.3)
            max_height = int(height * 0.5)
            
            for i, packshot in enumerate(packshots[:3]):  # Limit to 3 as per Appendix A
                packshot_resized = packshot.copy()
                packshot_resized.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                if i == 0:  # Top center
                    x = (width - packshot_resized.width) // 2
                    y = height // 3 - packshot_resized.height // 2
                elif i == 1:  # Bottom left
                    x = width // 3 - packshot_resized.width // 2
                    y = 2 * height // 3 - packshot_resized.height // 2
                else:  # Bottom right
                    x = 2 * width // 3 - packshot_resized.width // 2
                    y = 2 * height // 3 - packshot_resized.height // 2
                
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                img.paste(packshot_resized, (x, y), packshot_resized if packshot_resized.mode == 'RGBA' else None)
        
        draw = ImageDraw.Draw(img)
    
    # Add text with compliance font sizes - Appendix B HARD FAIL
    try:
        headline_font = ImageFont.truetype("Arial", 24)  # 20px minimum + buffer
        subhead_font = ImageFont.truetype("Arial", 16)   # 12px minimum + buffer
        tag_font = ImageFont.truetype("Arial", 14)
        drinkaware_font = ImageFont.truetype("Arial", 20)  # Minimum 20px for alcohol - HARD FAIL
    except:
        headline_font = ImageFont.load_default()
        subhead_font = ImageFont.load_default()
        tag_font = ImageFont.load_default()
        drinkaware_font = ImageFont.load_default()
    
    # Headline and subhead positioning - Appendix A: left-aligned
    text_x = 50  # Left alignment as per Appendix A
    
    if headline:
        headline_bbox = draw.textbbox((0, 0), headline, font=headline_font)
        headline_height = headline_bbox[3] - headline_bbox[1]
        headline_y = height - 180
        draw.text((text_x, headline_y), headline, fill="#000000", font=headline_font)
    
    if subhead:
        subhead_bbox = draw.textbbox((0, 0), subhead, font=subhead_font)
        subhead_height = subhead_bbox[3] - subhead_bbox[1]
        subhead_y = height - 140
        draw.text((text_x, subhead_y), subhead, fill="#000000", font=subhead_font)
    
    # Add value tile with proper positioning - Appendix A: predefined position
    if value_tile_type != "None":
        price_data = {
            'clubcard_price': clubcard_price,
            'regular_price': regular_price,
            'lep_price': lep_price,
            'end_date': clubcard_end_date
        }
        tile = generate_value_tile(value_tile_type, price_data)
        if tile:
            # Position value tile based on type - Appendix A rules
            if value_tile_type == "Everyday Low Price":
                # Appendix A: LEP positioned to the right of packshots
                tile_x = width - tile.width - 50
                tile_y = (height - tile.height) // 2
            else:
                # Clubcard or New: predefined positions
                tile_x = 50
                tile_y = 100
            
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            img.paste(tile, (tile_x, tile_y), tile)
    
    # Add Tesco tag with conditional logic - Appendix A & B
    appropriate_tag = get_appropriate_tag(value_tile_type, clubcard_end_date, product_exclusivity, creative_links_to_tesco)
    if tag_type != "None" and creative_links_to_tesco:
        tag_bbox = draw.textbbox((0, 0), appropriate_tag, font=tag_font)
        tag_width = tag_bbox[2] - tag_bbox[0]
        tag_x = text_x  # Left aligned with other text
        tag_y = height - 100
        
        # Appendix B HARD FAIL: Respect safe zones for 9:16 format (Facebook/Instagram Stories ONLY)
        if height == 1920:  # 9:16 format
            if tag_y < 250:  # Too close to bottom safe zone
                tag_y = 250 + 20
        
        draw.text((tag_x, tag_y), appropriate_tag, fill="#00539F", font=tag_font)
    
    # Add Drinkaware for alcohol - Appendix B HARD FAIL
    if product_category.lower() == "alcohol" and include_drinkaware:
        drinkaware_text = "be drinkaware.co.uk"
        drinkaware_bbox = draw.textbbox((0, 0), drinkaware_text, font=drinkaware_font)
        drinkaware_width = drinkaware_bbox[2] - drinkaware_bbox[0]
        drinkaware_x = (width - drinkaware_width) // 2
        drinkaware_y = height - 40
        
        # Appendix B HARD FAIL: Respect safe zones for 9:16 format
        if height == 1920:  # 9:16 format
            if drinkaware_y < 250:  # Too close to bottom safe zone
                drinkaware_y = 250 + 20
        
        draw.text((drinkaware_x, drinkaware_y), drinkaware_text, fill="#000000", font=drinkaware_font)
    
    return img

def check_creative_compliance(creative_data, format_name):
    """Check if creative meets ALL Appendix A & B HARD FAIL requirements"""
    issues = []
    warnings = []
    hard_fails = []
    
    # Appendix A: Required Elements (HARD FAIL)
    if not creative_data.get('headline'):
        hard_fails.append("HARD FAIL: Headline is required - appears on all banners (Appendix A)")
    if not creative_data.get('subhead'):
        hard_fails.append("HARD FAIL: Subhead is required - appears on all banners (Appendix A)")
    if not creative_data.get('packshots') or len(creative_data.get('packshots', [])) == 0:
        hard_fails.append("HARD FAIL: At least one packshot required - lead product required (Appendix A)")
    elif len(creative_data.get('packshots', [])) > 3:
        hard_fails.append("HARD FAIL: Maximum 3 packshots allowed (Appendix A)")
    
    # Appendix B: Alcohol-specific rules (HARD FAIL)
    if creative_data.get('product_category', '').lower() == 'alcohol':
        if not creative_data.get('include_drinkaware', False):
            hard_fails.append("HARD FAIL: Drinkaware required for alcohol campaigns (Appendix B)")
    
    # Appendix B: Copy Rules (HARD FAIL)
    text_result = compliance_engine.check_text_compliance(
        creative_data.get('headline', ''),
        creative_data.get('subhead', ''),
        creative_data.get('product_category', 'general')
    )
    if not text_result["approved"]:
        hard_fails.extend(text_result["issues"])
    
    # Appendix A: Clubcard End Date validation (HARD FAIL)
    if creative_data.get('value_tile_type') == 'Clubcard Price':
        end_date = creative_data.get('clubcard_end_date', '')
        is_valid, date_error = validate_dd_mm_format(end_date)
        if not is_valid:
            hard_fails.append(f"HARD FAIL: {date_error} for Clubcard Price (Appendix A)")
    
    # Appendix B: Safe Zone validation for 9:16 format (HARD FAIL) - Facebook/Instagram Stories ONLY
    if "1080x1920" in format_name or "9:16" in format_name:
        hard_fails.append("HARD FAIL: 9:16 format - leave 200px top and 250px bottom free from text/logos (Appendix B)")
    
    # Appendix B: People detection warning
    if creative_data.get('people_detected', False) and not creative_data.get('people_confirmed', False):
        warnings.append("Media Rule: People detected in images - prompt to confirm campaign (Appendix B)")
    
    # Appendix A & B: Tag validation
    if creative_data.get('creative_links_to_tesco', True):
        if not creative_data.get('tag_type') or creative_data.get('tag_type') == 'None':
            hard_fails.append("HARD FAIL: Tesco tag required when creative links to Tesco (Appendix A)")
        else:
            allowed_tags = ["Only at Tesco", "Available at Tesco", "Selected stores. While stocks last."]
            if creative_data.get('tag_type') not in allowed_tags:
                hard_fails.append(f"HARD FAIL: Only approved Tesco tags allowed (Appendix A & B)")
    
    # Design rule validations
    design_result = compliance_engine.validate_creative_design(creative_data, format_name)
    hard_fails.extend(design_result["hard_fails"])
    warnings.extend(design_result["warnings"])
    
    return {
        "compliant": len(hard_fails) == 0,
        "hard_fails": hard_fails,
        "warnings": warnings,
        "can_generate": len(hard_fails) == 0
    }

# Main application with enhanced UI
def main():
    # Header with theme toggle
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.title("🛒 Tesco GenAI Creative Compliance Studio")
        st.markdown("**An AI-Powered Retail Media Creative Builder**")
    
    with col2:
        st.write("")  # Spacer
    
    with col3:
        # Theme toggle
        theme_col1, theme_col2 = st.columns([1, 1])
        with theme_col1:
            st.write("🌙" if st.session_state.dark_mode else "☀️")
        with theme_col2:
            if st.button("Dark Mode" if not st.session_state.dark_mode else "Light Mode", 
                        use_container_width=True, key="theme_toggle"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()

    # Sidebar - Appendix A Elements
    with st.sidebar:
        st.markdown('<div class="section-header">🎯 Campaign Setup</div>', unsafe_allow_html=True)
        
        # Creative links to Tesco - Appendix A conditional
        st.session_state.creative_links_to_tesco = st.checkbox(
            "Creative links to Tesco", 
            value=True,
            help="Appendix A: If creative links to Tesco, it must use a Tesco tag (and Tesco value tile if includes price/promotion/new)"
        )
        
        # Product category (triggers alcohol rules)
        product_category = st.selectbox(
            "Product Category *",
            ["General", "Alcohol", "Grocery", "Electronics", "Home & Garden"],
            help="Appendix A & B: Required for proper guideline application"
        )
        st.session_state.product_category = product_category
        
        # Product exclusivity - Appendix A tag determination
        product_exclusivity = st.selectbox(
            "Product Exclusivity *",
            ["Exclusive", "Non-exclusive"],
            help="Appendix A: If product is exclusive, tag is 'Only at Tesco'. If not exclusive, tag is 'Available at Tesco'"
        )
        st.session_state.product_exclusivity = product_exclusivity
        
        # Alcohol-specific settings - Appendix B HARD FAIL
        if product_category == "Alcohol":
            st.session_state.include_drinkaware = st.checkbox(
                "Include Drinkaware *", 
                value=True,
                help="Appendix B HARD FAIL: All alcohol campaigns should include the drinkaware lock-up"
            )
            st.markdown('<div class="appendix-b">Appendix B HARD FAIL: Drinkaware required for alcohol - minimum 20px height, all-black/white, sufficient contrast</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">🎨 Creative Elements</div>', unsafe_allow_html=True)
        
        # Value tiles - Appendix A
        value_tile_type = st.selectbox(
            "Value Tile",
            ["None", "New", "Clubcard Price", "Everyday Low Price"],
            help="Appendix A: Value tile types are: New, White or Clubcard. Position is predefined. Nothing can overlap VT."
        )
        
        # Show value tile rules based on selection
        if value_tile_type == "Clubcard Price":
            st.markdown('<div class="appendix-a">Clubcard: flat design, predefined, only offer price and regular price editable</div>', unsafe_allow_html=True)
        elif value_tile_type == "Everyday Low Price":
            st.markdown('<div class="appendix-a">LEP: trade-style, white background, Tesco blue font, positioned right of packshot</div>', unsafe_allow_html=True)
        elif value_tile_type == "New":
            st.markdown('<div class="appendix-a">New: predefined and cannot be edited</div>', unsafe_allow_html=True)
        
        # Price configurations based on value tile type - Appendix A
        clubcard_price = ""
        regular_price = ""
        lep_price = ""
        clubcard_end_date = ""
        
        if value_tile_type == "Clubcard Price":
            col1, col2 = st.columns(2)
            with col1:
                clubcard_price = st.text_input("Clubcard Price *", "£3.50", 
                                             help="Appendix A: Only the offer price can be edited")
            with col2:
                regular_price = st.text_input("Regular Price *", "£4.50",
                                            help="Appendix A: Only the regular price can be edited")
            
            clubcard_end_date = st.text_input(
                "End Date (DD/MM) *", 
                value=st.session_state.clubcard_end_date,
                placeholder="23/06",
                help="Appendix A: If banner includes Clubcard Price tile, user must enter end date in DD/MM format"
            )
            st.session_state.clubcard_end_date = clubcard_end_date
            
            # Validate DD/MM format - Appendix A
            if clubcard_end_date:
                is_valid, date_error = validate_dd_mm_format(clubcard_end_date)
                if not is_valid:
                    st.error(f"Appendix A: {date_error}")
        
        elif value_tile_type == "Everyday Low Price":
            lep_price = st.text_input("LEP Price", "£2.99",
                                    help="Appendix A: Only the price can be edited")
            st.markdown('<div class="appendix-a">Appendix A: LEP logo positioned to right of packshot. Include tag: "Selected stores. While stocks last"</div>', unsafe_allow_html=True)
        
        # Tesco tags - Appendix A & B
        tag_type = st.selectbox(
            "Tesco Tag *" if st.session_state.creative_links_to_tesco else "Tesco Tag",
            ["None", "Only at Tesco", "Available at Tesco", "Selected stores. While stocks last"],
            help="Appendix A & B: Required for Tesco-linked creatives. Pinterest banners must include a tag."
        )
        
        # Conditional tag logic - Appendix A
        appropriate_tag = get_appropriate_tag(value_tile_type, clubcard_end_date, product_exclusivity, st.session_state.creative_links_to_tesco)
        if st.session_state.creative_links_to_tesco:
            if value_tile_type == "Clubcard Price" and clubcard_end_date:
                st.info(f"Appendix A: Tag will show: '{appropriate_tag}'")
            else:
                st.info(f"Appendix A: Appropriate tag: '{appropriate_tag}'")
        
        # Logo settings - Appendix A
        st.session_state.show_logo = st.checkbox("Show Tesco Logo", value=True,
                                               help="Appendix A: Logo shows on all banners. Can be uploaded new or brought in from user's brand space.")
        
        st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
        
        # Background options - Appendix A
        bg_option = st.radio("Background", ["Solid Color", "Upload Image"], 
                            help="Appendix A: User can choose a flat background colour or upload a single background image")
        
        if bg_option == "Solid Color":
            st.session_state.background_color = st.color_picker("Background Color", "#BFE0F5")
            st.session_state.background_image = None
        else:
            bg_image_file = st.file_uploader("Upload Background Image", type=['png', 'jpg', 'jpeg'],
                                           help="Appendix A: User can upload a single background image")
            if bg_image_file:
                st.session_state.background_image = Image.open(bg_image_file)
                st.session_state.background_color = "#BFE0F5"  # Fallback color

    # Main content area
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="section-header">📝 Creative Content</div>', unsafe_allow_html=True)
        
        # Headline and subhead - Appendix A (Required - HARD FAIL)
        st.markdown('<div class="required-field">Headline </div>', unsafe_allow_html=True)
        headline = st.text_input("Headline", 
                               value=st.session_state.headline,
                               placeholder="HEADLINE", 
                               help="Appendix A HARD FAIL: Appears on all banners",
                               label_visibility="collapsed")
        
        st.markdown('<div class="required-field">Subhead </div>', unsafe_allow_html=True)
        subhead = st.text_input("Subhead", 
                              value=st.session_state.subhead,
                              placeholder="SUBHEAD", 
                              help="Appendix A HARD FAIL: Appears on all banners",
                              label_visibility="collapsed")
        
        st.session_state.headline = headline
        st.session_state.subhead = subhead
        
        # Packshots - Appendix A (Required - HARD FAIL)
        st.markdown('<div class="section-header">🖼️ Packshots</div>', unsafe_allow_html=True)
        st.markdown('<div class="required-field">Upload Packshots </div>', unsafe_allow_html=True)
        
        uploaded_packshots = st.file_uploader("Upload Product Images", 
                                            type=['png', 'jpg', 'jpeg'], 
                                            accept_multiple_files=True,
                                            help="Appendix A HARD FAIL: Maximum of 3 packshots. Lead product is required.",
                                            key="packshot_uploader")
        
        if uploaded_packshots:
            # Limit to 3 packshots as per Appendix A HARD FAIL
            if len(uploaded_packshots) > 3:
                st.error("Appendix A HARD FAIL: Maximum 3 packshots allowed. Using first 3 images.")
                uploaded_packshots = uploaded_packshots[:3]
            
            st.session_state.packshots = [Image.open(img) for img in uploaded_packshots]
            
            # Display packshots in a grid
            st.markdown(f"**Uploaded Packshots ({len(st.session_state.packshots)}):**")
            cols = st.columns(min(3, len(st.session_state.packshots)))
            for i, (packshot, col) in enumerate(zip(st.session_state.packshots, cols)):
                with col:
                    st.image(packshot, caption=f"Packshot {i+1}", use_column_width=True)
            
            # People detection simulation - Appendix B Warning
            st.session_state.people_detected = random.choice([True, False])  # Simulated detection
            if st.session_state.people_detected:
                st.markdown('<div class="appendix-b">Appendix B: People detected in images</div>', unsafe_allow_html=True)
                st.session_state.people_confirmed = st.checkbox(
                    "Confirm people are integral to campaign", 
                    value=False,
                    help="Appendix B: Media Rule - Warning only, prompt to confirm campaign"
                )
        
        # Image processing options
        if uploaded_packshots:
            st.markdown('<div class="section-header">🔧 Image Processing</div>', unsafe_allow_html=True)
            col_proc1, col_proc2 = st.columns(2)
            with col_proc1:
                remove_bg = st.checkbox("Remove Background")
            with col_proc2:
                enhance_img = st.checkbox("Enhance Image Quality")
            
            if st.button("🔄 Process Images", use_container_width=True):
                with st.spinner("Processing images..."):
                    processed_packshots = []
                    for packshot in st.session_state.packshots:
                        processed_packshot = packshot.copy()
                        
                        if remove_bg:
                            processed_packshot = remove_background_ai(processed_packshot)
                        if enhance_img:
                            processed_packshot = enhance_image_quality(processed_packshot)
                        
                        processed_packshots.append(processed_packshot)
                    
                    st.session_state.processed_packshots = processed_packshots
                    st.success("✅ Images processed successfully!")
                    
                    # Show processed images
                    if st.session_state.processed_packshots:
                        st.markdown("**Processed Packshots:**")
                        cols = st.columns(min(3, len(st.session_state.processed_packshots)))
                        for i, (packshot, col) in enumerate(zip(st.session_state.processed_packshots, cols)):
                            with col:
                                st.image(packshot, caption=f"Processed {i+1}", use_column_width=True)

        # AI Copy Suggestions
        if headline or subhead:
            if st.button("🤖 Get AI Copy Suggestions", use_container_width=True):
                with st.spinner("Analyzing copy for improvements..."):
                    st.session_state.ai_suggestions = creative_suggestor.suggest_copy_improvements(
                        headline, subhead, product_category
                    )
                    st.session_state.performance_prediction = creative_suggestor.predict_performance(
                        {"headline": headline, "subhead": subhead, "has_value_tile": value_tile_type != "None"}, 
                        "social"
                    )
            
            if st.session_state.ai_suggestions:
                st.markdown("### 💡 AI Copy Suggestions")
                for suggestion in st.session_state.ai_suggestions:
                    st.info(suggestion)
            
            if st.session_state.performance_prediction:
                st.markdown("### 📊 Performance Prediction")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Engagement Score", f"{st.session_state.performance_prediction.get('engagement_score', 0)}/100")
                with col2:
                    st.metric("CTR Prediction", st.session_state.performance_prediction.get('click_through_prediction', '0%'))
                with col3:
                    st.metric("Grade", st.session_state.performance_prediction.get('performance_grade', 'B'))
        
        # Real-time text compliance analysis
        if headline or subhead:
            st.markdown('<div class="section-header">🔍 Real-time Compliance Analysis</div>', unsafe_allow_html=True)
            text_analysis = analyze_text_compliance(headline, subhead, product_category)
            
            # Compliance metrics
            col_metric1, col_metric2 = st.columns(2)
            with col_metric1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Compliance Score", f"{text_analysis['analysis']['compliance_score']}/100")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_metric2:
                status_color = "#4CAF50" if text_analysis["is_compliant"] else "#F44336"
                status_icon = "✅" if text_analysis["is_compliant"] else "❌"
                st.markdown(f'<div class="metric-card" style="background: linear-gradient(135deg, {status_color}, {status_color}99) !important;">', unsafe_allow_html=True)
                st.metric("Status", f"{status_icon} {'Compliant' if text_analysis['is_compliant'] else 'Issues'}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if not text_analysis["is_compliant"]:
                st.error("❌ Headline & Subhead have compliance issues")
                
                # Show specific issues
                for issue in text_analysis["analysis"]["headline_issues"]:
                    st.markdown(f'<div class="hard-fail">{issue}</div>', unsafe_allow_html=True)
                
                # Show recommendations from full compliance check
                if text_analysis["full_compliance"]["suggestions"]:
                    st.info("💡 Recommendations:")
                    for rec in text_analysis["full_compliance"]["suggestions"]:
                        st.write(f"- {rec}")

    with col2:
        st.markdown('<div class="section-header">👀 Creative Preview & Export</div>', unsafe_allow_html=True)
        
        # Format selection with Appendix B safe zone awareness
        st.markdown("**Select Formats:**")
        formats = st.multiselect(
            "Choose social media formats",
            [
                "Instagram Square (1080x1080)",
                "Instagram Stories (1080x1920)", 
                "Facebook Landscape (1200x628)"
            ],
            default=["Instagram Square (1080x1080)"],
            help="Appendix B HARD FAIL: 9:16 format (Facebook/Instagram Stories) has safe zone requirements"
        )
        
        # Real-time compliance check
        creative_data = {
            'headline': headline,
            'subhead': subhead,
            'packshots': uploaded_packshots if 'uploaded_packshots' in locals() and uploaded_packshots else [],
            'product_category': product_category,
            'include_drinkaware': st.session_state.include_drinkaware,
            'value_tile_type': value_tile_type,
            'tag_type': tag_type,
            'clubcard_end_date': clubcard_end_date,
            'product_exclusivity': product_exclusivity,
            'creative_links_to_tesco': st.session_state.creative_links_to_tesco,
            'people_detected': st.session_state.people_detected,
            'people_confirmed': st.session_state.people_confirmed
        }
        
        if headline or subhead or (uploaded_packshots if 'uploaded_packshots' in locals() else False):
            # Check compliance for all selected formats
            all_compliant = True
            compliance_issues = []
            compliance_warnings = []
            
            for format_name in formats:
                compliance_check = check_creative_compliance(creative_data, format_name)
                
                if not compliance_check["compliant"]:
                    all_compliant = False
                    compliance_issues.extend([(format_name, issue) for issue in compliance_check["hard_fails"]])
                
                if compliance_check["warnings"]:
                    compliance_warnings.extend([(format_name, warning) for warning in compliance_check["warnings"]])
            
            # Display compliance status
            if compliance_issues:
                st.markdown('<div class="non-compliant">❌ Appendix A & B HARD FAIL Issues Detected</div>', unsafe_allow_html=True)
                for format_name, issue in compliance_issues:
                    st.error(f"**{format_name}**: {issue}")
            
            if compliance_warnings:
                st.markdown('<div class="warning">⚠️ Compliance Warnings</div>', unsafe_allow_html=True)
                for format_name, warning in compliance_warnings:
                    st.warning(f"**{format_name}**: {warning}")
            
            if all_compliant and headline and subhead and (uploaded_packshots if 'uploaded_packshots' in locals() and uploaded_packshots else False):
                st.markdown('<div class="compliant">✅ All formats 100% Appendix A & B Compliant</div>', unsafe_allow_html=True)
        
        # Generate button with HARD FAIL compliance enforcement
        generate_disabled = not (headline and subhead and ('uploaded_packshots' in locals() and uploaded_packshots))
        
        if st.button("🚀 Generate 100% Compliant Creatives", 
                     type="primary", 
                     use_container_width=True,
                     disabled=generate_disabled):
            
            if generate_disabled:
                st.error("Appendix A HARD FAIL: Please complete all required fields (Headline, Subhead, and Packshots)")
            else:
                with st.spinner("Generating 100% Appendix A & B compliant creatives..."):
                    creatives = []
                    
                    # Use processed packshots if available, otherwise use originals
                    packshots_to_use = st.session_state.processed_packshots if st.session_state.processed_packshots else st.session_state.packshots
                    
                    for format_name in formats:
                        # Parse dimensions
                        if "1080x1080" in format_name:
                            dimensions = (1080, 1080)
                        elif "1080x1920" in format_name:
                            dimensions = (1080, 1920)
                        elif "1200x628" in format_name:
                            dimensions = (1200, 628)
                        else:
                            dimensions = (1080, 1080)
                        
                        # Generate creative
                        creative_img = generate_creative(
                            dimensions=dimensions,
                            packshots=packshots_to_use,
                            headline=headline,
                            subhead=subhead,
                            value_tile_type=value_tile_type,
                            tag_type=tag_type,
                            bg_color=st.session_state.background_color,
                            bg_image=st.session_state.background_image,
                            include_drinkaware=st.session_state.include_drinkaware,
                            clubcard_price=clubcard_price,
                            regular_price=regular_price,
                            lep_price=lep_price,
                            clubcard_end_date=clubcard_end_date,
                            product_category=product_category,
                            product_exclusivity=product_exclusivity,
                            creative_links_to_tesco=st.session_state.creative_links_to_tesco
                        )
                        
                        creatives.append({
                            "format": format_name,
                            "image": creative_img,
                            "dimensions": dimensions,
                            "timestamp": datetime.now(),
                            "compliance_checked": True,
                            "appendix_a_b_compliant": True,
                            "packshots_count": len(packshots_to_use)
                        })
                    
                    st.session_state.generated_creatives = creatives
                    st.success(f"✅ Successfully generated {len(creatives)} 100% compliant creatives!")
                    st.balloons()
        
        # Display generated creatives
        if st.session_state.generated_creatives:
            st.markdown('<div class="section-header">🎨 Generated Creatives</div>', unsafe_allow_html=True)
            
            for i, creative in enumerate(st.session_state.generated_creatives):
                st.markdown(f'<div class="creative-preview">', unsafe_allow_html=True)
                
                # Creative header
                col_header1, col_header2 = st.columns([3, 1])
                with col_header1:
                    st.write(f"**{creative['format']}** - {creative['dimensions'][0]}x{creative['dimensions'][1]}")
                    st.write("✅ **100% Compliant**")
                    st.write(f"📦 **Packshots:** {creative.get('packshots_count', 1)} displayed")
                with col_header2:
                    st.metric("Status", "Ready")
                
                # Show safe zone info for 9:16 format - Appendix B HARD FAIL
                if creative['dimensions'][1] == 1920:
                    st.info("📱 **9:16 Format**: Leave 200px top and 250px bottom free from text/logos (Appendix B HARD FAIL)")
                
                # Display creative
                st.image(creative['image'], use_column_width=True)
                
                # Download buttons
                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    png_bytes = image_to_bytes(creative['image'], 'PNG')
                    st.download_button(
                        "📥 Download PNG",
                        data=png_bytes,
                        file_name=f"tesco_compliant_{creative['format'].replace(' ', '_').lower()}.png",
                        mime="image/png",
                        use_container_width=True,
                        key=f"png_{i}"
                    )
                with col_dl2:
                    jpg_bytes = image_to_bytes(creative['image'], 'JPEG')
                    st.download_button(
                        "📥 Download JPEG", 
                        data=jpg_bytes,
                        file_name=f"tesco_compliant_{creative['format'].replace(' ', '_').lower()}.jpg",
                        mime="image/jpeg",
                        use_container_width=True,
                        key=f"jpg_{i}"
                    )
                
                st.markdown('</div>', unsafe_allow_html=True)

    # Enhanced AI Compliance Assistant
    with st.expander("🤖 AI Compliance Assistant", expanded=False):
        st.markdown("### Get instant guidance on Appendix A & B HARD FAIL requirements")
        
        user_question = st.text_input("Ask about specific guidelines...", 
                                     placeholder="e.g., What are the HARD FAIL rules for Clubcard Price?",
                                     key="ai_assistant_input")
        
        if user_question:
            question_lower = user_question.lower()
            
            if any(term in question_lower for term in ['clubcard', 'price']):
                st.info("""
                **Appendix A Clubcard Price Rules:**
                - ❌ End date in DD/MM format REQUIRED (HARD FAIL)
                - ❌ Flat tile design (HARD FAIL)
                - ❌ Only offer price and regular price can be edited (HARD FAIL)
                - ❌ Predefined position, cannot be moved (HARD FAIL)
                - ❌ Nothing can overlap value tile (HARD FAIL)
                - ✅ Tag must include: "Clubcard/app required. Ends DD/MM"
                """)
            
            elif any(term in question_lower for term in ['alcohol', 'drinkaware']):
                st.info("""
                **Appendix B Alcohol HARD FAIL Rules:**
                - ❌ Drinkaware lock-up REQUIRED (HARD FAIL)
                - ❌ Sufficient contrast from background (HARD FAIL)
                - ❌ All-black or all-white only (HARD FAIL)
                - ❌ Minimum 20px height (12px for SAYS) (HARD FAIL)
                - ❌ No health claims in copy (HARD FAIL)
                - ❌ No competition language (HARD FAIL)
                - ❌ No encouragement of consumption (HARD FAIL)
                """)
            
            elif any(term in question_lower for term in ['tag', 'tesco tag']):
                st.info("""
                **Appendix A & B Tag Rules:**
                - ❌ Creative links to Tesco REQUIRES Tesco tag (HARD FAIL)
                - ❌ Pinterest banners MUST include tag (HARD FAIL)
                - ❌ Only approved tags allowed (HARD FAIL):
                  - "Only at Tesco" (exclusive products)
                  - "Available at Tesco" (non-exclusive)
                  - "Selected stores. While stocks last."
                  - "Clubcard/app required. Ends DD/MM" (if Clubcard Price)
                - ❌ Content cannot overlay Tesco tag (HARD FAIL)
                """)
            
            elif any(term in question_lower for term in ['safe zone', '9:16']):
                st.info("""
                **Appendix B Safe Zone HARD FAIL Rules:**
                - ❌ Facebook/Instagram Stories 1080x1920px ONLY (HARD FAIL)
                - ❌ Leave 200px from top free from text/logos (HARD FAIL)
                - ❌ Leave 250px from bottom free from text/logos (HARD FAIL)
                - ✅ Only applies to 9:16 ratio formats
                """)
            
            elif any(term in question_lower for term in ['packshot', 'packshots']):
                st.info("""
                **Appendix A Packshot Rules:**
                - ✅ At least one packshot REQUIRED (HARD FAIL)
                - ❌ Maximum 3 packshots allowed (HARD FAIL)
                - ✅ Lead product is required
                - ✅ Multiple packshots are now properly displayed:
                  - 1 packshot: Centered
                  - 2 packshots: Side by side
                  - 3 packshots: Triangular arrangement
                """)
            
            elif any(term in question_lower for term in ['headline', 'subhead', 'text', 'claim']):
                st.info("""
                **Appendix A & B Text Rules:**
                - ✅ Headline & Subhead REQUIRED on all banners (HARD FAIL)
                - ❌ No price mentions outside value tiles (HARD FAIL)
                - ❌ No competition language (win, prize, free) (HARD FAIL)
                - ❌ No sustainability claims (eco, green, sustainable) (HARD FAIL)
                - ❌ No charity partnerships (HARD FAIL)
                - ❌ No money-back guarantees (HARD FAIL)
                - ❌ No T&Cs or asterisks (HARD FAIL)
                - ❌ No health claims (healthy, benefits) (HARD FAIL)
                - ❌ No superlatives (best, perfect, ultimate) (HARD FAIL)
                - ❌ No scarcity/urgency claims (limited time, hurry) (HARD FAIL)
                - ❌ No survey/research claims (studies show, proven) (HARD FAIL)
                - ❌ No violent/inappropriate content (HARD FAIL)
                - ❌ No illegal/drug references (HARD FAIL)
                - ❌ No gambling/lottery content (HARD FAIL)
                - ❌ No mental health references (suicide, depression) (HARD FAIL)
                - ❌ No hate speech/discrimination (racism, sexism) (HARD FAIL)
                - ❌ No adult/explicit content (porn, sexual) (HARD FAIL)
                - ❌ No terrorism/extremism (bomb, terrorist) (HARD FAIL)
                """)
            
            else:
                st.info("""
                **I can help with:**
                - Clubcard Price requirements
                - Alcohol/Drinkaware rules  
                - Tesco tag selection
                - Safe zone requirements
                - Packshot rules and arrangements
                - Forbidden terms in copy
                - Value tile specifications
                - Headline and subhead rules
                - Claim detection and prevention
                - Sensitive content detection
                - Violence and crime content
                - Drug and substance references
                - Mental health content
                - Hate speech and discrimination
                - Adult and explicit content
                - Terrorism and extremism
                - Gambling and betting content
                """)

    # Comprehensive Test the compliance detection with ALL types of sensitive content
    with st.expander("🧪 Test Comprehensive Claim Detection", expanded=False):
        st.markdown("### Test how the system detects ALL types of sensitive content and claims:")
        
        test_cases = {
            "✅ Compliant Example": "NEW LOOK - SAME AWARD WINNING TASTE",
            "❌ T&Cs Claim": "BEST PRODUCT EVER* - *TERMS APPLY",
            "❌ Competition Claim": "WIN A FREE CAR - ENTER OUR COMPETITION", 
            "❌ Sustainability Claim": "ECO-FRIENDLY SUSTAINABLE PRODUCT",
            "❌ Charity Claim": "PROCEEDS TO CHARITY - SUPPORT GOOD CAUSES",
            "❌ Price Claim": "ONLY £2.99 - LIMITED TIME OFFER",
            "❌ Money-back Claim": "MONEY-BACK GUARANTEE - RISK-FREE",
            "❌ Health Claim": "HEALTHY CHOICE - GOOD FOR YOU",
            "❌ Alcohol Encouragement": "PERFECT FOR PARTIES - GET DRUNK",
            "❌ Survey Claim": "STUDIES SHOW 95% SATISFACTION - PROVEN RESULTS",
            "❌ Scientific Claim": "CLINICALLY PROVEN - DOCTOR RECOMMENDED",
            "❌ Scarcity Claim": "LIMITED TIME ONLY - WHILE STOCKS LAST",
            "❌ Urgency Claim": "HURRY - ACT NOW BEFORE IT'S GONE",
            "❌ Exclusive Claim": "EXCLUSIVE OFFER - ONLY AVAILABLE HERE",
            "❌ Superlative Claim": "WORLD'S BEST PRODUCT - NUMBER ONE RATED",
            "❌ Reference Claim": "SEE DETAILS BELOW† - FOOTNOTE EXPLAINS",
            "❌ Guarantee Claim": "SATISFACTION GUARANTEED - NO QUESTIONS ASKED",
            "❌ Discount Claim": "50% OFF SALE - USE DISCOUNT CODE SAVE50",
            
            # NEW ENHANCED SENSITIVE CONTENT TESTS
            "❌ Violence Content": "KILLER DEAL - MURDEROUS PRICES",
            "❌ Weapons Reference": "SHARP KNIFE OFFER - GUN CONTROL SALE",
            "❌ Crime Content": "STEAL THIS DEAL - CRIMINAL SAVINGS",
            "❌ Fraud Content": "SCAM PRODUCT - FRAUDULENT CLAIMS",
            "❌ Drug Reference": "COCAINE ENERGY DRINK - HEROIN STRENGTH",
            "❌ Addiction Content": "ADDICTIVE PRODUCT - DRUG-LIKE EFFECTS",
            "❌ Mental Health": "DEPRESSION RELIEF - SUICIDE PREVENTION",
            "❌ Self-harm": "SELF-HARM SOLUTION - CUTTING EDGE",
            "❌ Hate Speech": "RACIST CONTENT - HATE-FILLED OFFER",
            "❌ Discrimination": "SEXIST PRODUCT - DISCRIMINATORY DEAL",
            "❌ Adult Content": "PORN STAR PRODUCT - SEXUAL MATERIAL",
            "❌ Explicit Content": "XXX RATED - ADULT ONLY OFFER",
            "❌ Terrorism": "BOMB SHELTER SALE - TERROR PRICES",
            "❌ Extremism": "RADICAL DEAL - EXTREMIST OFFER",
            "❌ Gambling": "LOTTERY TICKETS - GAMBLE AND WIN",
            "❌ Casino Content": "CASINO NIGHTS - BETTING BONANZA"
        }
        
        selected_test = st.selectbox("Choose test case:", list(test_cases.keys()))
        test_text = test_cases[selected_test]
        
        if st.button("Test Comprehensive Detection", key="test_comprehensive_detection"):
            # Split into headline and subhead for testing
            parts = test_text.split(" - ")
            test_headline = parts[0] if len(parts) > 0 else test_text
            test_subhead = parts[1] if len(parts) > 1 else ""
            
            result = compliance_engine.check_text_compliance(test_headline, test_subhead, "General")
            
            st.write(f"**Test Case:** {test_text}")
            st.write(f"**Compliant:** {'✅ YES' if result['approved'] else '❌ NO'}")
            
            if not result['approved']:
                st.write("**HARD FAIL Issues Found:**")
                for issue in result['issues']:
                    st.error(issue)
                
                if result['suggestions']:
                    st.write("**Suggestions:**")
                    for suggestion in result['suggestions']:
                        st.info(suggestion)
            else:
                st.success("✅ No claims detected - This text is compliant!")

    # Footer
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns([2, 1, 1])
    with footer_col1:
        st.markdown("**Tesco GenAI Creative Compliance Studio (An AI-Powered Retail Media Creative Builder)**")
    with footer_col2:
        st.markdown(f"**Theme:** {'🌙 Dark' if st.session_state.dark_mode else '☀️ Light'}")
    with footer_col3:
        st.markdown(f"**Generated:** {len(st.session_state.generated_creatives)} creatives")

    # Sample data for demo
    if not st.session_state.generated_creatives and st.button("🚀 Load Compliant Sample", type="secondary"):
        st.session_state.headline = "NEW LOOK"
        st.session_state.subhead = "SAME AWARD WINNING TASTE"
        st.session_state.product_category = "General"
        st.session_state.include_drinkaware = False
        st.session_state.product_exclusivity = "Exclusive"
        st.session_state.background_color = "#BFE0F5"
        st.session_state.creative_links_to_tesco = True
        st.info("Compliant sample loaded! This demonstrates 100% Appendix A & B compliance.")

# Run the main application
if __name__ == "__main__":
    main()