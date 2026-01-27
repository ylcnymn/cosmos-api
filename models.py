"""
Pydantic models for request/response validation (Pydantic v2 compatible)
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime

# ==================== Request Models ====================

class DistanceRequest(BaseModel):
    """Request model for distance calculation"""
    obj1: str = Field(..., description="Source celestial body name", example="earth")
    obj2: str = Field(..., description="Target celestial body name", example="mars")
    
    @field_validator('obj1', 'obj2')
    @classmethod
    def validate_body_name(cls, v):
        from astronomy import BODY_MAP
        if v.lower() not in BODY_MAP:
            raise ValueError(f"Invalid body name. Must be one of: {list(BODY_MAP.keys())}")
        return v.lower()

class PositionRequest(BaseModel):
    """Request model for position calculation"""
    planet: str = Field(..., description="Planet name", example="jupiter")
    lat: float = Field(..., description="Observer latitude in decimal degrees", ge=-90, le=90, example=41.0082)
    lon: float = Field(..., description="Observer longitude in decimal degrees", ge=-180, le=180, example=28.9784)
    
    @field_validator('planet')
    @classmethod
    def validate_planet_name(cls, v):
        from astronomy import BODY_MAP
        if v.lower() not in BODY_MAP:
            raise ValueError(f"Invalid planet name. Must be one of: {list(BODY_MAP.keys())}")
        return v.lower()

# ==================== Response Models ====================

class BodyListResponse(BaseModel):
    """Response model for available bodies"""
    available_bodies: list = Field(..., description="List of supported celestial bodies")

class DistanceResponse(BaseModel):
    """Response model for distance calculation"""
    source: str = Field(..., description="Source body name")
    target: str = Field(..., description="Target body name")
    km: float = Field(..., description="Distance in kilometers")
    au: float = Field(..., description="Distance in Astronomical Units")
    light_time_seconds: float = Field(..., description="Light travel time in seconds")
    timestamp: str = Field(..., description="ISO 8601 timestamp of calculation")

class PositionResponse(BaseModel):
    """Response model for position calculation"""
    planet: str = Field(..., description="Planet name")
    observer_location: Dict[str, float] = Field(..., description="Observer coordinates")
    altitude_deg: float = Field(..., description="Altitude above horizon in degrees")
    azimuth_deg: float = Field(..., description="Azimuth angle in degrees (0=N, 90=E)")
    distance_km: float = Field(..., description="Distance to planet in kilometers")
    is_visible: bool = Field(..., description="True if altitude > 0 (above horizon)")
    timestamp: str = Field(..., description="ISO 8601 timestamp of calculation")

class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str = Field(..., description="Error message")