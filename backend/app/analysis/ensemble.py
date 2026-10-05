import numpy as np
from typing import Dict, Any, List
from scipy.stats import qmc

def run_ensemble(base_scenario: Dict[str, Any], n_samples: int = 50, param_ranges: Dict[str, tuple] = None) -> List[Dict[str, Any]]:
    """
    Generates an ensemble of parameters using Latin Hypercube Sampling (LHS).
    
    Args:
        base_scenario: Dictionary of base model parameters.
        n_samples: Number of ensemble members to generate.
        param_ranges: Dict mapping parameter name to (min, max) tuple.
    """
    if param_ranges is None:
        param_ranges = {
            "breach_width": (10.0, 100.0),      # meters
            "formation_time": (0.5, 4.0),       # hours
            "manning_n": (0.025, 0.050),        # roughness
            "dem_vertical_error": (-1.0, 1.0)   # meters
        }
        
    keys = list(param_ranges.keys())
    bounds = np.array([param_ranges[k] for k in keys])
    
    # Latin Hypercube Sampling
    sampler = qmc.LatinHypercube(d=len(keys))
    sample = sampler.random(n=n_samples)
    
    # Scale samples to bounds
    scaled_samples = qmc.scale(sample, bounds[:, 0], bounds[:, 1])
    
    ensemble_scenarios = []
    for i in range(n_samples):
        scenario = base_scenario.copy()
        for j, key in enumerate(keys):
            scenario[key] = scaled_samples[i, j]
        scenario['ensemble_id'] = i
        ensemble_scenarios.append(scenario)
        
    return ensemble_scenarios

def compute_probability_map(ensemble_depths: np.ndarray, depth_threshold: float = 0.1) -> np.ndarray:
    """
    Computes the probability of inundation map from an ensemble of depth maps.
    
    Args:
        ensemble_depths: 3D array of shape (n_samples, rows, cols)
        depth_threshold: Depth above which a pixel is considered flooded.
        
    Returns:
        2D array of shape (rows, cols) with values between 0.0 and 1.0
    """
    # Create binary maps where depth > threshold
    flooded_masks = ensemble_depths > depth_threshold
    
    # Mean across the sample dimension gives the probability (0 to 1)
    probability_map = np.mean(flooded_masks, axis=0)
    
    return probability_map

def compute_percentile_maps(ensemble_depths: np.ndarray, percentiles: List[int] = None) -> Dict[int, np.ndarray]:
    """
    Computes percentile maps for maximum depths.
    
    Args:
        ensemble_depths: 3D array of shape (n_samples, rows, cols)
        percentiles: List of percentiles to compute (e.g., [10, 50, 90]).
        
    Returns:
        Dict mapping percentile integer to a 2D depth array.
    """
    if percentiles is None:
        percentiles = [10, 50, 90]
        
    results = {}
    for p in percentiles:
        # np.percentile computes the q-th percentile along the specified axis.
        results[p] = np.percentile(ensemble_depths, p, axis=0)
        
    return results
