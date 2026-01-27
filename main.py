"""
CosmosAPI - FastAPI application entry point
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from config import settings
from models import (
    BodyListResponse,
    DistanceResponse,
    PositionResponse,
    ErrorResponse
)
from astronomy import (
    calculate_distance,
    calculate_position_from_earth,
    AVAILABLE_BODIES
)

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# ==================== FastAPI Application ====================

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    contact={
        "name": "CosmosAPI Team",
        "url": "https://github.com/kullaniciadi/cosmos-api"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ==================== Middleware ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Exception Handlers ====================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    logger.warning(f"ValueError: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.warning(f"HTTPException: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )

# ==================== API Endpoints ====================

@app.get(
    "/",
    summary="API Information",
    response_description="API metadata and available endpoints"
)
def home():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to CosmosAPI!",
        "description": settings.APP_DESCRIPTION,
        "version": settings.APP_VERSION,
        "endpoints": ["/bodies", "/distance", "/position"],
        "documentation": "/docs",
        "repository": "https://github.com/kullaniciadi/cosmos-api"
    }

@app.get(
    "/bodies",
    response_model=BodyListResponse,
    summary="List Available Celestial Bodies",
    response_description="List of supported celestial bodies"
)
def list_bodies():
    """
    Returns all celestial bodies that can be used in calculations.
    
    **Returns:**
    - List of body names (e.g., sun, earth, mars, jupiter)
    """
    return {"available_bodies": AVAILABLE_BODIES}

@app.get(
    "/distance",
    response_model=DistanceResponse,
    summary="Calculate Distance Between Two Bodies",
    response_description="Distance with light-time correction",
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
def get_distance(
    obj1: str = Query(
        ...,
        description="Source celestial body name",
        example="earth"
    ),
    obj2: str = Query(
        ...,
        description="Target celestial body name",
        example="mars"
    ),
    at: Optional[str] = Query(
        None,
        description="ISO 8601 timestamp (e.g., '2025-01-15T12:00:00Z'). Current time if not specified.",
        example="2025-01-15T12:00:00Z"
    )
):
    """
    Calculate the instantaneous distance between two celestial bodies.
    
    **Features:**
    - Light-time correction (accounts for light travel time)
    - Supports all major planets, Sun, Moon, and Pluto
    - Returns distance in both kilometers and Astronomical Units (AU)
    
    **Query Parameters:**
    - `obj1`: Source body (e.g., 'earth')
    - `obj2`: Target body (e.g., 'mars')
    - `at`: Optional timestamp (ISO 8601 format)
    
    **Returns:**
    - Distance in kilometers and AU
    - Light travel time in seconds
    - Calculation timestamp
    """
    try:
        result = calculate_distance(obj1.lower(), obj2.lower(), at)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Distance calculation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Calculation failed")

@app.get(
    "/position",
    response_model=PositionResponse,
    summary="Calculate Observer-Based Sky Position",
    response_description="Altitude, azimuth, and visibility from Earth location",
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
def get_position(
    planet: str = Query(
        ...,
        description="Planet name",
        example="jupiter"
    ),
    lat: float = Query(
        ...,
        description="Observer latitude in decimal degrees (-90 to 90)",
        ge=-90,
        le=90,
        example=41.0082
    ),
    lon: float = Query(
        ...,
        description="Observer longitude in decimal degrees (-180 to 180)",
        ge=-180,
        le=180,
        example=28.9784
    ),
    at: Optional[str] = Query(
        None,
        description="ISO 8601 timestamp (e.g., '2025-01-15T12:00:00Z'). Current time if not specified.",
        example="2025-01-15T20:00:00Z"
    )
):
    """
    Calculate a planet's position in the sky from a specific Earth location.
    
    **Features:**
    - Altitude (degrees above horizon)
    - Azimuth (compass direction: 0°=North, 90°=East)
    - Distance from observer
    - Visibility check (altitude > 0)
    - Supports custom timestamps
    
    **Query Parameters:**
    - `planet`: Planet name (e.g., 'jupiter')
    - `lat`: Observer latitude (-90 to 90)
    - `lon`: Observer longitude (-180 to 180)
    - `at`: Optional timestamp (ISO 8601 format)
    
    **Returns:**
    - Altitude and azimuth angles
    - Distance in kilometers
    - Visibility status
    - Calculation timestamp
    
    **Note:** An object is visible when `altitude_deg > 0`.
    """
    try:
        result = calculate_position_from_earth(planet.lower(), lat, lon, at)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Position calculation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Calculation failed")

# ==================== Health Check ====================

@app.get(
    "/health",
    summary="Health Check",
    response_description="Service health status"
)
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "ephemeris_loaded": True
    }

# ==================== Startup/Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """Log application startup"""
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting...")
    logger.info(f"Available bodies: {', '.join(AVAILABLE_BODIES)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown"""
    logger.info(f"{settings.APP_NAME} shutting down...")