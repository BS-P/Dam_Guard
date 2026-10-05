import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class CoupledSolver:
    """
    Coupled solver logic handling the transition from SPH near-field models
    to shallow water far-field models (Delft3D or VPMM).
    """

    @staticmethod
    def extract_hydrograph(sph_measure_tool_csv: str) -> pd.DataFrame:
        """
        Extract discharge through control section from SPH MeasureTool output.
        """
        try:
            # MeasureTool typically outputs time, Flux, etc.
            df = pd.read_csv(sph_measure_tool_csv, sep=';', skipinitialspace=True)
            # Standardize columns: time [s], discharge [m3/s]
            if 'Time' in df.columns and 'Flux' in df.columns:
                df = df[['Time', 'Flux']].rename(columns={'Time': 'time', 'Flux': 'discharge'})
            return df
        except Exception as e:
            logger.error(f"Failed to extract SPH hydrograph: {str(e)}")
            raise

    @staticmethod
    def create_upstream_boundary(hydrograph: pd.DataFrame, output_bnd_file: str, model_type: str = "delft3d"):
        """
        Use SPH hydrograph as an upstream boundary for Delft3D or VPMM.
        """
        if model_type == "delft3d":
            # Delft3D expects a .bc or .tim file format depending on version
            with open(output_bnd_file, 'w') as f:
                for idx, row in hydrograph.iterrows():
                    f.write(f"{row['time']:.2f} {row['discharge']:.4f}\n")
            logger.info(f"Delft3D boundary file created at {output_bnd_file}")
            
        elif model_type == "vpmm":
            # VPMM typical input array format
            hydrograph.to_csv(output_bnd_file, index=False)
            logger.info(f"VPMM boundary file created at {output_bnd_file}")
        else:
            raise ValueError(f"Unknown model_type {model_type}")

    @staticmethod
    def validate_mass_conservation(sph_volume: float, far_field_inflow_volume: float, tolerance: float = 0.05) -> bool:
        """
        Validate mass conservation across the coupling interface.
        Difference should be less than the given tolerance (5% default).
        """
        if sph_volume <= 0:
            return False
            
        diff = abs(sph_volume - far_field_inflow_volume)
        error_ratio = diff / sph_volume
        
        is_valid = error_ratio <= tolerance
        if not is_valid:
            logger.warning(
                f"Mass conservation warning! SPH Vol: {sph_volume:.2f}, "
                f"Far-field Inflow Vol: {far_field_inflow_volume:.2f}. "
                f"Error: {error_ratio*100:.2f}% (Threshold: {tolerance*100:.2f}%)"
            )
        else:
            logger.info(f"Mass conservation validated. Error: {error_ratio*100:.2f}%")
            
        return is_valid
