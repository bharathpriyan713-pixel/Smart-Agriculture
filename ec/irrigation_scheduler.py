"""
irrigation_scheduler.py
Implements Smart Agriculture Problem #2:
IoT-Driven Smart Precision Irrigation Scheduling using Genetic Algorithm
based on FAO-56 Soil Moisture Dynamics and Evapotranspiration (ETc).
"""

from typing import List, Tuple, Dict, Any
import numpy as np

from config import (
    IrrigationZoneConfig,
    WeatherForecastDay,
    get_default_irrigation_zones,
    get_7day_weather_forecast,
)
from genetic_algorithm import GeneticAlgorithm, Individual


class SmartIrrigationOptimizer:
    """
    Optimizes multi-zone, 7-day irrigation schedules to:
      1. Prevent Crop Water Stress (keep soil moisture above Management Allowed Depletion - MAD)
      2. Eliminate Waterlogging & Runoff (keep soil moisture below Field Capacity - FC)
      3. Minimize Total Water Volume Used
      4. Exploit Rainfall Events & Weather Forecasts (ET0)
      5. Minimize Energy / Pumping Electricity Costs (avoiding grid peak tariff hours)
    """
    def __init__(
        self,
        zones: List[IrrigationZoneConfig] = None,
        forecast: List[WeatherForecastDay] = None,
    ):
        self.zones = zones if zones is not None else get_default_irrigation_zones()
        self.forecast = forecast if forecast is not None else get_7day_weather_forecast()
        self.num_zones = len(self.zones)
        self.num_days = len(self.forecast)
        self.chromosome_len = self.num_zones * self.num_days

    def get_chromosome_bounds(self) -> List[Tuple[float, float]]:
        """Gene bounds: [0, max_irrigation_per_day_mm] for each (zone, day) pair."""
        bounds = []
        for zone in self.zones:
            for _ in range(self.num_days):
                bounds.append((0.0, zone.max_irrigation_per_day_mm))
        return bounds

    def simulate_zone_dynamics(
        self,
        zone: IrrigationZoneConfig,
        irrigation_amounts: List[float],
    ) -> Tuple[List[float], float, float, float]:
        """
        Simulates 7-day soil water balance (FAO-56 standard):
          Soil_Moisture[t] = Soil_Moisture[t-1] + Irrigation[t] + Rain[t] - ETc[t] - DeepPercolation[t]
        """
        moisture_series = []
        current_moisture = zone.initial_soil_moisture_mm
        total_stress_penalty = 0.0
        total_drainage_loss = 0.0
        total_irrigation_applied = sum(irrigation_amounts)

        # Optimal moisture buffer (Management Allowed Depletion: 45% depletion of available water)
        total_available_water = zone.field_capacity_mm - zone.permanent_wilting_point_mm
        readily_available_water = 0.50 * total_available_water
        target_stress_threshold = zone.field_capacity_mm - readily_available_water

        for day_idx in range(self.num_days):
            day_fc = self.forecast[day_idx]
            irrig = irrigation_amounts[day_idx]
            rain = day_fc.forecast_rainfall_mm

            # Crop evapotranspiration: ETc = Kc * ET0
            etc = zone.kc_crop_coefficient * day_fc.et0_reference_evapotranspiration_mm

            # Water addition & consumption
            potential_moisture = current_moisture + irrig + rain - etc

            # Check deep percolation / runoff if exceeding Field Capacity
            if potential_moisture > zone.field_capacity_mm:
                drainage = potential_moisture - zone.field_capacity_mm
                current_moisture = zone.field_capacity_mm
                total_drainage_loss += drainage
            else:
                drainage = 0.0
                current_moisture = potential_moisture

            # Check for water stress
            if current_moisture < target_stress_threshold:
                stress_deficit = target_stress_threshold - current_moisture
                # Severe quadratic penalty if approaching wilting point
                total_stress_penalty += (stress_deficit ** 1.8) * 4.0

            # Absolute lower bound check (Permanent wilting point)
            if current_moisture < zone.permanent_wilting_point_mm:
                total_stress_penalty += 500.0 + (zone.permanent_wilting_point_mm - current_moisture) * 50.0
                current_moisture = max(10.0, current_moisture)

            moisture_series.append(current_moisture)

        return moisture_series, total_stress_penalty, total_drainage_loss, total_irrigation_applied

    def evaluate_chromosome(self, chromosome: List[float]) -> Tuple[float, Dict[str, float], Dict[str, float]]:
        """
        Fitness function for irrigation schedule.
        Fitness = -(Water Cost + Energy Tariff Cost + Stress Penalties + Drainage Waste)
        """
        total_cost = 0.0
        total_water_volume_m3 = 0.0
        total_stress_penalty = 0.0
        total_leaching_loss_mm = 0.0
        total_pumping_cost_usd = 0.0

        base_electricity_kwh_per_m3 = 0.35  # Pump energy to pressurize drip lines
        cost_per_kwh = 0.16                 # $ / kWh base grid cost

        gene_idx = 0
        zone_results = []

        for zone in self.zones:
            zone_schedule = chromosome[gene_idx : gene_idx + self.num_days]
            gene_idx += self.num_days

            (
                moisture_series,
                stress_pen,
                drainage_loss,
                irrig_applied,
            ) = self.simulate_zone_dynamics(zone, zone_schedule)

            total_stress_penalty += stress_pen
            total_leaching_loss_mm += drainage_loss

            # Water volume: 1 mm depth on 1 hectare = 10 m3
            zone_water_m3 = irrig_applied * 10.0 * zone.area_ha
            total_water_volume_m3 += zone_water_m3

            # Calculate pumping power cost adjusted by daily peak electricity tariff
            for day_idx, daily_irrig_mm in enumerate(zone_schedule):
                daily_volume_m3 = daily_irrig_mm * 10.0 * zone.area_ha
                day_tariff_factor = self.forecast[day_idx].electricity_peak_multiplier
                pump_cost = daily_volume_m3 * base_electricity_kwh_per_m3 * cost_per_kwh * day_tariff_factor
                total_pumping_cost_usd += pump_cost

        # Water resource expense ($0.045 / m3)
        water_raw_cost = total_water_volume_m3 * 0.045
        total_water_energy_cost = water_raw_cost + total_pumping_cost_usd

        # Penalty components
        violations = {}
        if total_stress_penalty > 1.0:
            violations["crop_water_stress"] = total_stress_penalty
        if total_leaching_loss_mm > 5.0:
            violations["deep_percolation_waste"] = total_leaching_loss_mm

        # Total combined cost to minimize (converted to maximization fitness)
        # We penalize crop stress most severely (crop loss is catastrophic), followed by energy & waste
        total_loss = (
            total_stress_penalty * 3.5 +
            total_leaching_loss_mm * 12.0 +
            total_water_energy_cost * 0.8
        )

        fitness = -total_loss

        objectives = {
            "total_water_used_m3": total_water_volume_m3,
            "total_pumping_cost_usd": total_pumping_cost_usd,
            "water_resource_cost_usd": water_raw_cost,
            "crop_stress_penalty": total_stress_penalty,
            "water_leaching_waste_mm": total_leaching_loss_mm,
            "overall_irrigation_cost_usd": total_water_energy_cost,
        }

        return fitness, objectives, violations

    def run_optimization(
        self,
        population_size: int = 100,
        generations: int = 140,
        crossover_rate: float = 0.85,
        mutation_rate: float = 0.15,
        verbose: bool = True,
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Runs GA optimization for 7-day precision irrigation."""
        ga = GeneticAlgorithm(
            chromosome_length=self.chromosome_len,
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
            print("  OPTIMIZING IOT SMART PRECISION IRRIGATION (GA)       ")
            print("=======================================================")
            print(f"Irrigation Zones: {self.num_zones} | Forecast Horizon: {self.num_days} days")
            print(f"Total Decision Variables: {self.chromosome_len} genes")
            print("Running evolutionary search...\n")

        best_ind, history = ga.evolve(verbose=verbose)

        # Unpack best schedule per zone
        zone_schedules = []
        gene_idx = 0
        for zone in self.zones:
            daily_schedule = [round(best_ind.chromosome[gene_idx + d], 2) for d in range(self.num_days)]
            gene_idx += self.num_days
            moisture_series, stress_pen, drainage_loss, irrig_applied = self.simulate_zone_dynamics(zone, daily_schedule)

            zone_schedules.append({
                "zone_id": zone.zone_id,
                "name": zone.name,
                "crop": zone.crop_name,
                "area_ha": zone.area_ha,
                "daily_irrigation_mm": daily_schedule,
                "total_irrigation_mm": round(irrig_applied, 2),
                "total_water_volume_m3": round(irrig_applied * 10.0 * zone.area_ha, 1),
                "moisture_series_mm": [round(m, 1) for m in moisture_series],
                "field_capacity_mm": zone.field_capacity_mm,
                "wilting_point_mm": zone.permanent_wilting_point_mm,
                "stress_penalty": round(stress_pen, 2),
                "drainage_waste_mm": round(drainage_loss, 2),
            })

        results = {
            "best_fitness": best_ind.fitness,
            "objectives": best_ind.raw_objectives,
            "violations": best_ind.constraints_violated,
            "zone_schedules": zone_schedules,
            "best_chromosome": [round(x, 2) for x in best_ind.chromosome],
        }

        return results, history
