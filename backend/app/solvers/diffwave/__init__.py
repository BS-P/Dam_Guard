import numpy as np
from typing import Dict, Any, Callable
from ..base import SolverProvider, SolverStatus, RunStatus, RunResult
from .solver import compute_fluxes, update_depths

class DiffWaveProvider(SolverProvider):
    """
    2D Explicit Diffusion-Wave solver based on NIH Roorkee 2019 report.
    Implements Equations 3.14-3.22 for dam break inundation modelling.
    """

    @classmethod
    def check_installed(cls) -> SolverStatus:
        """Pure Python/Numba solver, always available if dependencies met."""
        return SolverStatus(
            available=True,
            version="1.0",
            message="DiffWave pure Python solver (Numba-accelerated) is available."
        )

    def run(self, inputs: Dict[str, Any], progress_callback: Callable[[float, str], None] = None) -> RunResult:
        """
        Run the 2D Diffusive Wave simulation.
        
        Inputs:
        - DEM: 2D numpy array of elevations (m)
        - mannings_n: 2D numpy array or scalar
        - dx: grid spacing x (m)
        - dy: grid spacing y (m)
        - duration: simulation duration (s)
        - output_interval: time between output frames (s)
        - rain: 2D array of rainfall intensity (m/s), optional
        - source_inflow: 2D array of inflow (m3/s), optional
        """
        try:
            # Extract inputs
            dem = inputs['DEM']
            rows, cols = dem.shape
            
            n_input = inputs.get('mannings_n', 0.03)
            if np.isscalar(n_input):
                mannings_n = np.full((rows, cols), n_input, dtype=np.float64)
            else:
                mannings_n = np.asarray(n_input, dtype=np.float64)
                
            dx = float(inputs['dx'])
            dy = float(inputs['dy'])
            duration = float(inputs['duration'])
            output_interval = float(inputs.get('output_interval', min(duration, 60.0)))
            
            rain = inputs.get('rain', np.zeros_like(dem))
            if np.isscalar(rain):
                rain = np.full((rows, cols), rain, dtype=np.float64)
                
            source_inflow = inputs.get('source_inflow', np.zeros_like(dem))
            
            # Initialize state arrays
            h = np.zeros((rows, cols), dtype=np.float64)
            qx = np.zeros((rows, cols), dtype=np.float64)  # Fluxes in x direction
            qy = np.zeros((rows, cols), dtype=np.float64)  # Fluxes in y direction
            
            # Result arrays
            h_max = np.zeros((rows, cols), dtype=np.float64)
            v_max = np.zeros((rows, cols), dtype=np.float64)
            arrival_time = np.full((rows, cols), -1.0, dtype=np.float64)
            duration_exceeded = np.zeros((rows, cols), dtype=np.float64)
            
            depth_threshold = 0.01  # 1 cm threshold for arrival time
            
            outputs = []
            mass_errors = []
            
            t = 0.0
            next_output = 0.0
            dt_max = 1.0  # Max default time step
            
            if progress_callback:
                progress_callback(0.0, "Starting DiffWave simulation")
                
            while t < duration:
                # 1. Compute intercell fluxes and adaptive dt based on CFL and max diffusion
                dt_stable = compute_fluxes(h, dem, mannings_n, dx, dy, qx, qy, dt_max)
                
                # Ensure we hit the output interval exactly, but don't exceed remaining time
                dt = min(dt_stable, next_output - t)
                if t + dt > duration:
                    dt = duration - t
                
                # 2. Update depths using explicit continuity equation
                vol_error = update_depths(h, qx, qy, rain, source_inflow, dx, dy, dt, h_max, v_max)
                
                # 3. Track arrival times and duration
                exceeds = h > depth_threshold
                first_arrival = exceeds & (arrival_time < 0)
                arrival_time[first_arrival] = t
                duration_exceeded[exceeds] += dt
                
                mass_errors.append(vol_error)
                
                t += dt
                
                # 4. Save outputs at intervals
                if t >= next_output or t >= duration:
                    outputs.append(h.copy())
                    next_output += output_interval
                    
                    if progress_callback:
                        progress = min(1.0, t / duration)
                        progress_callback(progress, f"Simulated {t:.1f}/{duration:.1f}s")
                        
            # Finalize results
            results = {
                'depth_series': np.stack(outputs) if outputs else np.array([h]),
                'max_depth': h_max,
                'max_velocity': v_max,
                'arrival_time': arrival_time,
                'duration': duration_exceeded,
                'mass_errors': mass_errors
            }
            
            if progress_callback:
                progress_callback(1.0, "Simulation complete")
                
            return RunResult(
                status=RunStatus.SUCCESS,
                message="Simulation completed successfully",
                outputs=results
            )
            
        except Exception as e:
            return RunResult(
                status=RunStatus.FAILED,
                message=f"DiffWave solver failed: {str(e)}"
            )
