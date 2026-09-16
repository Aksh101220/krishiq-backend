from __future__ import annotations

from math import asin, ceil, cos, radians, sin, sqrt
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator


FRONTEND_PATH = (
    Path(__file__).resolve().parent
    / "attached_assets"
    / "krishiq-app_(1)_1789501820108.html"
)

app = FastAPI(
    title="Krishiq API",
    description="Simple mandi and buyer recommendations for agricultural lots.",
    version="1.0.0",
)

# The frontend can be opened directly as an HTML file during development, so
# allow browser requests from any origin. Tighten this list before production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


TRUCK_CAPACITY_QTL = 100
BASE_TRUCK_COST = 1_800
TRUCK_COST_PER_KM = 42
APMC_FEE_RATE = 0.01
COMMISSION_RATE = 0.02
HAMALI_PER_QTL = 22

GRADE_FACTORS = {"A": 1.04, "B": 1.00, "C": 0.95}
GRADE_NAMES = {"A": "Premium", "B": "Standard", "C": "Fair"}

MANDIS = [
    {
        "id": 1,
        "name": "Nagpur",
        "district": "Nagpur",
        "latitude": 21.1458,
        "longitude": 79.0882,
        "modal": {"Soybean": 4720, "Cotton": 7150},
    },
    {
        "id": 2,
        "name": "Akola",
        "district": "Akola",
        "latitude": 20.7002,
        "longitude": 77.0082,
        "modal": {"Soybean": 4680, "Cotton": 7080},
    },
    {
        "id": 3,
        "name": "Amravati",
        "district": "Amravati",
        "latitude": 20.9374,
        "longitude": 77.7796,
        "modal": {"Soybean": 4760, "Cotton": 7120},
    },
    {
        "id": 4,
        "name": "Wardha",
        "district": "Wardha",
        "latitude": 20.7453,
        "longitude": 78.6022,
        "modal": {"Soybean": 4630, "Cotton": 6990},
    },
    {
        "id": 5,
        "name": "Yavatmal",
        "district": "Yavatmal",
        "latitude": 20.3888,
        "longitude": 78.1204,
        "modal": {"Soybean": 4610, "Cotton": 7040},
    },
    {
        "id": 6,
        "name": "Pune",
        "district": "Pune",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "modal": {"Soybean": 4890, "Cotton": 7340},
    },
    {
        "id": 7,
        "name": "Nashik",
        "district": "Nashik",
        "latitude": 19.9975,
        "longitude": 73.7898,
        "modal": {"Soybean": 4810, "Cotton": 7260},
    },
]

BUYERS = [
    {
        "id": 1,
        "name": "Vidarbha Agro Processing",
        "type": "processor",
        "crops_accepted": ["Soybean", "Cotton"],
        "min_order_qty_qtl": 80,
        "verified_status": "verified",
        "latitude": 21.15,
        "longitude": 79.09,
        "offer": {"Soybean": 4820, "Cotton": 7350},
    },
    {
        "id": 2,
        "name": "Nagpur Oil Mills",
        "type": "processor",
        "crops_accepted": ["Soybean"],
        "min_order_qty_qtl": 60,
        "verified_status": "verified",
        "latitude": 21.19,
        "longitude": 79.12,
        "offer": {"Soybean": 4790},
    },
    {
        "id": 3,
        "name": "Shree Traders",
        "type": "trader",
        "crops_accepted": ["Soybean", "Cotton"],
        "min_order_qty_qtl": 15,
        "verified_status": "curated",
        "latitude": 21.06,
        "longitude": 79.04,
        "offer": {"Soybean": 4700, "Cotton": 7200},
    },
    {
        "id": 4,
        "name": "AgriCorp Institutional",
        "type": "institutional",
        "crops_accepted": ["Soybean", "Cotton"],
        "min_order_qty_qtl": 150,
        "verified_status": "verified",
        "latitude": 18.53,
        "longitude": 73.86,
        "offer": {"Soybean": 5010, "Cotton": 7480},
    },
    {
        "id": 5,
        "name": "Sahyadri Cotton Co.",
        "type": "processor",
        "crops_accepted": ["Cotton"],
        "min_order_qty_qtl": 100,
        "verified_status": "curated",
        "latitude": 20.00,
        "longitude": 73.79,
        "offer": {"Cotton": 7410},
    },
    {
        "id": 6,
        "name": "Local Mandi Aggregator",
        "type": "trader",
        "crops_accepted": ["Soybean", "Cotton"],
        "min_order_qty_qtl": 5,
        "verified_status": "curated",
        "latitude": 21.01,
        "longitude": 79.10,
        "offer": {"Soybean": 4650, "Cotton": 7050},
    },
]


