# Smart Agriculture Optimization Using Genetic Algorithms (GA)

An evolutionary computation system engineered for precision agriculture and sustainable farm management. This project applies **Real-Coded Genetic Algorithms (RCGA)** to solve two core optimization problems in smart agriculture:

1. **Macro-Level: Optimal Crop Allocation & Land-Resource Balancing**
   - Multi-objective maximization of net farm profit while minimizing water footprint, chemical nitrogen runoff, and climate/drought vulnerability under regulatory and crop-rotation constraints.
2. **Micro-Level: IoT-Driven Precision Irrigation Scheduling**
   - Dynamic 7-day soil water balance optimization based on the FAO-56 Penman-Monteith Evapotranspiration model, weather precipitation forecasts, and electricity grid peak tariffs.

---

## 🌾 Why Genetic Algorithms in Smart Agriculture?

Traditional linear programming and static heuristic methods fail in modern smart agriculture because farming systems exhibit:
- **Non-linear crop growth and water response curves** (diminishing returns, threshold water-stress penalties).
- **High-dimensional combinatorial search spaces** (crop combinations, multi-zone multi-day irrigation depth).
- **Conflicting multi-objective trade-offs** (maximizing revenue vs. conserving aquifer water vs. soil restoration).
- **Complex dynamic constraints** (soil field capacity, deep percolation leaching, seasonal budget ceilings, crop rotation minimums).

Genetic Algorithms (GAs) mimic Darwinian natural selection (reproduction, crossover, mutation, and survival of the fittest) to explore multi-modal fitness landscapes and find Pareto-optimal operational decisions without requiring gradient information.

---

## 📐 Mathematical Formulation

### 1. Macro-Level: Crop Planning & Resource Allocation

Given $N$ candidate crops and total arable land $L_{\text{total}}$:

- **Decision Vector (Chromosome):**
  $$X = [x_1, x_2, \dots, x_N], \quad x_i \ge 0 \text{ (hectares allocated to crop } i \text{)}$$

- **Objective Functions:**
  - **Net Profit:**
    $$\text{Profit}(X) = \sum_{i=1}^N \min(x_i \cdot Y_i, D_i) \cdot P_i - \left[ \sum_{i=1}^N x_i (C_{\text{labor},i} + C_{\text{seed},i}) + W(X) \cdot c_w + F(X) \cdot c_f \right]$$
  - **Water Footprint Conservation:**
    $$W(X) = \sum_{i=1}^N x_i \cdot W_{\text{req}, i}$$
  - **Soil Nitrogen Rejuvenation & Rotation:**
    $$\text{Legume Fraction}(X) = \frac{\sum_{i \in \text{Legumes}} x_i}{\sum_{i=1}^N x_i} \ge \theta_{\text{min}} \quad (15\%)$$
  - **Drought Resilience & Diversification:**
    $$\text{Resilience}(X) = \sum_{i=1}^N \left(\frac{x_i}{L_{\text{total}}}\right) \cdot \text{DT}_i + \lambda \cdot H(X)$$
    where $H(X)$ is the Shannon diversity entropy across cultivated crops.

- **Fitness Formulation:**
  $$\text{Maximize } \mathcal{F}(X) = w_1 \tilde{P}(X) + w_2 \tilde{W}_{\text{saved}}(X) + w_3 \tilde{S}_{\text{health}}(X) + w_4 \tilde{R}_{\text{resilience}}(X) - \sum \text{Penalty}_k$$

---

### 2. Micro-Level: Precision Irrigation Scheduling (FAO-56 Soil Dynamics)

Given $Z$ irrigation zones and $T$ forecast days:

- **Decision Vector (Chromosome):**
  $$I = [i_{z, t}] \in \mathbb{R}^{Z \times T}, \quad 0 \le i_{z,t} \le I_{\max} \text{ (irrigation depth in mm)}$$

- **Soil Moisture Balance Dynamics (Root Zone):**
  $$\theta_{z, t+1} = \theta_{z, t} + i_{z, t} + R_t - ET_{c, z, t} - DP_{z, t}$$
  where:
  - $\theta_{z,t}$: Available soil water content (mm).
  - $R_t$: Effective rainfall on day $t$.
  - $ET_{c, z, t} = K_{c, z} \cdot ET_{0, t}$: Crop evapotranspiration.
  - $DP_{z, t} = \max(0, \theta_{z,t} + i_{z,t} + R_t - ET_{c,z,t} - FC_z)$: Deep percolation loss (leaching and runoff waste when exceeding Field Capacity $FC$).

- **Crop Stress & Energy Loss Minimization:**
  $$\text{Minimize } \mathcal{L}(I) = \sum_{z=1}^Z \sum_{t=1}^T \left( \alpha \cdot \text{StressPenalty}(\theta_{z,t}) + \beta \cdot DP_{z,t} + \gamma \cdot i_{z,t} \cdot \text{Area}_z \cdot \text{Tariff}(t) \right)$$

---

## 🧬 Genetic Algorithm Architecture

| Operator | Mechanism | Purpose |
|---|---|---|
| **Encoding** | Real-Coded Chromosome ($\mathbb{R}^n$) | Direct representation of physical variables (hectares, mm depth) without binary quantization error. |
| **Selection** | Tournament Selection ($k=3$) | Balances selection pressure and maintains population diversity. |
| **Crossover** | Blend Crossover ($\text{BLX-}\alpha, \alpha=0.3$) | Explores continuous solution spaces smoothly between promising parent genes. |
| **Mutation** | Gaussian Mutation ($\sigma=0.10 \cdot \text{span}$) | Local perturbation with bounds clamping to escape local minima. |
| **Elitism** | Strict Preservation ($N_{\text{elite}}=2-3$) | Guarantees monotonic non-decreasing best fitness across generations. |
| **Constraint Handling**| Exterior Quadratic Penalty Functions | Guides search from infeasible regions toward high-value feasible boundaries. |

---

## 📁 Repository Structure

```
ec/
├── config.py                 # Farm geometry, budget constraints, weather forecasts & zone definitions
├── crop_data.py              # Crop database (yield, market price, water, NPK, drought tolerance)
├── genetic_algorithm.py      # Core modular GA engine (tournament selection, BLX-alpha, Gaussian mutation)
├── crop_planner.py           # Macro-optimization module: Multi-Crop Land Allocation
├── irrigation_scheduler.py   # Micro-optimization module: 7-Day Precision Irrigation
├── generate_visuals.py       # Standalone interactive HTML dashboard generator (Chart.js)
├── main.py                   # Master entry point executing both models and logging convergence
├── smart_agri_dashboard.html # Generated interactive visualization report
└── README.md                 # Complete documentation & theoretical formulations
```

---

## 🚀 How to Run

### 1. Execute Optimization
Run the unified pipeline:
```powershell
python main.py
```

### 2. View Interactive Dashboard
Double-click or open `smart_agri_dashboard.html` in any web browser to view:
- **KPI Summary Cards**: Net Profit ($), Water Conserved (%), Legume Rotation (%), Drought Resilience (%).
- **Crop Land Distribution Chart**: Interactive breakdown of farm acreage per crop.
- **GA Convergence Trajectories**: Generational fitness evolution curves.
- **Weather-Adaptive Irrigation Heatmap**: 7-day irrigation schedule displaying natural rain adaptation (e.g., automated shutoff during Day 4 rain).
