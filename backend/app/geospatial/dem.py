"""
DEM processing module.

Handles DEM loading, clipping, reprojection, and basic analysis.
Uses rasterio (BSD-3) for I/O and pyproj (MIT) for coordinate transforms.
"""
import numpy as np
import os
import hashlib
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

try:
    import rasterio
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    from rasterio.mask import mask as rasterio_mask
    from rasterio.transform import from_bounds
    from rasterio.crs import CRS
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

try:
    from pyproj import Transformer, CRS as PyprojCRS
    HAS_PYPROJ = True
except ImportError:
    HAS_PYPROJ = False

try:
    from shapely.geometry import box, mapping
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False


@dataclass
class DEMInfo:
    """DEM metadata and statistics."""
    file_path: str
    crs: str
    resolution_m: Tuple[float, float]
    bounds: Tuple[float, float, float, float]  # (west, south, east, north)
    shape: Tuple[int, int]  # (rows, cols)
    nodata: Optional[float]
    min_elevation: float
    max_elevation: float
    mean_elevation: float
    dtype: str
    content_hash: str
    is_geographic: bool


def compute_file_hash(filepath: str) -> str:
    """Compute SHA-256 hash of file content for caching."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()[:16]


def load_dem_info(filepath: str) -> DEMInfo:
    """
    Load DEM metadata without reading the full array.
    
    Args:
        filepath: Path to GeoTIFF DEM file
        
    Returns:
        DEMInfo with metadata and basic statistics
    """
    if not HAS_RASTERIO:
        raise ImportError("rasterio is required for DEM processing. Install with: pip install rasterio")
    
    with rasterio.open(filepath) as src:
        crs = src.crs
        is_geographic = crs.is_geographic if crs else True
        
        # Compute approximate resolution in meters
        if is_geographic and HAS_PYPROJ:
            # Convert from degrees to approximate meters at center latitude
            center_lat = (src.bounds.bottom + src.bounds.top) / 2
            res_x_deg, res_y_deg = src.res
            # 1 degree latitude ≈ 111,320 meters
            res_y_m = abs(res_y_deg) * 111320.0
            res_x_m = abs(res_x_deg) * 111320.0 * np.cos(np.radians(center_lat))
        else:
            res_x_m, res_y_m = abs(src.res[0]), abs(src.res[1])
        
        # Read data for statistics (windowed for large files)
        data = src.read(1)
        nodata = src.nodata
        
        if nodata is not None:
            valid = data[data != nodata]
        else:
            valid = data[np.isfinite(data)]
        
        content_hash = compute_file_hash(filepath)
        
        return DEMInfo(
            file_path=filepath,
            crs=str(crs) if crs else "UNKNOWN",
            resolution_m=(res_x_m, res_y_m),
            bounds=(src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top),
            shape=(src.height, src.width),
            nodata=nodata,
            min_elevation=float(np.min(valid)) if len(valid) > 0 else 0.0,
            max_elevation=float(np.max(valid)) if len(valid) > 0 else 0.0,
            mean_elevation=float(np.mean(valid)) if len(valid) > 0 else 0.0,
            dtype=str(data.dtype),
            content_hash=content_hash,
            is_geographic=is_geographic
        )


def load_dem_array(
    filepath: str,
    band: int = 1
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Load DEM as numpy array with metadata.
    
    Returns:
        (elevation_array, metadata_dict)
    """
    if not HAS_RASTERIO:
        raise ImportError("rasterio required")
    
    with rasterio.open(filepath) as src:
        data = src.read(band).astype(np.float64)
        nodata = src.nodata
        
        if nodata is not None:
            data[data == nodata] = np.nan
        
        meta = {
            'transform': src.transform,
            'crs': src.crs,
            'bounds': src.bounds,
            'res': src.res,
            'shape': data.shape,
            'nodata': nodata
        }
    
    return data, meta


