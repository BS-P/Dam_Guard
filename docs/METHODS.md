# BREACHSCOPE — Methods Documentation

## 1. Breach / Outflow Hydrograph Models

### 1.1 Froehlich (2008) Parametric Breach Model

**Reference**: Froehlich, D.C. (2008). "Embankment Dam Breach Parameters and Their Uncertainties." *Journal of Hydraulic Engineering*, 134(12), 1708–1721.

**Breach Width (Average)**:
$$B_{avg} = 0.27 \cdot k_o \cdot V_w^{0.32} \cdot h_b^{0.04}$$

Where:
- $k_o$ = 1.3 for overtopping, 1.0 for piping
- $V_w$ = reservoir volume at breach time (m³)
- $h_b$ = breach height (m)

**Breach Formation Time**:
$$t_f = 63.2 \sqrt{\frac{V_w}{g \cdot h_b^2}}$$

Where $g$ = 9.81 m/s².

**Peak Outflow (Froehlich 1995)**:
$$Q_p = 0.607 \cdot V_w^{0.295} \cdot h_w^{1.24}$$

Where $h_w$ = depth of water above breach invert at failure.

### 1.2 MacDonald & Langridge-Monopolis (1984)

**Reference**: MacDonald, T.C. & Langridge-Monopolis, J. (1984). "Breaching Characteristics of Dam Failures." *J. Hydraulic Eng.*, 110(5).

**Breach Formation Factor**:
$$V_{er} = 0.0261 \cdot (V_w \cdot h_w)^{0.769}$$

### 1.3 Von Thun & Gillette (1990)

**Reference**: Von Thun, J.L. & Gillette, D.R. (1990). "Guidance on Breach Parameters." Internal Document, USBR.

**Breach Width**:
$$B_{avg} = 2.5 \cdot h_w + C_b$$

Where $C_b$ is a function of reservoir volume:
| Volume (m³) | $C_b$ (m) |
|---|---|
| < 1.23×10⁶ | 6.1 |
| 1.23–6.17×10⁶ | 18.3 |
| 6.17–12.3×10⁶ | 42.7 |
| > 12.3×10⁶ | 54.9 |

**Formation Time** (with highly erodible foundation):
$$t_f = 0.015 \cdot h_w$$

### 1.4 Reservoir Routing

The breach outflow hydrograph is computed by coupling the breach opening geometry (trapezoidal, growing linearly in time from initiation to $t_f$) with reservoir continuity:

$$\frac{dS}{dt} = Q_{in}(t) - Q_{out}(t)$$

$$Q_{out}(t) = C_d \cdot B(t) \cdot \sqrt{2g} \cdot h(t)^{1.5}$$

Where $C_d$ ≈ 0.544 (broad-crested weir), $B(t)$ is the time-varying breach width, and $h(t)$ is the head above the breach invert.

Stage-storage relationship $S(h)$ is interpolated from the user-provided or DEM-derived curve. The ODE is solved with an adaptive Runge-Kutta method (scipy.integrate.solve_ivp, RK45).

**Mass conservation check**: $\int Q_{out} \cdot dt = V_w - V_{final}$ (tolerance: 0.1%).

### 1.5 Sudden Failure

For instantaneous failure: the full breach opens at $t=0$, producing a step function in opening geometry. The hydrograph is computed from the same reservoir routing with $B = B_{max}$ for all $t > 0$.

### 1.6 River Blockage / Landslide Dam Release

A natural dam (landslide-dammed lake) is modeled with user-specified:
- Blockage volume and geometry
- Lake volume and stage-storage
- Overtopping erosion rate (from empirical or user-defined)

The release hydrograph follows the same reservoir routing framework with progressive erosion of the blockage.

---

## 2. 2D-VPMM (Variable Parameter Muskingum-Cunge Method)

**Primary References**:
- Perumal, M. & Price, R.K. (2013). "A fully mass conservative variable parameter McCarthy–Muskingum method." *J. Hydrology*, 502, 89–102.
- Kale, R.V. & Perumal, M. (2014). 2D extension derivation.
- Shakya, N.M. (2015). PhD Thesis, IIT Roorkee.
- NIH Roorkee Report (2019): "Flood Inundation Modelling Using 2D-VPMM."

### 2.1 Governing Equations

The 2D shallow water equations in conservative form, simplified to the diffusion-wave approximation:

