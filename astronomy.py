"""
Astronomical calculation engine using Skyfield and NASA JPL ephemeris data
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from skyfield.api import load, wgs84
from pathlib import Path

# Configure logging
logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

# ==================== Ephemeris Loading ====================

logger.info("Loading NASA JPL ephemeris data...")
planets = load('de421.bsp')
ts = load.timescale()

# ==================== Body Mapping ====================

BODY_MAP = {
    "sun": "sun",
    "earth": "earth",
    "moon": "moon",
    "mercury": "mercury",
    "venus": "venus",
    "mars": "mars",
    "jupiter": "jupiter barycenter",
    "saturn": "saturn barycenter",
    "uranus": "uranus barycenter",
    "neptune": "neptune barycenter",
    "pluto": "pluto barycenter"
}

AVAILABLE_BODIES = list(BODY_MAP.keys())

def get_body(name: str):
    """
    Get Skyfield body object by name
    
    Args:
        name: Body name (e.g., 'earth', 'mars')
    
    Returns:
        Skyfield body object
    
    Raises:
        ValueError: If body name is not recognized
    """
    key = BODY_MAP.get(name.lower())
    if not key:
        raise ValueError(
            f"Invalid celestial body: '{name}'. "
            f"Available bodies: {', '.join(AVAILABLE_BODIES)}"
        )
    return planets[key]

# ==================== Time Parsing ====================

def parse_timestamp(at: Optional[str] = None):
    """
    Parse ISO 8601 timestamp or return current time
    
    Args:
        at: Optional ISO 8601 timestamp string
    
    Returns:
        Skyfield Time object
    
    Raises:
        ValueError: If timestamp format is invalid
    """
    if at is None:
        return ts.now()
    
    try:
        # Handle 'Z' suffix
        if at.endswith('Z'):
            at = at[:-1] + '+00:00'
        
        # Parse ISO format
        dt = datetime.fromisoformat(at)
        
        # Convert to UTC if timezone-aware
        if dt.tzinfo:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        
        return ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    except Exception as e:
        raise ValueError(
            f"Invalid timestamp format: '{at}'. "
            f"Expected ISO 8601 format (e.g., '2025-01-15T12:00:00Z' or '2025-01-15T12:00:00+00:00'). "
            f"Error: {str(e)}"
        )

# ==================== Calculation Functions ====================

def calculate_distance(
    body1_name: str,
    body2_name: str,
    at: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate distance between two celestial bodies with light-time correction
    
    Args:
        body1_name: Source body name
        body2_name: Target body name
        at: Optional ISO 8601 timestamp (defaults to current time)
    
    Returns:
        Dictionary with distance data
    
    Raises:
        ValueError: If body names are invalid or timestamp is malformed
    """
    # Get body objects
    obj1 = get_body(body1_name)
    obj2 = get_body(body2_name)
    
    # Get time
    t = parse_timestamp(at)
    
    # Calculate distance with light-time correction
    geometry = obj1.at(t).observe(obj2)
    distance = geometry.distance()
    
    return {
        "source": body1_name,
        "target": body2_name,
        "km": round(float(distance.km), 2),
        "au": round(float(distance.au), 6),
        "light_time_seconds": round(float(distance.light_seconds()), 2),
        "timestamp": t.utc_iso()
    }

def calculate_position_from_earth(
    planet_name: str,
    lat: float,
    lon: float,
    at: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate observer-based sky position (altitude/azimuth) of a planet
    
    Args:
        planet_name: Planet name
        lat: Observer latitude in decimal degrees (-90 to 90)
        lon: Observer longitude in decimal degrees (-180 to 180)
        at: Optional ISO 8601 timestamp (defaults to current time)
    
    Returns:
        Dictionary with position data
    
    Raises:
        ValueError: If inputs are invalid
    """
    # Validate coordinates
    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitude must be between -90 and 90 degrees, got {lat}")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Longitude must be between -180 and 180 degrees, got {lon}")
    
    # Get body objects
    target = get_body(planet_name)
    earth = planets['earth']
    
    # Get time
    t = parse_timestamp(at)
    
    # Create observer location
    observer = earth + wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon)
    
    # Calculate apparent position
    astrometric = observer.at(t).observe(target)
    alt, az, distance = astrometric.apparent().altaz()
    
    return {
        "planet": planet_name,
        "observer_location": {"lat": lat, "lon": lon},
        "altitude_deg": round(float(alt.degrees), 2),
        "azimuth_deg": round(float(az.degrees), 2),
        "distance_km": round(float(distance.km), 2),
        "is_visible": alt.degrees > 0,
        "timestamp": t.utc_iso()
    }