import numpy as np
from typing import Dict

def hit_rate(sim_extent: np.ndarray, obs_extent: np.ndarray) -> float:
    """
    Hit Rate (HR) or Probability of Detection.
    HR = Hits / (Hits + Misses)
    """
    sim_bool = sim_extent.astype(bool)
    obs_bool = obs_extent.astype(bool)
    
    hits = np.sum(sim_bool & obs_bool)
    misses = np.sum((~sim_bool) & obs_bool)
    
    if (hits + misses) == 0:
        return 0.0
    return float(hits / (hits + misses))

def false_alarm_ratio(sim_extent: np.ndarray, obs_extent: np.ndarray) -> float:
    """
    False Alarm Ratio (FAR).
    FAR = False Alarms / (Hits + False Alarms)
    """
    sim_bool = sim_extent.astype(bool)
    obs_bool = obs_extent.astype(bool)
    
    hits = np.sum(sim_bool & obs_bool)
    false_alarms = np.sum(sim_bool & (~obs_bool))
    
    if (hits + false_alarms) == 0:
        return 0.0
    return float(false_alarms / (hits + false_alarms))

def critical_success_index(sim_extent: np.ndarray, obs_extent: np.ndarray) -> float:
    """
    Critical Success Index (CSI).
    CSI = Hits / (Hits + Misses + False Alarms)
    """
    sim_bool = sim_extent.astype(bool)
    obs_bool = obs_extent.astype(bool)
    
    hits = np.sum(sim_bool & obs_bool)
    misses = np.sum((~sim_bool) & obs_bool)
    false_alarms = np.sum(sim_bool & (~obs_bool))
    
    denom = hits + misses + false_alarms
    if denom == 0:
        return 0.0
    return float(hits / denom)

def f1_score(sim_extent: np.ndarray, obs_extent: np.ndarray) -> float:
    """
    F1 Score (Harmonic mean of precision and recall).
    """
    hr = hit_rate(sim_extent, obs_extent)  # Recall
    far = false_alarm_ratio(sim_extent, obs_extent)
    precision = 1.0 - far
    
    if (precision + hr) == 0:
        return 0.0
    return float(2 * (precision * hr) / (precision + hr))

def fit_index(sim_extent: np.ndarray, obs_extent: np.ndarray) -> float:
    """
    Fit Index (FI). Similar to CSI. (Ratio of intersection over union)
    """
    sim_bool = sim_extent.astype(bool)
    obs_bool = obs_extent.astype(bool)
    
    intersection = np.sum(sim_bool & obs_bool)
    union = np.sum(sim_bool | obs_bool)
    
    if union == 0:
        return 0.0
    return float(intersection / union)

def nse(observed: np.ndarray, simulated: np.ndarray) -> float:
    """
    Nash-Sutcliffe Efficiency (NSE) for timeseries data (e.g. hydrographs).
    """
    obs_mean = np.mean(observed)
    numerator = np.sum((observed - simulated) ** 2)
    denominator = np.sum((observed - obs_mean) ** 2)
    
    if denominator == 0:
        return 0.0
    return float(1.0 - (numerator / denominator))

def volume_error_pct(observed: np.ndarray, simulated: np.ndarray, time_array: np.ndarray) -> float:
    """
    Percentage error in total volume (integration of discharge over time).
    """
    # Calculate integration (dt * Q)
    dt = np.diff(time_array)
    # Using simple forward Euler integration for approximation
    obs_vol = np.sum(observed[:-1] * dt)
    sim_vol = np.sum(simulated[:-1] * dt)
    
    if obs_vol == 0:
        return 0.0
    return float(((sim_vol - obs_vol) / obs_vol) * 100.0)

def peak_error_pct(observed: np.ndarray, simulated: np.ndarray) -> float:
    """
    Percentage error in peak magnitude (e.g., peak discharge or peak stage).
    """
    obs_peak = np.max(observed)
    sim_peak = np.max(simulated)
    
    if obs_peak == 0:
        return 0.0
    return float(((sim_peak - obs_peak) / obs_peak) * 100.0)

def compute_all_metrics(sim_result: np.ndarray, obs_result: np.ndarray) -> Dict[str, float]:
    """
    Compute all spatial categorical metrics. 
    Assumes 2D arrays where > 0 is flooded.
    """
    sim_ext = sim_result > 0
    obs_ext = obs_result > 0
    
    return {
        "Hit Rate": hit_rate(sim_ext, obs_ext),
        "False Alarm Ratio": false_alarm_ratio(sim_ext, obs_ext),
        "Critical Success Index": critical_success_index(sim_ext, obs_ext),
        "F1 Score": f1_score(sim_ext, obs_ext),
        "Fit Index": fit_index(sim_ext, obs_ext)
    }