**Continuity** (per cell):
$$\frac{\partial h}{\partial t} + \frac{\partial q_x}{\partial x} + \frac{\partial q_y}{\partial y} = r(t)$$

**Momentum** (diffusion-wave):
$$S_{fx} = S_{0x} - \frac{\partial h}{\partial x}$$

$$q_x = \frac{1}{n} h^{5/3} S_{fx}^{1/2} \cdot \text{sign}(S_{fx})$$

where $S_{fx}$ is the friction slope in x, $S_{0x}$ is the bed slope, $h$ is flow depth, $n$ is Manning's roughness.

### 2.2 Muskingum Routing Per Cell

For each cell in x and y directions, flow is routed using the variable parameter Muskingum method:

$$Q_{out}^{j+1} = C_1 Q_{in}^{j+1} + C_2 Q_{in}^j + C_3 Q_{out}^j + C_4 \cdot q_{lat}$$

Where the Muskingum coefficients are:

$$C_1 = \frac{\Delta t - 2K\varepsilon}{D}, \quad C_2 = \frac{\Delta t + 2K\varepsilon}{D}, \quad C_3 = \frac{2K(1-\varepsilon) - \Delta t}{D}, \quad C_4 = \frac{2\Delta t}{D}$$

$$D = 2K(1-\varepsilon) + \Delta t$$

**Travel time**:
$$K = \frac{\Delta x}{c_0}$$

where $c_0 = \frac{5}{3} v_0$ is the kinematic wave celerity for wide rectangular flow with Manning's equation, and $v_0$ is the reference velocity.

**Weighting factor**:
$$\varepsilon = \frac{1}{2} - \frac{Q_0}{2 S_0 c_0 B \Delta x}$$

where $Q_0$ is the reference discharge, $S_0$ is bed slope, and $B$ is flow width.

### 2.3 Documented Limitations

- Valid ONLY in diffusion-wave regime
- NOT valid for: hydraulic jumps, supercritical flow ($Fr > 1$), shock fronts, backwater
- Tested on impervious small catchments with wide rectangular flow
- Dam-break use on real DEMs is an EXTENSION — validity mask is generated per-run
- Flat/adverse slopes handled by DEM conditioning ($S_{min} = 10^{-5}$)

---

## 3. 2D Explicit Diffusion-Wave Baseline

Direct explicit finite-difference solution of the 2D diffusion-wave equation on a regular grid. Uses adaptive time stepping based on CFL condition for stability:

$$\Delta t \leq \frac{\Delta x^2}{2 \cdot D_{max}}$$

where $D_{max}$ is the maximum diffusion coefficient. This solver serves as the built-in comparator for the VPMM method.

---

## 4. Hazard Classification

| Class | Depth (m) | Depth×Velocity (m²/s) | Description |
|-------|-----------|----------------------|-------------|
| H1 | < 0.25 | — | Caution zone |
| H2 | 0.25–0.75 | — | Danger to some |
| H3 | 0.75–1.5 | — | Danger to most |
| H4 | 1.5–2.5 | — | Danger to all |
| H5 | > 2.5 | > 7 | Extreme danger |

Thresholds are editable by the user. Classification follows DEFRA/EA (2006) and ANCOLD (2012) guidelines.

---

## 5. Exposure and Loss Analysis

- **Buildings**: OSM building footprints within inundation extent
- **Population**: WorldPop 100m grid, zonal sum within inundation
- **Roads**: OSM road network length within inundation
- **Damage**: Parametric depth-damage curves (JRC 2017 global curves, editable)

All values labeled **ESTIMATED** with method citation.

---

## 6. Validation Metrics

- **NSE** (Nash-Sutcliffe Efficiency): $NSE = 1 - \frac{\sum(Q_{obs} - Q_{sim})^2}{\sum(Q_{obs} - \bar{Q}_{obs})^2}$
- **EVOL** (Volume Error %): $EVOL = \frac{V_{sim} - V_{obs}}{V_{obs}} \times 100$
- **Hit Rate**: $HR = \frac{A_{sim} \cap A_{obs}}{A_{obs}}$
- **False Alarm Ratio**: $FAR = \frac{A_{sim} \setminus A_{obs}}{A_{sim}}$
- **Critical Success Index**: $CSI = \frac{A_{sim} \cap A_{obs}}{A_{sim} \cup A_{obs}}$
- **F1 Score**: $F1 = \frac{2 \cdot HR \cdot (1-FAR)}{HR + (1-FAR)}$
