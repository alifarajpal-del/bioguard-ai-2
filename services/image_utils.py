"""Image utility functions for consistent handling across the app."""
from PIL import Image
import numpy as np
import cv2


def ensure_rgb(img: Image.Image) -> Image.Image:
    """
    Convert image to RGB mode if needed.
    Handles RGBA, P (palette), LA, etc.
    
    Args:
        img: PIL Image object
        
    Returns:
        PIL Image in RGB mode
    """
    if img.mode == 'RGB':
        return img
    
    if img.mode == 'RGBA':
        # Create white background and composite
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        return background
    
    if img.mode in ('P', 'LA', 'L', '1'):
        # Convert palette, LA, grayscale, binary to RGB
        return img.convert('RGB')
    
    # Default conversion for other modes
    return img.convert('RGB')


def ensure_rgb_from_array(frame: np.ndarray) -> np.ndarray:
    """
    Convert numpy array frame to RGB if it has alpha channel or other issues.
    
    Args:
        frame: numpy array from camera or image
        
    Returns:
        numpy array in BGR or RGB format suitable for PIL/OpenCV
    """
    if len(frame.shape) != 3:
        return frame
    
    channels = frame.shape[2]
    
    # If 4-channel (BGRA), convert to BGR
    if channels == 4:
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    
    # If 1-channel (grayscale), convert to BGR
    if channels == 1:
        return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    
    # Already 3-channel (BGR or RGB)
    return frame


def image_to_jpeg_bytes(img: Image.Image) -> bytes:
    """
    Convert PIL Image to JPEG bytes safely.
    
    Args:
        img: PIL Image object
        
    Returns:
        JPEG bytes
    """
    # Ensure RGB before save
    img = ensure_rgb(img)
    
    from io import BytesIO
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf.getvalue()


def frame_to_jpeg_bytes(frame: np.ndarray) -> bytes:
    """
    Convert numpy frame to JPEG bytes safely.
    
    Args:
        frame: numpy array (BGR from camera)
        
    Returns:
        JPEG bytes
    """
    # Ensure proper format
    frame = ensure_rgb_from_array(frame)
    
    # Convert to PIL Image (OpenCV uses BGR, PIL expects RGB)
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    return image_to_jpeg_bytes(img)
