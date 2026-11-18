"""
generate_visuals.py
Generates an interactive, modern HTML visualization dashboard
displaying optimization results, convergence curves, and farm schedules.
"""

import json
from typing import Dict, Any, List


def generate_html_dashboard(
    crop_results: Dict[str, Any],
    crop_history: List[Dict[str, Any]],
    irrig_results: Dict[str, Any],
    irrig_history: List[Dict[str, Any]],
    output_path: str = "smart_agri_dashboard.html"
):
    """Creates a self-contained dashboard with interactive Chart.js visualizations."""

    # Extract Crop Planning data
    crop_labels = [item["crop"] for item in crop_results["allocations"]]
    crop_hectares = [item["allocated_ha"] for item in crop_results["allocations"]]
    crop_yields = [item["expected_yield_tons"] for item in crop_results["allocations"]]
    crop_waters = [item["water_m3"] for item in crop_results["allocations"]]

    crop_gen_labels = [h["generation"] for h in crop_history]
    crop_gen_best = [round(h["best_fitness"], 2) for h in crop_history]
    crop_gen_mean = [round(h["mean_fitness"], 2) for h in crop_history]

    # Extract Irrigation data
    irrig_gen_labels = [h["generation"] for h in irrig_history]
    irrig_gen_best = [round(h["best_fitness"], 2) for h in irrig_history]

    zone_names = [z["name"] for z in irrig_results["zone_schedules"]]
    days = ["Day 1", "Day 2", "Day 3", "Day 4 (Rain)", "Day 5", "Day 6", "Day 7"]

    crop_obj = crop_results["objectives"]
    irrig_obj = irrig_results["objectives"]

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Agriculture Evolutionary Optimization Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #0b1120;
            --card-bg: #1e293b;
            --accent-green: #10b981;
            --accent-blue: #38bdf8;
            --accent-amber: #f59e0b;
            --accent-purple: #a855f7;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background-color: var(--bg-color); color: var(--text-main); padding: 24px; line-height: 1.5; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; padding-bottom: 18px; border-bottom: 1px solid var(--border-color); }}
        .header h1 {{ font-size: 26px; color: var(--accent-green); font-weight: 700; }}
        .header p {{ color: var(--text-muted); font-size: 14px; margin-top: 4px; }}
        .badge {{ background: rgba(16, 185, 129, 0.2); color: var(--accent-green); padding: 6px 12px; border-radius: 9999px; font-weight: 600; font-size: 12px; border: 1px solid var(--accent-green); }}

        /* KPI Cards */
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; margin-bottom: 28px; }}
        .kpi-card {{ background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; transition: transform 0.2s; }}
        .kpi-card:hover {{ transform: translateY(-3px); }}
        .kpi-title {{ font-size: 13px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.05em; }}
        .kpi-value {{ font-size: 26px; font-weight: 800; margin-top: 8px; color: #fff; }}
        .kpi-subtext {{ font-size: 12px; margin-top: 6px; }}
        .text-green {{ color: var(--accent-green); }}
        .text-blue {{ color: var(--accent-blue); }}
        .text-amber {{ color: var(--accent-amber); }}
        .text-purple {{ color: var(--accent-purple); }}

        /* Content Grid */
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 28px; }}
        @media (max-width: 900px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}

        .card {{ background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 22px; }}
        .card-title {{ font-size: 17px; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; }}

        /* Table */
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border-color); }}
        th {{ background: rgba(255, 255, 255, 0.03); color: var(--text-muted); font-weight: 600; }}
        tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}

        .highlight-rain {{ background: rgba(56, 189, 248, 0.15); color: var(--accent-blue); font-weight: 600; border-radius: 4px; padding: 2px 6px; }}
        .tag-legume {{ background: rgba(16, 185, 129, 0.15); color: var(--accent-green); padding: 2px 8px; border-radius: 4px; font-size: 11px; }}

        .chart-box {{ position: relative; height: 260px; width: 100%; }}
        .section-desc {{ font-size: 13px; color: var(--text-muted); margin-bottom: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Smart Agriculture Optimization System</h1>
            <p>Powered by Real-Coded Genetic Algorithms (BLX-&alpha; Crossover, Gaussian Mutation & Multi-Objective Pareto Fitness)</p>
        </div>
        <div class="badge">EVOLUTIONARY COMPUTATION ACTIVE</div>
    </div>

    <!-- KPI ROW -->
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-title">Optimized Net Profit</div>
            <div class="kpi-value text-green">${crop_obj['net_profit_usd']:,.0f}</div>
            <div class="kpi-subtext text-muted">Revenue: ${crop_obj['total_revenue_usd']:,.0f} | Cost: ${crop_obj['total_cost_usd']:,.0f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Water Conservation</div>
            <div class="kpi-value text-blue">{crop_obj['water_savings_percent']:.1f}%</div>
            <div class="kpi-subtext text-muted">{crop_obj['water_used_m3']:,.0f} m&sup3; of 480,000 m&sup3; used</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Soil Rejuvenation</div>
            <div class="kpi-value text-purple">{crop_obj['legume_fraction_percent']:.1f}%</div>
            <div class="kpi-subtext text-muted">Legume rotation (N-fixation active)</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Drought Resilience</div>
            <div class="kpi-value text-amber">{crop_obj['drought_resilience_percent']:.1f}%</div>
            <div class="kpi-subtext text-muted">Soil health score: {crop_obj['soil_health_index']:+.2f}</div>
        </div>
    </div>

    <!-- MODULE 1: CROP PLANNING -->
    <div class="grid-2">
        <div class="card">
            <div class="card-title">Optimal Crop Land Allocation (Hectares)</div>
            <div class="chart-box">
                <canvas id="cropLandChart"></canvas>
            </div>
        </div>
        <div class="card">
            <div class="card-title">GA Convergence (Crop Planning)</div>
            <div class="chart-box">
                <canvas id="cropConvergenceChart"></canvas>
            </div>
        </div>
    </div>

    <!-- CROP TABLE -->
    <div class="card" style="margin-bottom: 28px;">
        <div class="card-title">Macro Crop & Resource Schedule Breakdown</div>
        <table>
            <thead>
                <tr>
                    <th>Crop</th>
                    <th>Type</th>
                    <th>Allocated Area (ha)</th>
                    <th>Share of Farm</th>
                    <th>Expected Yield (Tons)</th>
                    <th>Water Demand (m&sup3;)</th>
                    <th>Nitrogen (kg)</th>
                </tr>
            </thead>
            <tbody>
                {"".join(f'''
                <tr>
                    <td><strong>{item['crop']}</strong></td>
                    <td><span class="{'tag-legume' if item['crop_type'] == 'Legume' else ''}">{item['crop_type']}</span></td>
                    <td>{item['allocated_ha']:.2f} ha</td>
                    <td>{item['percent_of_farm']:.1f}%</td>
                    <td>{item['expected_yield_tons']:.1f} T</td>
                    <td>{item['water_m3']:,.0f} m&sup3;</td>
                    <td>{item['nitrogen_kg']:,.0f} kg</td>
                </tr>
                ''' for item in crop_results['allocations'])}
            </tbody>
        </table>
    </div>

    <!-- MODULE 2: PRECISION IRRIGATION -->
    <div class="grid-2">
        <div class="card">
            <div class="card-title">
                7-Day Precision Irrigation Schedule (mm/day)
                <span class="highlight-rain">Day 4: Rain 12mm</span>
            </div>
            <p class="section-desc">Notice how the GA intelligently schedules zero or minimal water on Day 4 to exploit natural precipitation, avoiding runoff and power tariffs.</p>
            <table>
                <thead>
                    <tr>
                        <th>Zone & Crop</th>
                        <th>D1</th>
                        <th>D2</th>
                        <th>D3</th>
                        <th>D4 (Rain)</th>
                        <th>D5</th>
                        <th>D6</th>
                        <th>D7</th>
                        <th>Total mm</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(f'''
                    <tr>
                        <td><strong>{z['crop']}</strong> ({z['area_ha']} ha)</td>
                        {"".join(f"<td>{mm:.1f}</td>" for mm in z['daily_irrigation_mm'])}
                        <td><strong>{z['total_irrigation_mm']:.1f}</strong></td>
                    </tr>
                    ''' for z in irrig_results['zone_schedules'])}
                </tbody>
            </table>
        </div>

        <div class="card">
            <div class="card-title">GA Convergence (Smart Irrigation Loss Minimization)</div>
            <div class="chart-box">
                <canvas id="irrigConvergenceChart"></canvas>
            </div>
        </div>
    </div>

    <!-- SCRIPTS -->
    <script>
        // 1. Crop Distribution Chart
        new Chart(document.getElementById('cropLandChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(crop_labels)},
                datasets: [{{
                    data: {json.dumps(crop_hectares)},
                    backgroundColor: ['#10b981', '#f59e0b', '#38bdf8', '#ec4899', '#8b5cf6', '#64748b'],
                    borderWidth: 2,
                    borderColor: '#1e293b'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'right', labels: {{ color: '#f8fafc', font: {{ size: 12 }} }} }}
                }}
            }}
        }});

        // 2. Crop Planning GA Convergence
        new Chart(document.getElementById('cropConvergenceChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(crop_gen_labels)},
                datasets: [
                    {{
                        label: 'Best Fitness',
                        data: {json.dumps(crop_gen_best)},
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.25,
                        pointRadius: 1
                    }},
                    {{
                        label: 'Population Mean Fitness',
                        data: {json.dumps(crop_gen_mean)},
                        borderColor: '#64748b',
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{ title: {{ display: true, text: 'Generation', color: '#94a3b8' }}, ticks: {{ color: '#94a3b8' }} }},
                    y: {{ title: {{ display: true, text: 'Fitness Score', color: '#94a3b8' }}, ticks: {{ color: '#94a3b8' }} }}
                }},
                plugins: {{ legend: {{ labels: {{ color: '#f8fafc' }} }} }}
            }}
        }});

        // 3. Irrigation GA Convergence
        new Chart(document.getElementById('irrigConvergenceChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(irrig_gen_labels)},
                datasets: [{{
                    label: 'Best Schedule Loss (Fitness)',
                    data: {json.dumps(irrig_gen_best)},
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.15)',
                    fill: true,
                    tension: 0.25,
                    pointRadius: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{ title: {{ display: true, text: 'Generation', color: '#94a3b8' }}, ticks: {{ color: '#94a3b8' }} }},
                    y: {{ title: {{ display: true, text: 'Loss / Negative Cost', color: '#94a3b8' }}, ticks: {{ color: '#94a3b8' }} }}
                }},
                plugins: {{ legend: {{ labels: {{ color: '#f8fafc' }} }} }}
            }}
        }});
    </script>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n[+] Interactive HTML Dashboard generated successfully at: {output_path}")
