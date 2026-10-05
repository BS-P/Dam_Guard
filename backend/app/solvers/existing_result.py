import os
import logging
from pathlib import Path
from typing import Dict, Any, List

try:
    import rasterio
    from rasterio.errors import RasterioIOError
except ImportError:
    rasterio = None

class ExistingResultProvider:
    """
    Loads pre-computed results (GeoTIFFs or NetCDF) from files.
    Labels them as EXTERNAL RESULT for the platform.
    """
    
    def __init__(self, result_dir: str):
        self.result_dir = Path(result_dir)
        self.logger = logging.getLogger(self.__class__.__name__)

    def validate_result(self, file_path: Path) -> Dict[str, Any]:
        """
        Validates CRS, bounds, and layers of a pre-computed raster file.
        """
        if rasterio is None:
            return {"valid": False, "error": "rasterio not installed"}

        if not file_path.exists():
            return {"valid": False, "error": f"File not found: {file_path}"}

        try:
            with rasterio.open(file_path) as src:
                crs = src.crs.to_string() if src.crs else "UNKNOWN"
                bounds = src.bounds
                count = src.count
                
                return {
                    "valid": True,
                    "crs": crs,
                    "bounds": {
                        "left": bounds.left,
                        "bottom": bounds.bottom,
                        "right": bounds.right,
                        "top": bounds.top
                    },
                    "layers": count,
                    "source_type": "EXTERNAL RESULT"
                }
        except RasterioIOError as e:
            return {"valid": False, "error": f"Raster parsing error: {str(e)}"}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def load_results(self) -> List[Dict[str, Any]]:
        """
        Scans the directory for valid raster outputs (depth, velocity)
        """
        results = []
        if not self.result_dir.exists():
            self.logger.error(f"Directory {self.result_dir} does not exist.")
            return results

        for ext in ["*.tif", "*.tiff", "*.nc"]:
            for file_path in self.result_dir.glob(ext):
                meta = self.validate_result(file_path)
                meta["file_name"] = file_path.name
                meta["file_path"] = str(file_path)
                results.append(meta)
                
        return results
