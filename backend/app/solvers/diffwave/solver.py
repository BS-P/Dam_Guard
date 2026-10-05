import numpy as np
import numba as nb

@nb.njit(parallel=True)
def compute_fluxes(h, E, n, dx, dy, qx, qy, dt_max):
    """
    Compute friction slopes and intercell fluxes based on explicitly formulated Diffusive Wave equations.
    (Eqs 3.15-3.22)
    qx[i, j] represents flux from cell (i, j-1) to cell (i, j)
    qy[i, j] represents flux from cell (i-1, j) to cell (i, j)
    """
    rows, cols = h.shape
    h_min = 1e-6
    S_min = 1e-5
    
    max_diff_coeff = 1e-12

    # Compute qx (flux in x direction, across columns)
    for i in nb.prange(rows):
        for j in range(1, cols):
            # Bed slope (Eq 3.15)
            S0x = (E[i, j-1] - E[i, j]) / dx
            
            # Friction slope (Eq 3.17)
            Sfx = S0x - (h[i, j] - h[i, j-1]) / dx
            
            # Flow depth to use (upwind based on friction slope)
            if Sfx >= 0:
                h_f = h[i, j-1]
            else:
                h_f = h[i, j]
                
            if h_f > h_min:
                n_val = 0.5 * (n[i, j-1] + n[i, j])
                abs_Sfx = max(abs(Sfx), S_min)
                
                # Diffusion coefficient D = (1/n) * h^(5/3) / (2 * sqrt(Sfx))
                # Max diffusion coefficient for CFL limit
                D = (1.0 / n_val) * (h_f**(5/3)) / (2.0 * np.sqrt(abs_Sfx))
                if D > max_diff_coeff:
                    max_diff_coeff = D
                
                # Discharge (Eq 3.19-3.20)
                if Sfx >= 0:
                    qx[i, j] = (1.0 / n_val) * (h_f**(5/3)) * np.sqrt(abs_Sfx)
                else:
                    qx[i, j] = -(1.0 / n_val) * (h_f**(5/3)) * np.sqrt(abs_Sfx)
            else:
                qx[i, j] = 0.0

    # Compute qy (flux in y direction, across rows)
    for i in nb.prange(1, rows):
        for j in range(cols):
            # Bed slope (Eq 3.16)
            S0y = (E[i-1, j] - E[i, j]) / dy
            
            # Friction slope (Eq 3.18)
            Sfy = S0y - (h[i, j] - h[i-1, j]) / dy
            
            if Sfy >= 0:
                h_f = h[i-1, j]
            else:
                h_f = h[i, j]
                
            if h_f > h_min:
                n_val = 0.5 * (n[i-1, j] + n[i, j])
                abs_Sfy = max(abs(Sfy), S_min)
                
                D = (1.0 / n_val) * (h_f**(5/3)) / (2.0 * np.sqrt(abs_Sfy))
                if D > max_diff_coeff:
                    max_diff_coeff = D
                
                # Discharge (Eq 3.21-3.22)
                if Sfy >= 0:
                    qy[i, j] = (1.0 / n_val) * (h_f**(5/3)) * np.sqrt(abs_Sfy)
                else:
                    qy[i, j] = -(1.0 / n_val) * (h_f**(5/3)) * np.sqrt(abs_Sfy)
            else:
                qy[i, j] = 0.0
                
    # Adaptive dt based on stability criteria (dx = dy = W assumed for stability)
    W = min(dx, dy)
    dt_stable = (W * W) / (2.0 * max_diff_coeff) if max_diff_coeff > 0 else dt_max
    
    return min(dt_stable, dt_max)


@nb.njit(parallel=True)
def update_depths(h, qx, qy, rain, source_inflow, dx, dy, dt, h_max, v_max):
    """
    Update depths based on Continuity (Eq 3.14).
    h[i,j]^(t+1) = h[i,j]^t + R_e*dt - [(qx[i,j+1] - qx[i,j])/dx + (qy[i+1,j] - qy[i,j])/dy] * dt
    + point source contributions.
    """
    rows, cols = h.shape
    vol_error = 0.0
    
    for i in nb.prange(rows):
        for j in range(cols):
            # Net flux out in x and y directions
            # qx[i, j+1] is flux from (i, j) to (i, j+1)
            # qx[i, j] is flux from (i, j-1) to (i, j)
            out_x = 0.0
            in_x = 0.0
            if j < cols - 1:
                out_x = qx[i, j+1]
            if j > 0:
                in_x = qx[i, j]
                
            out_y = 0.0
            in_y = 0.0
            if i < rows - 1:
                out_y = qy[i+1, j]
            if i > 0:
                in_y = qy[i, j]
                
            flux_term = ((out_x - in_x) / dx + (out_y - in_y) / dy)
            
            # Rainfall and point sources
            r_val = rain[i, j] if rain is not None else 0.0
            s_val = source_inflow[i, j] / (dx * dy) if source_inflow is not None else 0.0
            
            # Eq 3.14
            dh = (r_val + s_val - flux_term) * dt
            
            new_h = h[i, j] + dh
            
            if new_h < 0:
                # Mass conservation tracking for numerical error
                vol_error += -new_h * dx * dy
                new_h = 0.0
                
            h[i, j] = new_h
            
            # Update max depth
            if new_h > h_max[i, j]:
                h_max[i, j] = new_h
                
            # Estimate cell-centered velocity for max_v tracking
            # Velocity = discharge / depth
            if new_h > 1e-6:
                vx = 0.5 * (in_x + out_x) / new_h
                vy = 0.5 * (in_y + out_y) / new_h
                v_mag = np.sqrt(vx*vx + vy*vy)
                if v_mag > v_max[i, j]:
                    v_max[i, j] = v_mag
                    
    return vol_error
