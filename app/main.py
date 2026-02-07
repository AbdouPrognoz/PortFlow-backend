from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.v1.endpoints import auth, admin, common
from .api.v1.endpoints import operator, carrier, driver


app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes
app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["Authentication"])
app.include_router(admin.router, prefix=settings.API_V1_STR + "/admin", tags=["Admin"])
app.include_router(common.router, prefix=settings.API_V1_STR + "/common", tags=["Common"])
app.include_router(operator.router, prefix=settings.API_V1_STR + "/operator", tags=["Operator"])
app.include_router(carrier.router, prefix=settings.API_V1_STR + "/carrier", tags=["Carrier"])
app.include_router(driver.router, prefix=settings.API_V1_STR + "/driver", tags=["Driver"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to Port Terminal API",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}