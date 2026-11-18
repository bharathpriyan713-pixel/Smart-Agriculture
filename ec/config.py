"""
config.py
Configurable constraints, economic rates, and environment parameters
for smart agriculture optimization.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class FarmConfig:
    # Macro Land & Resource Constraints
    total_arable_land_ha: float = 100.0       # Total farm size in hectares
    max_seasonal_water_m3: float = 480_000.0  # Total water quota available in reservoir
    max_nitrogen_kg: float = 12_000.0         # Environmental ceiling on total N application
    max_total_budget_usd: float = 85_000.0    # Operating budget (seeds, labor, fertilizer, water)

    # Unit Costs
    water_cost_per_m3: float = 0.045          # $ / m3
    nitrogen_cost_per_kg: float = 1.10        # $ / kg
    phosphorus_cost_per_kg: float = 1.35      # $ / kg
    potassium_cost_per_kg: float = 0.95       # $ / kg

    # Regulatory & Agro-Ecological Constraints
    min_legume_fraction: float = 0.15         # At least 15% land in legumes for soil rejuvenation
    max_single_crop_fraction: float = 0.40    # Monoculture avoidance cap (max 40% on any single crop)

    # Multi-Objective Weights (must balance farmer goals)
    weight_profit: float = 0.50               # Weight given to maximizing net revenue
    weight_water_savings: float = 0.20        # Weight given to conserving irrigation water
    weight_soil_health: float = 0.15          # Weight given to soil regeneration / nitrogen fixation
    weight_risk_reduction: float = 0.15       # Weight given to diversification & drought resilience


@dataclass
class IrrigationZoneConfig:
    zone_id: int
    name: str
    crop_name: str
    area_ha: float
    soil_type: str                            # e.g., 'Clay Loam', 'Sandy Loam'
    field_capacity_mm: float                  # Upper moisture threshold (before runoff/leaching)
    permanent_wilting_point_mm: float         # Lower moisture limit (crop death)
    initial_soil_moisture_mm: float           # Current sensor reading
    kc_crop_coefficient: float                # Evapotranspiration coefficient Kc
    max_irrigation_per_day_mm: float = 25.0   # Physical capacity of drip/sprinkler nozzles


@dataclass
class WeatherForecastDay:
    day_index: int
    et0_reference_evapotranspiration_mm: float # Reference ET0 (mm/day)
    forecast_rainfall_mm: float               # Predicted rain (mm)
    temp_max_c: float
    humidity_percent: float
    electricity_peak_multiplier: float        # Cost factor for pumping energy


def get_default_irrigation_zones() -> List[IrrigationZoneConfig]:
    return [
        IrrigationZoneConfig(
            zone_id=1,
            name="Zone 1 - High Value Orchard/Tomatoes",
            crop_name="Tomato",
            area_ha=15.0,
            soil_type="Clay Loam",
            field_capacity_mm=130.0,
            permanent_wilting_point_mm=60.0,
            initial_soil_moisture_mm=95.0,
            kc_crop_coefficient=1.15,
            max_irrigation_per_day_mm=25.0,
        ),
        IrrigationZoneConfig(
            zone_id=2,
            name="Zone 2 - Grain Fields (Maize)",
            crop_name="Corn (Maize)",
            area_ha=35.0,
            soil_type="Silt Loam",
            field_capacity_mm=120.0,
            permanent_wilting_point_mm=50.0,
            initial_soil_moisture_mm=80.0,
            kc_crop_coefficient=1.05,
            max_irrigation_per_day_mm=20.0,
        ),
        IrrigationZoneConfig(
            zone_id=3,
            name="Zone 3 - Legume Fields (Soybean)",
            crop_name="Soybean",
            area_ha=25.0,
            soil_type="Sandy Loam",
            field_capacity_mm=100.0,
            permanent_wilting_point_mm=40.0,
            initial_soil_moisture_mm=70.0,
            kc_crop_coefficient=0.85,
            max_irrigation_per_day_mm=20.0,
        ),
        IrrigationZoneConfig(
            zone_id=4,
            name="Zone 4 - Fiber Fields (Cotton)",
            crop_name="Cotton",
            area_ha=25.0,
            soil_type="Loam",
            field_capacity_mm=115.0,
            permanent_wilting_point_mm=45.0,
            initial_soil_moisture_mm=75.0,
            kc_crop_coefficient=0.90,
            max_irrigation_per_day_mm=18.0,
        ),
    ]


def get_7day_weather_forecast() -> List[WeatherForecastDay]:
    """Simulated 7-day weather forecast based on meteorological patterns."""
    return [
        WeatherForecastDay(day_index=1, et0_reference_evapotranspiration_mm=5.2, forecast_rainfall_mm=0.0, temp_max_c=31.0, humidity_percent=45.0, electricity_peak_multiplier=1.0),
        WeatherForecastDay(day_index=2, et0_reference_evapotranspiration_mm=5.8, forecast_rainfall_mm=0.0, temp_max_c=33.5, humidity_percent=40.0, electricity_peak_multiplier=1.2),
        WeatherForecastDay(day_index=3, et0_reference_evapotranspiration_mm=6.1, forecast_rainfall_mm=0.0, temp_max_c=35.0, humidity_percent=38.0, electricity_peak_multiplier=1.3),
        WeatherForecastDay(day_index=4, et0_reference_evapotranspiration_mm=3.5, forecast_rainfall_mm=12.0, temp_max_c=27.0, humidity_percent=78.0, electricity_peak_multiplier=0.9), # Rain event
        WeatherForecastDay(day_index=5, et0_reference_evapotranspiration_mm=4.0, forecast_rainfall_mm=3.0, temp_max_c=28.5, humidity_percent=70.0, electricity_peak_multiplier=0.9),
        WeatherForecastDay(day_index=6, et0_reference_evapotranspiration_mm=5.0, forecast_rainfall_mm=0.0, temp_max_c=31.0, humidity_percent=50.0, electricity_peak_multiplier=1.1),
        WeatherForecastDay(day_index=7, et0_reference_evapotranspiration_mm=5.5, forecast_rainfall_mm=0.0, temp_max_c=32.0, humidity_percent=46.0, electricity_peak_multiplier=1.1),
    ]