def clip_dem_to_bounds(
    filepath: str,
    bounds: Tuple[float, float, float, float],
    output_path: str,
    buffer_m: float = 1000.0
) -> str:
    """
    Clip DEM to bounding box with buffer.
    
    Args:
        filepath: Input DEM path
        bounds: (west, south, east, north) in the DEM's CRS
        output_path: Output file path
        buffer_m: Buffer distance in meters
        
    Returns:
        Path to clipped DEM
    """
    if not HAS_RASTERIO or not HAS_SHAPELY:
        raise ImportError("rasterio and shapely required")
    
    west, south, east, north = bounds
    
    # Apply buffer (approximate in geographic coords)
    with rasterio.open(filepath) as src:
        if src.crs and src.crs.is_geographic:
            # Approximate buffer in degrees
            buf_deg = buffer_m / 111320.0
            west -= buf_deg
            south -= buf_deg
            east += buf_deg
            north += buf_deg
        else:
            west -= buffer_m
            south -= buffer_m
            east += buffer_m
            north += buffer_m
    
    clip_geom = [mapping(box(west, south, east, north))]
    
    with rasterio.open(filepath) as src:
        out_image, out_transform = rasterio_mask(src, clip_geom, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
        })
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(out_image)
    
    return output_path


def reproject_dem(
    filepath: str,
    target_crs: str,
    output_path: str,
    target_resolution: Optional[float] = None
) -> str:
    """
    Reproject DEM to target CRS.
    
    Args:
        filepath: Input DEM path
        target_crs: Target CRS string (e.g., 'EPSG:32644')
        output_path: Output file path
        target_resolution: Target resolution in meters (optional)
        
    Returns:
        Path to reprojected DEM
    """
    if not HAS_RASTERIO:
        raise ImportError("rasterio required")
    
    with rasterio.open(filepath) as src:
        if target_resolution:
            transform, width, height = calculate_default_transform(
                src.crs, target_crs, src.width, src.height,
                *src.bounds,
                resolution=target_resolution
            )
        else:
            transform, width, height = calculate_default_transform(
                src.crs, target_crs, src.width, src.height, *src.bounds
            )
        
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': target_crs,
            'transform': transform,
            'width': width,
            'height': height,
            'driver': 'GTiff'
        })
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with rasterio.open(output_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    resampling=Resampling.bilinear
                )
    
    return output_path


def compute_slopes(
    dem: np.ndarray,
    dx: float,
    dy: float,
    s_min: float = 1e-5
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute bed slopes from DEM (matching NIH report Eqs 3.15-3.16).
    
    S0x[i,j] = (E[i,j-1] - E[i,j]) / dx  (slope in x-direction)
    S0y[i,j] = (E[i-1,j] - E[i,j]) / dy  (slope in y-direction)
    
    Args:
        dem: 2D elevation array
        dx, dy: Grid spacing in meters
        s_min: Minimum slope magnitude (for numerical stability)
        
    Returns:
        (slope_x, slope_y) arrays
    """
    nrows, ncols = dem.shape
    slope_x = np.zeros_like(dem)
    slope_y = np.zeros_like(dem)
    
    # X-direction slope: (E[i,j-1] - E[i,j]) / dx
    slope_x[:, 1:] = (dem[:, :-1] - dem[:, 1:]) / dx
    slope_x[:, 0] = slope_x[:, 1]  # Boundary
    
    # Y-direction slope: (E[i-1,j] - E[i,j]) / dy
    slope_y[1:, :] = (dem[:-1, :] - dem[1:, :]) / dy
    slope_y[0, :] = slope_y[1, :]  # Boundary
    
    return slope_x, slope_y


def create_cog(
    input_path: str,
    output_path: str,
    overview_levels: Optional[list] = None
) -> str:
    """
    Convert a GeoTIFF to Cloud-Optimized GeoTIFF (COG).
    
    Args:
        input_path: Input GeoTIFF path
        output_path: Output COG path
        overview_levels: Overview levels (default: [2, 4, 8, 16])
    """
    if not HAS_RASTERIO:
        raise ImportError("rasterio required")
    
    if overview_levels is None:
        overview_levels = [2, 4, 8, 16]
    
    with rasterio.open(input_path) as src:
        profile = src.profile.copy()
        profile.update(
            driver='GTiff',
            tiled=True,
            blockxsize=256,
            blockysize=256,
            compress='deflate',
            predictor=2
        )
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with rasterio.open(output_path, 'w', **profile) as dst:
            for i in range(1, src.count + 1):
                dst.write(src.read(i), i)
            
            # Build overviews
            dst.build_overviews(overview_levels, Resampling.nearest)
            dst.update_tags(ns='rio_overview', resampling='nearest')
    
    return output_path
