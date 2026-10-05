import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Base paths
    BASE_DIR: Path = Path("d:/SIH 2026/DamGuard")
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./breachscope.db"
    
    # Directories
    PROJECTS_DIR: Path = BASE_DIR / "projects"
    RUNS_DIR: Path = BASE_DIR / "runs"
    OUTPUTS_DIR: Path = BASE_DIR / "outputs"
    DATA_DIR: Path = BASE_DIR / "data"
    DEM_CACHE_DIR: Path = BASE_DIR / "dem_cache"
    
    # Solver Paths
    DELFT3D_PATH: Optional[str] = None
    DUALSPHYSICS_PATH: Optional[str] = None
    
    # Credentials
    GEE_CREDENTIALS_FILE: Optional[str] = None
    
    # Configs
    TILE_SERVER_PORT: int = 8081
    MAX_WORKERS: int = 4
    SMIN: float = 1e-5
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Ensure directories exist
for dir_path in [settings.PROJECTS_DIR, settings.RUNS_DIR, settings.OUTPUTS_DIR, settings.DATA_DIR, settings.DEM_CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
