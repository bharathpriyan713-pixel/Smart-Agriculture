"""
crop_data.py
Defines the agricultural profiles, resource requirements, economic metrics,
and environmental impact factors for different crops.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CropProfile:
    name: str
    crop_type: str            # e.g., 'Cereal', 'Legume', 'Vegetable', 'Cash Crop'
    yield_per_ha: float       # Metric tons per hectare
    market_price_per_ton: float # In USD per metric ton
    water_req_m3_per_ha: float  # Cubic meters of water required per hectare
    nitrogen_req_kg_ha: float   # Nitrogen requirement (kg/ha)
    phosphorus_req_kg_ha: float # Phosphorus requirement (kg/ha)
    potassium_req_kg_ha: float  # Potassium requirement (kg/ha)
    labor_cost_per_ha: float    # Base labor & machinery cost ($/ha)
    seed_cost_per_ha: float     # Seed & planting cost ($/ha)
    market_demand_tons: float   # Maximum local market demand before price drops
    drought_tolerance: float    # Scale 0.0 (very sensitive) to 1.0 (very resilient)
    soil_health_benefit: float  # -1.0 (depletes soil) to +1.0 (enriches soil, e.g. legumes)
    growth_duration_days: int   # Crop cycle in days


CROPS_DATABASE: Dict[str, CropProfile] = {
    "Wheat": CropProfile(
        name="Wheat",
        crop_type="Cereal",
        yield_per_ha=4.2,
        market_price_per_ton=280.0,
        water_req_m3_per_ha=4500.0,
        nitrogen_req_kg_ha=120.0,
        phosphorus_req_kg_ha=50.0,
        potassium_req_kg_ha=40.0,
        labor_cost_per_ha=320.0,
        seed_cost_per_ha=110.0,
        market_demand_tons=350.0,
        drought_tolerance=0.70,
        soil_health_benefit=0.10,
        growth_duration_days=120,
    ),
    "Corn (Maize)": CropProfile(
        name="Corn (Maize)",
        crop_type="Cereal",
        yield_per_ha=8.5,
        market_price_per_ton=230.0,
        water_req_m3_per_ha=6200.0,
        nitrogen_req_kg_ha=180.0,
        phosphorus_req_kg_ha=70.0,
        potassium_req_kg_ha=80.0,
        labor_cost_per_ha=450.0,
        seed_cost_per_ha=160.0,
        market_demand_tons=600.0,
        drought_tolerance=0.55,
        soil_health_benefit=-0.15,
        growth_duration_days=110,
    ),
    "Soybean": CropProfile(
        name="Soybean",
        crop_type="Legume",
        yield_per_ha=3.1,
        market_price_per_ton=490.0,
        water_req_m3_per_ha=4100.0,
        nitrogen_req_kg_ha=30.0,    # Fixes atmospheric nitrogen!
        phosphorus_req_kg_ha=45.0,
        potassium_req_kg_ha=60.0,
        labor_cost_per_ha=340.0,
        seed_cost_per_ha=130.0,
        market_demand_tons=250.0,
        drought_tolerance=0.65,
        soil_health_benefit=0.85,   # Highly beneficial for nitrogen fixation
        growth_duration_days=100,
    ),
    "Tomato": CropProfile(
        name="Tomato",
        crop_type="Vegetable",
        yield_per_ha=28.0,
        market_price_per_ton=450.0,
        water_req_m3_per_ha=7500.0,
        nitrogen_req_kg_ha=160.0,
        phosphorus_req_kg_ha=80.0,
        potassium_req_kg_ha=150.0,
        labor_cost_per_ha=1800.0,
        seed_cost_per_ha=350.0,
        market_demand_tons=280.0,
        drought_tolerance=0.35,
        soil_health_benefit=-0.30,
        growth_duration_days=90,
    ),
    "Cotton": CropProfile(
        name="Cotton",
        crop_type="Cash Crop",
        yield_per_ha=2.4,
        market_price_per_ton=1650.0,
        water_req_m3_per_ha=6800.0,
        nitrogen_req_kg_ha=140.0,
        phosphorus_req_kg_ha=60.0,
        potassium_req_kg_ha=70.0,
        labor_cost_per_ha=600.0,
        seed_cost_per_ha=180.0,
        market_demand_tons=120.0,
        drought_tolerance=0.75,
        soil_health_benefit=-0.25,
        growth_duration_days=150,
    ),
    "Chickpea": CropProfile(
        name="Chickpea",
        crop_type="Legume",
        yield_per_ha=2.0,
        market_price_per_ton=620.0,
        water_req_m3_per_ha=3200.0,
        nitrogen_req_kg_ha=25.0,    # Legume nitrogen fixation
        phosphorus_req_kg_ha=40.0,
        potassium_req_kg_ha=35.0,
        labor_cost_per_ha=290.0,
        seed_cost_per_ha=105.0,
        market_demand_tons=140.0,
        drought_tolerance=0.85,
        soil_health_benefit=0.75,
        growth_duration_days=95,
    ),
}

def get_crop_list() -> List[CropProfile]:
    return list(CROPS_DATABASE.values())
