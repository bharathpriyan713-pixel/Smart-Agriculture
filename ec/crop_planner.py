"""
crop_planner.py
Implements Smart Agriculture Problem #1:
Optimal Multi-Crop Land Allocation & Resource Balancing using Genetic Algorithm.
"""

from typing import List, Tuple, Dict, Any
import numpy as np

from crop_data import CropProfile, get_crop_list
from config import FarmConfig
from genetic_algorithm import GeneticAlgorithm, Individual


class CropPlanningOptimizer:
    """
    Optimizes farm acreage allocation across candidate crops to simultaneously:
      1. Maximize Net Economic Profit ($)
      2. Minimize Irrigation Water Footprint (m3)
      3. Maximize Soil Regeneration (Nitrogen-fixing legumes)
      4. Minimize Drought & Market Volatility Risk
    Subject to land, water quota, nitrogen threshold, budget, and ecological crop rotation bounds.
    """
    def __init__(self, farm_config: FarmConfig = FarmConfig(), crops: List[CropProfile] = None):
        self.config = farm_config
        self.crops = crops if crops is not None else get_crop_list()
        self.n_crops = len(self.crops)

        # Baseline scales for normalization in multi-objective fitness
        self.ref_max_profit = 150_000.0  # Estimated upper bound on profit ($)
        self.ref_max_water = self.config.max_seasonal_water_m3
        self.ref_max_budget = self.config.max_total_budget_usd

    def get_chromosome_bounds(self) -> List[Tuple[float, float]]:
        """Each gene represents hectares assigned to crop i."""
        max_single = self.config.total_arable_land_ha * self.config.max_single_crop_fraction
        return [(0.0, max_single) for _ in range(self.n_crops)]

    def evaluate_chromosome(self, chromosome: List[float]) -> Tuple[float, Dict[str, float], Dict[str, float]]:
        """
        Fitness evaluation mapping chromosome -> fitness score, objective metrics, and penalties.
        """
        allocations = np.array(chromosome)
        total_allocated_land = float(np.sum(allocations))

        # 1. Agricultural & Economic Calculations
        total_revenue = 0.0
        total_labor_seeds_cost = 0.0
        total_water_m3 = 0.0
        total_n_kg = 0.0
        total_p_kg = 0.0
        total_k_kg = 0.0
        soil_health_acc = 0.0
        drought_risk_acc = 0.0
        legume_land = 0.0

        for i, crop in enumerate(self.crops):
            area = allocations[i]
            if area <= 0.001:
                continue

            # Production & market capping
            produced_tons = area * crop.yield_per_ha
            sold_tons = min(produced_tons, crop.market_demand_tons)
            # Excess yield sold at 50% discount due to local glut
            excess_tons = max(0.0, produced_tons - sold_tons)
            crop_rev = (sold_tons * crop.market_price_per_ton) + (excess_tons * crop.market_price_per_ton * 0.50)
            total_revenue += crop_rev

            # Operational input costs
            crop_base_cost = area * (crop.labor_cost_per_ha + crop.seed_cost_per_ha)
            total_labor_seeds_cost += crop_base_cost

            # Resource demands
            crop_water = area * crop.water_req_m3_per_ha
            total_water_m3 += crop_water

            crop_n = area * crop.nitrogen_req_kg_ha
            crop_p = area * crop.phosphorus_req_kg_ha
            crop_k = area * crop.potassium_req_kg_ha
            total_n_kg += crop_n
            total_p_kg += crop_p
            total_k_kg += crop_k

            # Ecological & Risk Metrics
            soil_health_acc += area * crop.soil_health_benefit
            drought_risk_acc += area * (1.0 - crop.drought_tolerance)

            if crop.crop_type.lower() == "legume":
                legume_land += area

        # Resource input expenditure
        water_cost = total_water_m3 * self.config.water_cost_per_m3
        fertilizer_cost = (
            total_n_kg * self.config.nitrogen_cost_per_kg +
            total_p_kg * self.config.phosphorus_cost_per_kg +
            total_k_kg * self.config.potassium_cost_per_kg
        )
        total_operational_cost = total_labor_seeds_cost + water_cost + fertilizer_cost
        net_profit = total_revenue - total_operational_cost

        # Normalized Ecological / Risk indices
        eff_land = max(1.0, total_allocated_land)
        soil_health_score = soil_health_acc / eff_land  # -1.0 to +1.0
        drought_vulnerability = drought_risk_acc / eff_land  # 0.0 to 1.0
        legume_fraction = legume_land / eff_land

        # Diversity index (Shannon entropy across planted crops)
        crop_shares = [a / eff_land for a in allocations if a > 0.01]
        diversity_entropy = -sum(s * np.log(s) for s in crop_shares) if crop_shares else 0.0

        # 2. Constraint Violations
        violations = {}
        penalty = 0.0

        # Constraint A: Total Land Availability
        if total_allocated_land > self.config.total_arable_land_ha:
            diff = total_allocated_land - self.config.total_arable_land_ha
            violations["land_exceeded_ha"] = diff
            penalty += 1500.0 * (diff ** 1.5)

        # Constraint B: Water Allocation Quota
        if total_water_m3 > self.config.max_seasonal_water_m3:
            diff = total_water_m3 - self.config.max_seasonal_water_m3
            violations["water_exceeded_m3"] = diff
            penalty += 5.0 * diff

        # Constraint C: Environmental Nitrogen Cap
        if total_n_kg > self.config.max_nitrogen_kg:
            diff = total_n_kg - self.config.max_nitrogen_kg
            violations["nitrogen_exceeded_kg"] = diff
            penalty += 25.0 * diff

        # Constraint D: Budget Limit
        if total_operational_cost > self.config.max_total_budget_usd:
            diff = total_operational_cost - self.config.max_total_budget_usd
            violations["budget_exceeded_usd"] = diff
            penalty += 8.0 * diff

        # Constraint E: Legume Rotation Minimum (for sustainable nitrogen regeneration)
        if legume_fraction < self.config.min_legume_fraction:
            diff = self.config.min_legume_fraction - legume_fraction
            violations["legume_deficit_frac"] = diff
            penalty += 20_000.0 * (diff ** 2)

        # 3. Scaled Multi-Objective Utility Function
        norm_profit = net_profit / self.ref_max_profit
        norm_water_savings = (self.ref_max_water - total_water_m3) / self.ref_max_water
        norm_soil = (soil_health_score + 1.0) / 2.0  # normalize [-1, 1] -> [0, 1]
        norm_resilience = (1.0 - drought_vulnerability) * 0.7 + min(1.0, diversity_entropy / 1.7) * 0.3

        raw_fitness = (
            self.config.weight_profit * norm_profit +
            self.config.weight_water_savings * norm_water_savings +
            self.config.weight_soil_health * norm_soil +
            self.config.weight_risk_reduction * norm_resilience
        ) * 100.0

        final_fitness = raw_fitness - penalty

        objectives = {
            "net_profit_usd": net_profit,
            "total_revenue_usd": total_revenue,
            "total_cost_usd": total_operational_cost,
            "water_used_m3": total_water_m3,
            "water_savings_percent": max(0.0, 100.0 * (1.0 - total_water_m3 / self.config.max_seasonal_water_m3)),
            "nitrogen_applied_kg": total_n_kg,
            "total_land_allocated_ha": total_allocated_land,
            "legume_fraction_percent": legume_fraction * 100.0,
            "soil_health_index": soil_health_score,
            "drought_resilience_percent": (1.0 - drought_vulnerability) * 100.0,
        }

        return final_fitness, objectives, violations

    def run_optimization(
        self,
        population_size: int = 120,
        generations: int = 160,
        crossover_rate: float = 0.88,
        mutation_rate: float = 0.18,
        verbose: bool = True,
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Executes the Genetic Algorithm for crop planning."""
        ga = GeneticAlgorithm(
            chromosome_length=self.n_crops,
            bounds=self.get_chromosome_bounds(),
            fitness_function=self.evaluate_chromosome,
            population_size=population_size,
            generations=generations,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            elitism_count=3,
        )

        if verbose:
            print("\n=======================================================")
            print("  OPTIMIZING SMART AGRICULTURE CROP ALLOCATION (GA)    ")
            print("=======================================================")
            print(f"Farm Land: {self.config.total_arable_land_ha} ha | Water Quota: {self.config.max_seasonal_water_m3:,.0f} m3")
            print(f"Candidate Crops: {[c.name for c in self.crops]}")
            print("Running evolutionary search...\n")

        best_ind, history = ga.evolve(verbose=verbose)

        # Build clean allocation summary
        allocations_summary = []
        for i, crop in enumerate(self.crops):
            allocated_ha = round(best_ind.chromosome[i], 2)
            pct_land = (allocated_ha / self.config.total_arable_land_ha) * 100.0
            expected_tons = round(allocated_ha * crop.yield_per_ha, 1)
            allocations_summary.append({
                "crop": crop.name,
                "crop_type": crop.crop_type,
                "allocated_ha": allocated_ha,
                "percent_of_farm": round(pct_land, 1),
                "expected_yield_tons": expected_tons,
                "water_m3": round(allocated_ha * crop.water_req_m3_per_ha, 0),
                "nitrogen_kg": round(allocated_ha * crop.nitrogen_req_kg_ha, 0),
            })

        results = {
            "best_fitness": best_ind.fitness,
            "is_valid": best_ind.is_valid,
            "violations": best_ind.constraints_violated,
            "objectives": best_ind.raw_objectives,
            "allocations": allocations_summary,
            "best_chromosome": [round(x, 2) for x in best_ind.chromosome],
        }

        return results, history