# Demo farmer lots used for pool aggregation.
# These are intentionally small sample records for the prototype.
OPEN_LOTS = [
    # Indore-area demo lots so the pool feature works during local testing.
    {"id": 201, "farmer_name": "Indore Farmer A", "crop": "Soybean", "quantity_qtl": 30, "latitude": 22.72, "longitude": 75.86},
    {"id": 202, "farmer_name": "Indore Farmer B", "crop": "Soybean", "quantity_qtl": 25, "latitude": 22.73, "longitude": 75.87},
    {"id": 203, "farmer_name": "Indore Farmer C", "crop": "Soybean", "quantity_qtl": 20, "latitude": 22.71, "longitude": 75.85},
    {"id": 204, "farmer_name": "Indore Farmer D", "crop": "Cotton", "quantity_qtl": 35, "latitude": 22.70, "longitude": 75.88},

    # Existing Maharashtra demo lots.
    {"id": 101, "farmer_name": "Demo Farmer A", "crop": "Soybean", "quantity_qtl": 30, "latitude": 21.15, "longitude": 79.09},
    {"id": 102, "farmer_name": "Demo Farmer B", "crop": "Soybean", "quantity_qtl": 25, "latitude": 21.16, "longitude": 79.10},
    {"id": 103, "farmer_name": "Demo Farmer C", "crop": "Soybean", "quantity_qtl": 20, "latitude": 21.14, "longitude": 79.08},
    {"id": 104, "farmer_name": "Demo Farmer D", "crop": "Cotton", "quantity_qtl": 35, "latitude": 20.70, "longitude": 77.01},
]

class RecommendationRequest(BaseModel):
    crop: str = Field(..., description="Supported crop, currently Soybean or Cotton")
    quantity_qtl: float = Field(..., gt=0, description="Harvest quantity in quintals")
    quality_grade: Literal["A", "B", "C"] = Field(
        ..., description="A = Premium, B = Standard, C = Fair"
    )
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

    @field_validator("crop", mode="before")
    @classmethod
    def normalize_crop(cls, value: object) -> str:
        return str(value).strip().title()

    @field_validator("quality_grade", mode="before")
    @classmethod
    def normalize_grade(cls, value: object) -> str:
        return str(value).strip().upper()


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(FRONTEND_PATH, media_type="text/html")


def haversine_km(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
) -> float:
    """Return the great-circle distance between two points in kilometres."""
    earth_radius_km = 6371.0
    lat_delta = radians(end_lat - start_lat)
    lon_delta = radians(end_lon - start_lon)
    a = (
        sin(lat_delta / 2) ** 2
        + cos(radians(start_lat))
        * cos(radians(end_lat))
        * sin(lon_delta / 2) ** 2
    )
    return 2 * earth_radius_km * asin(sqrt(a))


def transport_breakdown(distance_km: float, quantity_qtl: float) -> dict[str, float]:
    """Estimate transport using a full truck cost for each required trip."""
    trips = max(1, ceil(quantity_qtl / TRUCK_CAPACITY_QTL))
    cost_per_trip = BASE_TRUCK_COST + TRUCK_COST_PER_KM * distance_km
    total_cost = cost_per_trip * trips
    return {
        "trips": trips,
        "transport_cost": round(total_cost, 2),
        "transport_cost_per_qtl": round(total_cost / quantity_qtl, 2),
    }


