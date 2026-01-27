# CosmosAPI — Real-Time Astronomical Calculation Service

CosmosAPI is a high-performance RESTful service that uses NASA JPL data to compute positions of celestial bodies, distances between them, and visibility from any location on Earth. This project demonstrates scientific data processing, mathematical modeling, and modern backend architecture.

## Features

- Precise position computation using NASA JPL DE421 ephemeris (binary SPK kernel).
- Real-time distances between two celestial bodies in kilometers and Astronomical Units (AU).
- Light-time correction: accounts for the time light takes to travel, producing observationally consistent positions.
- Observer-based positions: compute altitude and azimuth from any Earth latitude and longitude.
- Docker-ready for easy deployment.
- Auto-generated interactive API documentation via FastAPI (Swagger UI).
- Production-ready error handling and validation.

## Technology Stack

- Language: Python 3.9+
- Web framework: FastAPI (asynchronous, high-performance)
- Astronomy engine: Skyfield (NumPy-based)
- Ephemeris: NASA JPL DE421 (`de421.bsp`, ~17 MB)
- ASGI server: Uvicorn
- Data validation: Pydantic
- Containerization: Docker

## Important Notes Before Use

- First-run download: The NASA ephemeris file (`de421.bsp`, ~17 MB) is automatically downloaded on first execution. This may take 10–30 seconds depending on your internet connection.
- JSON format: All API responses use standard JSON format without trailing spaces in keys or string values (for example, `"source"` not `"source "`).
- Time support: The current version calculates positions for the current moment only. Historical and future timestamp support is planned for future releases.

## Installation & Quick Start

Follow these steps to run CosmosAPI locally.

1. Clone the repository
```bash
git clone https://github.com/username/cosmos-api.git
cd cosmos-api
```

2. (Recommended) Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application (development)
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open the interactive API documentation at: http://127.0.0.1:8000/docs

## Docker Deployment

Start the service with Docker (no local Python setup required).

Build the image:
```bash
docker build -t cosmos-api .
```

Run the container:
```bash
docker run -p 8000:8000 cosmos-api
```

Important: The NASA ephemeris file is downloaded during the first container execution (not during image build). To persist the ephemeris file between container restarts, use a volume mount:
```bash
docker run -p 8000:8000 -v $(pwd)/data:/app/data cosmos-api
```

## API Endpoints

Base URL (local): http://127.0.0.1:8000

All endpoints are documented and testable in the Swagger UI at `/docs`.

1) Root endpoint

- Description: Basic API information and available endpoints.
- Endpoint: GET /

Example response:
```json
{
  "message": "Welcome to CosmosAPI!",
  "endpoints": ["/bodies", "/distance", "/position", "/health"],
  "docs": "/docs"
}
```

2) Health check

- Description: Health status endpoint for monitoring systems.
- Endpoint: GET /health

Example response:
```json
{
  "status": "healthy",
  "service": "CosmosAPI",
  "version": "1.0.0",
  "ephemeris_loaded": true
}
```

3) List supported bodies

- Description: Returns all celestial bodies available for calculations.
- Endpoint: GET /bodies

Example response:
```json
{
  "available_bodies": [
    "sun", "earth", "moon", "mercury", "venus", "mars",
    "jupiter", "saturn", "uranus", "neptune", "pluto"
  ]
}
```

4) Distance between two bodies

- Description: Compute the instantaneous distance between two bodies with light-time correction.
- Endpoint: GET /distance
- Query parameters:
  - `obj1` (string, required) — source body (e.g., `earth`)
  - `obj2` (string, required) — target body (e.g., `mars`)

Example request:
```
/distance?obj1=earth&obj2=mars
```

Example response:
```json
{
  "source": "earth",
  "target": "mars",
  "km": 285430120.54,
  "au": 1.907982,
  "light_time_seconds": 952.1,
  "timestamp": "2026-01-26T14:30:00Z"
}
```

5) Observer-based sky position (altitude / azimuth)

- Description: Compute a planet's sky position from a given Earth location.
- Endpoint: GET /position
- Query parameters:
  - `planet` (string, required) — planet name (e.g., `jupiter`)
  - `lat` (float, required) — observer latitude in decimal degrees (-90 to 90)
  - `lon` (float, required) — observer longitude in decimal degrees (-180 to 180)

Example request:
```
/position?planet=jupiter&lat=41.0082&lon=28.9784
```

Example response:
```json
{
  "planet": "jupiter",
  "observer_location": {
    "lat": 41.0082,
    "lon": 28.9784
  },
  "altitude_deg": 45.2,
  "azimuth_deg": 180.5,
  "distance_km": 590430000.0,
  "is_visible": true,
  "timestamp": "2026-01-26T14:30:00Z"
}
```

Note: An object is visible above the horizon when `altitude_deg > 0`.

## Scientific Background

- Calculations are based on vector astrometry principles using NASA JPL DE421 ephemeris data.
- Light-time correction is applied to all distance calculations, providing observationally accurate positions that account for the finite speed of light.
- For gas giants (Jupiter, Saturn, Uranus, Neptune), positions are computed using the system barycenter (center of mass) rather than a planetary surface point. This aligns with astronomical standards and improves precision.
- Altitude is measured in degrees above the horizon (0° = horizon, 90° = zenith).
- Azimuth is measured in degrees from true north (0° = North, 90° = East, 180° = South, 270° = West).

## Production Considerations

- CORS: Default configuration allows all origins. For production deployments, restrict CORS origins to trusted domains.
- Rate limiting: Not implemented in the base version. Consider adding rate limiting middleware for public deployments.
- Ephemeris persistence: The ephemeris file (`de421.bsp`) should be persisted between restarts using Docker volumes or persistent storage to avoid repeated downloads.
- Error handling: All endpoints return standardized error responses with descriptive messages for invalid inputs.

## Contributing

Contributions are welcome. Please open a pull request for bug fixes and enhancements. For larger changes, open an issue first to discuss the design.

Guidelines:
- Follow the existing code style and PEP 8 standards.
- Add tests for new features or bug fixes.
- Keep pull requests focused on a single feature or fix.
- Update documentation when adding new functionality.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
