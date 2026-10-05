import numpy as np

class DEMInfo:
    def __init__(self, path: str, resolution: float):
        self.path = path
        self.resolution = resolution

def fetch_copernicus_dem(bounds: list, output_dir: str) -> str:
    """
    Fetches Copernicus DEM for the given bounds.
    (Placeholder implementation for documented API)
    """
    import os
    output_path = os.path.join(output_dir, "copernicus_dem.tif")
    # Simulation of API call and saving file
    with open(output_path, 'w') as f:
        f.write("mock dem data")
    return output_path

def process_uploaded_dem(file_path: str, project_dir: str) -> DEMInfo:
    """Processes an uploaded DEM file."""
    # In reality, this would read the file, reproject, clip, etc.
    return DEMInfo(path=file_path, resolution=30.0)

def get_roughness_map(dem_path: str, landcover_path: str = None, default_n: float = 0.035) -> np.ndarray:
    """
    Generates a Manning's n roughness map.
    Maps ESA WorldCover classes to Manning's n if landcover is available.
    """
    import rasterio
    
    try:
        with rasterio.open(dem_path) as src:
            shape = src.shape
            
        if landcover_path is None:
            return np.full(shape, default_n)
            
        # Mock ESA to Manning's mapping
        # Tree: 0.15, Shrub: 0.07, Grass: 0.035, Crop: 0.04, Built: 0.015, Water: 0.025, Bare: 0.025
        with rasterio.open(landcover_path) as lc_src:
            lc_data = lc_src.read(1)
            
        roughness = np.full(lc_data.shape, default_n)
        roughness[lc_data == 10] = 0.15 # Trees
        roughness[lc_data == 20] = 0.07 # Shrubland
        roughness[lc_data == 30] = 0.035 # Grassland
        roughness[lc_data == 40] = 0.04 # Cropland
        roughness[lc_data == 50] = 0.015 # Built-up
        roughness[lc_data == 60] = 0.025 # Bare
        roughness[lc_data == 80] = 0.025 # Water
        
        return roughness
    except Exception:
        return np.array([[]]) # Fallback