def financial_breakdown(
    price_per_qtl: float,
    distance_km: float,
    quantity_qtl: float,
) -> dict[str, float | dict[str, float]]:
    gross_price = price_per_qtl * quantity_qtl
    apmc_fee = gross_price * APMC_FEE_RATE
    commission = gross_price * COMMISSION_RATE
    hamali = HAMALI_PER_QTL * quantity_qtl
    transport = transport_breakdown(distance_km, quantity_qtl)
    total_fees = apmc_fee + commission + hamali
    net_price = gross_price - total_fees - transport["transport_cost"]

    return {
        "gross_price": round(gross_price, 2),
        "fees": {
            "apmc_fee": round(apmc_fee, 2),
            "commission": round(commission, 2),
            "hamali": round(hamali, 2),
            "total_fees": round(total_fees, 2),
        },
        "transport_cost": transport["transport_cost"],
        "transport_cost_per_qtl": transport["transport_cost_per_qtl"],
        "trips": transport["trips"],
        "estimated_net_price": round(net_price, 2),
        "estimated_net_price_per_qtl": round(net_price / quantity_qtl, 2),
    }


def recommendation_for_mandi(
    mandi: dict,
    request: RecommendationRequest,
    max_price: float,
) -> dict:
    distance = haversine_km(
        request.latitude,
        request.longitude,
        mandi["latitude"],
        mandi["longitude"],
    )
    price_per_qtl = mandi["modal"][request.crop] * GRADE_FACTORS[request.quality_grade]
    breakdown = financial_breakdown(price_per_qtl, distance, request.quantity_qtl)
    return {
        "mandi": {
            "id": mandi["id"],
            "name": mandi["name"],
            "district": mandi["district"],
        },
        "distance_km": round(distance, 1),
        "modal_price": round(price_per_qtl, 2),
        "max_price": round(max_price, 2),
        **breakdown,
    }


def recommendation_for_buyer(
    buyer: dict,
    request: RecommendationRequest,
) -> dict:
    distance = haversine_km(
        request.latitude,
        request.longitude,
        buyer["latitude"],
        buyer["longitude"],
    )
    eligible_crop = request.crop in buyer["crops_accepted"]
    meets_minimum = request.quantity_qtl >= buyer["min_order_qty_qtl"]
    eligible = eligible_crop and meets_minimum
    offer_price = buyer["offer"][request.crop] if eligible_crop else None
    breakdown = (
        financial_breakdown(offer_price, distance, request.quantity_qtl)
        if offer_price is not None
        else None
    )
    if not eligible_crop:
        reason = f"Does not accept {request.crop}"
    elif not meets_minimum:
        reason = f"Needs at least {buyer['min_order_qty_qtl']} qtl"
    else:
        reason = "Eligible"

    return {
        "buyer": {
            "id": buyer["id"],
            "name": buyer["name"],
            "type": buyer["type"],
            "verified_status": buyer["verified_status"],
            "minimum_order_qtl": buyer["min_order_qty_qtl"],
        },
        "eligible": eligible,
        "eligibility_reason": reason,
        "distance_km": round(distance, 1),
        "offer_price": round(offer_price, 2) if offer_price is not None else None,
        **(breakdown or {}),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "krishiq-api"}


POOL_RADIUS_KM = 25.0

def pool_candidates(request: RecommendationRequest) -> list[dict]:
    """Find compatible demo farmer lots within the pool radius."""
    candidates = []
    for lot in OPEN_LOTS:
        if lot["crop"] != request.crop:
            continue
        distance = haversine_km(
            request.latitude, request.longitude,
            lot["latitude"], lot["longitude"]
        )
        if distance <= POOL_RADIUS_KM:
            candidates.append({
                **lot,
                "distance_km": round(distance, 1),
            })
    candidates.sort(key=lambda item: item["distance_km"])
    return candidates

