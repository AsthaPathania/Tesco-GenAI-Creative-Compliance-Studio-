from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import numpy as np

def remove_background_ai(image):
    """Enhanced AI-powered background removal simulation"""
    try:
        # Convert to RGBA for transparency
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Create a simple simulation of background removal
        # In production, this would use a proper AI model like rembg
        width, height = image.size
        pixels = image.load()
        
        # Simple background detection (light backgrounds)
        for i in range(width):
            for j in range(height):
                r, g, b, a = pixels[i, j]
                
                # Detect light background (adjust thresholds as needed)
                is_light_background = (r > 200 and g > 200 and b > 200)
                is_white_background = (r > 240 and g > 240 and b > 240)
                
                if is_light_background or is_white_background:
                    # Make background transparent
                    pixels[i, j] = (r, g, b, 0)
        
        return image
        
    except Exception as e:
        print(f"Background removal error: {e}")
        return image

def enhance_image_quality(image):
    """Enhance image quality for professional creatives"""
    # Convert to RGB if necessary
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.3)
    
    # Enhance color saturation
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(1.1)
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.05)
    
    # Apply subtle sharpening filter
    image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
    
    return image

def apply_creative_filters(image, filter_type):
    """Apply creative filters to images"""
    if filter_type == "Warm":
        # Warm filter - enhance reds and yellows
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.2)
        
        # Split and adjust channels
        r, g, b = image.split()
        r = r.point(lambda i: min(255, i * 1.1))
        image = Image.merge('RGB', (r, g, b))
    
    elif filter_type == "Cool":
        # Cool filter - enhance blues
        r, g, b = image.split()
        b = b.point(lambda i: min(255, i * 1.1))
        image = Image.merge('RGB', (r, g, b))
    
    elif filter_type == "Vibrant":
        # Vibrant filter - increase saturation
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.4)
    
    return image

def optimize_for_social_media(image, platform):
    """Optimize image for specific social media platforms"""
    optimizations = {
        'instagram': {
            'size': (1080, 1080), 
            'quality': 95
        },
        'facebook': {
            'size': (1200, 630), 
            'quality': 90
        },
        'instagram_story': {
            'size': (1080, 1920), 
            'quality': 95
        }
    }
    
    if platform in optimizations:
        config = optimizations[platform]
        image = image.resize(config['size'], Image.Resampling.LANCZOS)
    
    return image

def validate_image_dimensions(image, min_width=500, min_height=500):
    """Validate image dimensions with recommendations"""
    width, height = image.size
    
    if width < min_width or height < min_height:
        recommendations = []
        if width < min_width:
            recommendations.append(f"Increase width to at least {min_width} pixels")
        if height < min_height:
            recommendations.append(f"Increase height to at least {min_height} pixels")
        
        return False, f"Image too small. Minimum: {min_width}x{min_height}. Recommendations: {', '.join(recommendations)}"
    
    return True, f"Dimensions OK: {width}x{height}"

def create_placeholder_image(width, height, text="Upload Image"):
    """Create professional placeholder image"""
    img = Image.new('RGB', (width, height), color='#BFE0F5')
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([0, 0, width-1, height-1], outline='#00539F', width=3)
    
    # Draw icon placeholder
    icon_size = min(width, height) // 3
    icon_x = (width - icon_size) // 2
    icon_y = (height - icon_size) // 2 - 20
    
    draw.rectangle([icon_x, icon_y, icon_x + icon_size, icon_y + icon_size], 
                   fill='#00539F', outline='#003366', width=2)
    
    # Add text
    try:
        font_size = min(24, width // 15)
        from PIL import ImageFont
        font = ImageFont.truetype("Arial", font_size)
    except:
        font = ImageFont.load_default()
    
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (width - text_width) // 2
    text_y = icon_y + icon_size + 30
    
    draw.text((text_x, text_y), text, fill='#00539F', font=font)
    
    return img