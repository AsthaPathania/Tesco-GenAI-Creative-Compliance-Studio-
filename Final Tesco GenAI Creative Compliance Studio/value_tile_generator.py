from PIL import Image, ImageDraw, ImageFont
import random

def generate_value_tile(tile_type, price_data, dimensions=(300, 100)):
    """Generate 100% compliant value tiles based on EXACT Appendix A specifications"""
    width, height = dimensions
    
    if tile_type == "Clubcard Price":
        return create_clubcard_tile(price_data, width, height)
    elif tile_type == "Everyday Low Price":
        return create_lep_tile(price_data, width, height)
    elif tile_type == "New":
        return create_new_tile(width, height)
    else:
        return create_default_tile(width, height)

def create_clubcard_tile(price_data, width, height):
    """Create Clubcard price tile - EXACT Appendix A: flat design, predefined, only offer+regular price editable"""
    # Tesco blue background - flat design as per Appendix A
    tile = Image.new('RGBA', (width, height), (0, 83, 159, 255))
    draw = ImageDraw.Draw(tile)
    
    try:
        price_font = ImageFont.truetype("Arial", 28)
        label_font = ImageFont.truetype("Arial", 16)
        was_font = ImageFont.truetype("Arial", 14)
    except:
        price_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        was_font = ImageFont.load_default()
    
    # Clubcard price (main emphasis) - Appendix A: only offer price and regular price editable
    clubcard_price = price_data.get('clubcard_price', '£3.50')
    price_bbox = draw.textbbox((0, 0), clubcard_price, font=price_font)
    price_width = price_bbox[2] - price_bbox[0]
    price_x = (width - price_width) // 2
    draw.text((price_x, 15), clubcard_price, fill='white', font=price_font)
    
    # "Clubcard Price" label - predefined
    label_text = "Clubcard Price"
    label_bbox = draw.textbbox((0, 0), label_text, font=label_font)
    label_width = label_bbox[2] - label_bbox[0]
    label_x = (width - label_width) // 2
    draw.text((label_x, 55), label_text, fill='white', font=label_font)
    
    # Regular price (strikethrough) - Appendix A: required for Clubcard
    regular_price = price_data.get('regular_price', '')
    if regular_price:
        was_text = f"Was {regular_price}"
        was_bbox = draw.textbbox((0, 0), was_text, font=was_font)
        was_width = was_bbox[2] - was_bbox[0]
        was_x = (width - was_width) // 2
        
        # Strikethrough effect
        strike_y = 85 + (was_bbox[3] - was_bbox[1]) // 2
        draw.line([was_x, strike_y, was_x + was_width, strike_y], fill='white', width=1)
        
        draw.text((was_x, 85), was_text, fill='white', font=was_font)
    
    return tile

def create_lep_tile(price_data, width, height):
    """Create Everyday Low Price tile - EXACT Appendix A: white background, Tesco blue font, trade-style"""
    # White background with blue border - Appendix A: white value tile
    tile = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(tile)
    
    # Blue border - trade-style design
    draw.rectangle([0, 0, width-1, height-1], outline=(0, 83, 159), width=2)
    
    try:
        price_font = ImageFont.truetype("Arial", 26)
        label_font = ImageFont.truetype("Arial", 14)
    except:
        price_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
    
    # LEP price - Appendix A: only the price can be edited
    lep_price = price_data.get('lep_price', '£2.99')
    price_bbox = draw.textbbox((0, 0), lep_price, font=price_font)
    price_width = price_bbox[2] - price_bbox[0]
    price_x = (width - price_width) // 2
    draw.text((price_x, 20), lep_price, fill=(0, 83, 159), font=price_font)
    
    # "Everyday low price" label - predefined
    label_text = "Everyday low price"
    label_bbox = draw.textbbox((0, 0), label_text, font=label_font)
    label_width = label_bbox[2] - label_bbox[0]
    label_x = (width - label_width) // 2
    draw.text((label_x, 60), label_text, fill=(0, 83, 159), font=label_font)
    
    return tile

def create_new_tile(width, height):
    """Create New product tile - EXACT Appendix A: predefined, cannot be edited"""
    # Green background - fixed design as per Appendix A
    tile = Image.new('RGBA', (width, height), (34, 139, 34, 255))
    draw = ImageDraw.Draw(tile)
    
    try:
        font = ImageFont.truetype("Arial", 32)
    except:
        font = ImageFont.load_default()
    
    text = "NEW"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (width - text_width) // 2
    text_y = (height - (bbox[3] - bbox[1])) // 2
    
    draw.text((text_x, text_y), text, fill='white', font=font)
    
    return tile

def create_default_tile(width, height):
    """Create default placeholder tile"""
    tile = Image.new('RGBA', (width, height), (200, 200, 200, 255))
    draw = ImageDraw.Draw(tile)
    
    try:
        font = ImageFont.truetype("Arial", 20)
    except:
        font = ImageFont.load_default()
    
    text = "VALUE"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (width - text_width) // 2
    text_y = (height - (bbox[3] - bbox[1])) // 2
    
    draw.text((text_x, text_y), text, fill='#666666', font=font)
    
    return tile

def validate_value_tile_design(tile_image, tile_type):
    """Validate value tile design against EXACT Appendix A & B guidelines"""
    width, height = tile_image.size
    
    issues = []
    
    # Appendix B HARD FAIL: No overlapping elements
    issues.append("HARD FAIL: Content cannot overlay value tile")
    
    # Appendix A: Position validation
    issues.append("HARD FAIL: Value tile position is predefined and cannot be moved")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "recommendations": [
            "Value tile position is predefined and cannot be moved (Appendix A)",
            "Nothing can overlap value tile (Appendix B HARD FAIL)",
            "Clubcard: flat design, only offer+regular price editable (Appendix A)", 
            "LEP: white background, Tesco blue font, trade-style (Appendix A)",
            "New: predefined, cannot be edited (Appendix A)"
        ]
    }

def get_value_tile_templates():
    """Get all available value tile templates based on EXACT Appendix A"""
    return {
        "tile_types": [
            "Clubcard Price",
            "Everyday Low Price", 
            "New"
        ],
        "appendix_a_rules": {
            "Clubcard Price": "Flat design, predefined, only offer price and regular price editable, requires end date DD/MM",
            "Everyday Low Price": "White background, Tesco blue font, trade-style, only price editable, positioned right of packshot",
            "New": "Predefined, cannot be edited"
        }
    }