def build_pool_suggestion(
    request: RecommendationRequest,
    buyers: list[dict],
    best_mandi: dict,
) -> dict | None:
    """Build a pool payload matching the Krishiq frontend."""
    nearby = pool_candidates(request)
    if not nearby or request.quantity_qtl >= 70:
        return None

    qty = request.quantity_qtl
    group_qty = qty + sum(lot["quantity_qtl"] for lot in nearby)
    all_lots = [{"latitude": request.latitude, "longitude": request.longitude, "quantity_qtl": qty}, *nearby]

    pool_lat = sum(l["latitude"] * l["quantity_qtl"] for l in all_lots) / group_qty
    pool_lon = sum(l["longitude"] * l["quantity_qtl"] for l in all_lots) / group_qty

    solo_distance = haversine_km(request.latitude, request.longitude, best_mandi["latitude"], best_mandi["longitude"])
    pool_distance = haversine_km(pool_lat, pool_lon, best_mandi["latitude"], best_mandi["longitude"])

    grade_price = best_mandi["modal"][request.crop] * GRADE_FACTORS[request.quality_grade]
    solo_breakdown = financial_breakdown(grade_price, solo_distance, qty)
    pooled_breakdown = financial_breakdown(grade_price, pool_distance, group_qty)

    pooled_total = pooled_breakdown["estimated_net_price_per_qtl"] * group_qty
    user_pooled_total = pooled_total * (qty / group_qty)
    solo_net = solo_breakdown["estimated_net_price_per_qtl"]
    pooled_net = user_pooled_total / qty

    unlocked = []
    for item in buyers:
        buyer = item["buyer"]
        if buyer["minimum_order_qtl"] <= group_qty and buyer["minimum_order_qtl"] > qty:
            unlocked.append({
                "id": buyer["id"],
                "name": buyer["name"],
                "type": buyer["type"],
                "crops_accepted": [request.crop],
                "min_order_qty_qtl": buyer["minimum_order_qtl"],
                "verified_status": buyer["verified_status"],
                "offer": item.get("offer_price"),
            })

    return {
        "solo_net_per_qtl": round(solo_net, 2),
        "pooled_net_per_qtl": round(pooled_net, 2),
        "savings_per_qtl": round(pooled_net - solo_net, 2),
        "group_quantity_qtl": round(group_qty, 2),
        "group_size": len(nearby) + 1,
        "pooled_transport_per_qtl": round(pooled_breakdown["transport_cost_per_qtl"], 2),
        "solo_transport_per_qtl": round(solo_breakdown["transport_cost_per_qtl"], 2),
        "mandi_distance_km": round(solo_distance, 1),
        "group": nearby,
        "unlocked_buyers": unlocked,
        "candidates": nearby,
    }


@app.post("/recommendations")
def recommendations(request: RecommendationRequest) -> dict:
    if request.crop not in {crop for mandi in MANDIS for crop in mandi["modal"]}:
        supported = sorted({crop for mandi in MANDIS for crop in mandi["modal"]})
        return {
            "recommendations": [],
            "buyer_recommendations": [],
            "error": f"Unsupported crop '{request.crop}'. Supported crops: {', '.join(supported)}.",
        }

    grade_factor = GRADE_FACTORS[request.quality_grade]
    max_price = max(
        mandi["modal"][request.crop] * grade_factor
        for mandi in MANDIS
    )
    mandi_recommendations = [
        recommendation_for_mandi(mandi, request, max_price)
        for mandi in MANDIS
    ]
    mandi_recommendations.sort(
        key=lambda item: item["estimated_net_price_per_qtl"],
        reverse=True,
    )
    for rank, item in enumerate(mandi_recommendations, start=1):
        item["rank"] = rank

    buyer_recommendations = [
        recommendation_for_buyer(buyer, request)
        for buyer in BUYERS
    ]
    buyer_recommendations.sort(
        key=lambda item: (
            item["eligible"],
            item.get("estimated_net_price_per_qtl") or float("-inf"),
        ),
        reverse=True,
    )
    for rank, item in enumerate(buyer_recommendations, start=1):
        item["rank"] = rank

    return {
        "source": "demo-dataset",
        "crop": request.crop,
        "quantity_qtl": request.quantity_qtl,
        "quality_grade": request.quality_grade,
        "quality_grade_name": GRADE_NAMES[request.quality_grade],
        "recommendations": mandi_recommendations,
        "buyer_recommendations": buyer_recommendations,
        "pooling_suggestion": build_pool_suggestion(request, buyer_recommendations, mandi_recommendations[0]["mandi"]),
        "cost_assumptions": {
            "truck_capacity_qtl": TRUCK_CAPACITY_QTL,
            "base_truck_cost": BASE_TRUCK_COST,
            "truck_cost_per_km": TRUCK_COST_PER_KM,
            "apmc_fee_rate": APMC_FEE_RATE,
            "commission_rate": COMMISSION_RATE,
            "hamali_per_qtl": HAMALI_PER_QTL,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)