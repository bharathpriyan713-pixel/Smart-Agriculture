"""
main.py
Main entry point for Smart Agriculture Optimization using Genetic Algorithms.
Executes both Macro-Crop Planning and Micro-Irrigation Scheduling.
"""

import sys
import time
from config import FarmConfig
from crop_planner import CropPlanningOptimizer
from irrigation_scheduler import SmartIrrigationOptimizer
from generate_visuals import generate_html_dashboard


def run_full_suite():
    print("=" * 72)
    print("     SMART AGRICULTURE OPTIMIZATION USING GENETIC ALGORITHMS     ")
    print("              Evolutionary Decision Support System               ")
    print("=" * 72)

    start_time = time.time()

    # -------------------------------------------------------------
    # 1. MACRO-LEVEL: CROP LAND ALLOCATION & RESOURCE BALANCING
    # -------------------------------------------------------------
    farm_cfg = FarmConfig()
    crop_opt = CropPlanningOptimizer(farm_config=farm_cfg)

    crop_results, crop_history = crop_opt.run_optimization(
        population_size=120,
        generations=160,
        crossover_rate=0.88,
        mutation_rate=0.18,
        verbose=True,
    )

    print("\n-------------------------------------------------------------")
    print("  OPTIMAL CROP ALLOCATION RESULTS (MACRO-PLANNING)")
    print("-------------------------------------------------------------")
    allocations = crop_results["allocations"]
    print(f"{'Crop':<16} | {'Type':<10} | {'Area (ha)':<10} | {'Share':<8} | {'Yield (T)':<10} | {'Water (m3)':<11} | {'N (kg)':<8}")
    print("-" * 84)
    for a in allocations:
        print(f"{a['crop']:<16} | {a['crop_type']:<10} | {a['allocated_ha']:<10.2f} | {a['percent_of_farm']:<6.1f}% | {a['expected_yield_tons']:<10.1f} | {a['water_m3']:<11,.0f} | {a['nitrogen_kg']:<8,.0f}")
    print("-" * 84)

    obj = crop_results["objectives"]
    print(f"Total Arable Land Used : {obj['total_land_allocated_ha']:.2f} ha / {farm_cfg.total_arable_land_ha} ha")
    print(f"Projected Net Profit   : ${obj['net_profit_usd']:,.2f} (Rev: ${obj['total_revenue_usd']:,.2f} - Cost: ${obj['total_cost_usd']:,.2f})")
    print(f"Total Water Footprint  : {obj['water_used_m3']:,.0f} m3 ({obj['water_savings_percent']:.1f}% quota conserved)")
    print(f"Legume Rotation Share  : {obj['legume_fraction_percent']:.1f}% (Minimum required: {farm_cfg.min_legume_fraction * 100:.0f}%)")
    print(f"Soil Health Score      : {obj['soil_health_index']:+.3f} (-1 to +1 scale)")
    print(f"Drought Resilience     : {obj['drought_resilience_percent']:.1f}%")

    if crop_results["violations"]:
        print("\n[!] Constraint Warnings:", crop_results["violations"])
    else:
        print("\n[*] All ecological, budgetary, and agronomic constraints STRICTLY SATISFIED.")

    # -------------------------------------------------------------
    # 2. MICRO-LEVEL: IOT SMART PRECISION IRRIGATION SCHEDULING
    # -------------------------------------------------------------
    irrig_opt = SmartIrrigationOptimizer()

    irrig_results, irrig_history = irrig_opt.run_optimization(
        population_size=100,
        generations=140,
        crossover_rate=0.85,
        mutation_rate=0.15,
        verbose=True,
    )

    print("\n-------------------------------------------------------------")
    print("  OPTIMAL 7-DAY PRECISION IRRIGATION SCHEDULE (mm/day)")
    print("-------------------------------------------------------------")
    print("Day 4 Forecast: 12.0 mm Precipitation event (Weather-Adaptive Trigger)")
    print(f"{'Zone & Crop':<30} | {'D1':<5} | {'D2':<5} | {'D3':<5} | {'D4*':<5} | {'D5':<5} | {'D6':<5} | {'D7':<5} | {'Total mm':<8}")
    print("-" * 88)
    for z in irrig_results["zone_schedules"]:
        d_str = " | ".join(f"{mm:5.1f}" for mm in z["daily_irrigation_mm"])
        print(f"{z['crop'] + ' (' + str(z['area_ha']) + ' ha)':<30} | {d_str} | {z['total_irrigation_mm']:8.1f}")
    print("-" * 88)

    i_obj = irrig_results["objectives"]
    print(f"7-Day Total Irrigation Water: {i_obj['total_water_used_m3']:,.1f} m3")
    print(f"Energy/Pumping Power Cost   : ${i_obj['total_pumping_cost_usd']:,.2f}")
    print(f"Crop Moisture Stress Penalty: {i_obj['crop_stress_penalty']:.2f} (Zero or near-zero indicates healthy crop)")
    print(f"Leaching / Runoff Waste     : {i_obj['water_leaching_waste_mm']:.2f} mm")

    # -------------------------------------------------------------
    # 3. GENERATE VISUAL DASHBOARD
    # -------------------------------------------------------------
    generate_html_dashboard(
        crop_results=crop_results,
        crop_history=crop_history,
        irrig_results=irrig_results,
        irrig_history=irrig_history,
        output_path="smart_agri_dashboard.html"
    )

    elapsed = time.time() - start_time
    print(f"\nOptimization completed in {elapsed:.2f} seconds.")
    print("Open 'smart_agri_dashboard.html' in your browser to view the interactive charts and schedules.\n")


if __name__ == "__main__":
    run_full_suite()
