"""
Shop Command Center — Static Knowledge Base
Pre-loaded vehicle specs and service pricing guidelines.
Used to inject accurate facts into AI prompts, reducing token usage
and preventing hallucinated specs.
"""

# ── Vehicle Specs ─────────────────────────────────────────────────────────────
# Mirror of the 10 vehicles shown in the frontend ComponentCare panel.
# Keys are lowercase "make model" for fuzzy matching.

VEHICLES = {
    "toyota camry": {
        "name": "Toyota Camry (2018-2023)",
        "engines": ["2.5L 4-cyl A25A-FKS", "3.5L V6 2GR-FKS"],
        "oil": "0W-20 Full Synthetic",
        "oil_cap": "4.8 qt (2.5L) / 6.4 qt (3.5L)",
        "coolant": "Toyota Pink SLLC",
        "spark_plug": "NGK DILKAR6A11GS",
        "torque": {
            "Lug Nuts": "76 ft-lb",
            "Drain Plug": "30 ft-lb",
            "Caliper Bolts": "25 ft-lb",
        },
        "intervals": {
            "Oil Change": "10,000 mi",
            "Cabin Air Filter": "15,000 mi",
            "Engine Air Filter": "30,000 mi",
            "Spark Plugs (2.5L)": "60,000 mi",
            "Transmission Fluid": "60,000 mi",
            "Coolant Flush": "100,000 mi",
        },
        "known_issues": [
            "Oil consumption >1 qt/5k mi (2.5L pre-2021 build)",
            "Sunroof drain clogs leading to interior leaks",
            "Catalytic converter theft risk — high target vehicle",
        ],
    },
    "honda accord": {
        "name": "Honda Accord (2018-2022)",
        "engines": ["1.5L Turbo L15B7", "2.0L Turbo K20C4"],
        "oil": "0W-20 Full Synthetic",
        "oil_cap": "3.4 qt (1.5T) / 5.1 qt (2.0T)",
        "coolant": "Honda Blue Type 2",
        "spark_plug": "NGK ILZKR7B11GS",
        "torque": {
            "Lug Nuts": "80 ft-lb",
            "Drain Plug": "29 ft-lb",
            "Caliper Bolts (front)": "37 ft-lb",
        },
        "intervals": {
            "Oil Change": "7,500 mi (1.5T) / 5,000 mi (2.0T)",
            "Cabin Air Filter": "15,000 mi",
            "Engine Air Filter": "30,000 mi",
            "Spark Plugs": "30,000 mi",
            "Coolant Flush": "60,000 mi",
        },
        "known_issues": [
            "1.5T oil dilution in cold climates — monitor closely",
            "CVT judder at low speeds on some 2018-2019 units",
            "Bluetooth connectivity drops after software updates",
        ],
    },
    "ford f-150": {
        "name": "Ford F-150 (2018-2023)",
        "engines": ["5.0L V8 Coyote", "2.7L EcoBoost V6", "3.5L EcoBoost V6"],
        "oil": "5W-30 (5.0L) / 5W-30 (EcoBoost)",
        "oil_cap": "7.7 qt (5.0L) / 6.0 qt (2.7T)",
        "coolant": "Ford Orange VC-3-B",
        "spark_plug": "Motorcraft SP-537 (5.0L)",
        "torque": {
            "Lug Nuts": "150 ft-lb",
            "Drain Plug": "19 ft-lb",
            "Caliper Bolts": "26 ft-lb",
        },
        "intervals": {
            "Oil Change": "7,500 mi (dino) / 10,000 mi (syn)",
            "Engine Air Filter": "30,000 mi",
            "Spark Plugs": "60,000 mi",
            "Transmission Fluid": "150,000 mi (normal) / 60,000 mi (towing)",
            "Transfer Case Fluid": "150,000 mi",
        },
        "known_issues": [
            "EcoBoost carbon buildup on intake valves (walnut blast at 60k)",
            "Panoramic roof wind noise on 2019-2021",
            "Tailgate latch sticking in cold weather",
        ],
    },
    "chevrolet silverado": {
        "name": "Chevrolet Silverado 1500 (2019-2023)",
        "engines": ["5.3L V8 L84", "6.2L V8 L87"],
        "oil": "0W-20 Full Synthetic (AFM)",
        "oil_cap": "6.0 qt (5.3L) / 8.0 qt (6.2L)",
        "coolant": "Dex-Cool Orange",
        "spark_plug": "ACDelco 41-164",
        "torque": {
            "Lug Nuts": "140 ft-lb",
            "Drain Plug": "18 ft-lb",
            "Caliper Bolts": "32 ft-lb",
        },
        "intervals": {
            "Oil Change": "7,500 mi",
            "Engine Air Filter": "30,000 mi",
            "Spark Plugs": "100,000 mi",
            "Transmission Fluid": "45,000 mi (towing) / 100,000 mi (normal)",
        },
        "known_issues": [
            "AFM/DFM lifter failures on 5.3L — watch for tick at startup",
            "Oil consumption with active fuel management enabled",
            "Trailer brake controller sensitivity complaints",
        ],
    },
    "toyota tacoma": {
        "name": "Toyota Tacoma (2016-2023)",
        "engines": ["2.7L 4-cyl 2TR-FE", "3.5L V6 2GR-FKS"],
        "oil": "0W-20 Full Synthetic",
        "oil_cap": "5.5 qt (2.7L) / 6.2 qt (3.5L)",
        "coolant": "Toyota Pink SLLC",
        "spark_plug": "NGK ILFR5E11 (3.5L)",
        "torque": {
            "Lug Nuts": "85 ft-lb",
            "Drain Plug": "27 ft-lb",
            "Caliper Bolts": "25 ft-lb",
        },
        "intervals": {
            "Oil Change": "5,000 mi (2.7L) / 10,000 mi (3.5L)",
            "Cabin Air Filter": "15,000 mi",
            "Engine Air Filter": "30,000 mi",
            "Spark Plugs": "60,000 mi",
            "Differential Fluid": "30,000 mi (4WD)",
        },
        "known_issues": [
            "Frame rust concerns on older units in salt-belt states",
            "Infotainment system slow response on early 2016-2018",
            "Rear leaf spring squeaks common — lube or replace bushings",
        ],
    },
    "honda civic": {
        "name": "Honda Civic (2016-2021)",
        "engines": ["1.5L Turbo L15B7", "2.0L NA R20C1"],
        "oil": "0W-20 Full Synthetic",
        "oil_cap": "3.4 qt (1.5T) / 3.7 qt (2.0L)",
        "coolant": "Honda Blue Type 2",
        "spark_plug": "NGK SILZKR7B11GS",
        "torque": {
            "Lug Nuts": "80 ft-lb",
            "Drain Plug": "29 ft-lb",
            "Caliper Bolts (front)": "25 ft-lb",
        },
        "intervals": {
            "Oil Change": "7,500 mi (1.5T) / 5,000 mi (2.0L)",
            "Cabin Air Filter": "15,000 mi",
            "Spark Plugs": "30,000 mi",
            "Coolant Flush": "60,000 mi",
        },
        "known_issues": [
            "1.5T oil dilution — especially cold starts in northern climates",
            "AC compressor failure on 2016-2018 1.5T",
            "Adhesive-mounted trim panels separating in heat",
        ],
    },
    "ram 1500": {
        "name": "Ram 1500 (2019-2023)",
        "engines": ["5.7L HEMI V8", "3.6L Pentastar V6", "3.0L EcoDiesel V6"],
        "oil": "5W-20 (HEMI) / 5W-20 (V6)",
        "oil_cap": "7.0 qt (HEMI) / 5.9 qt (V6)",
        "coolant": "HOAT Orange",
        "spark_plug": "Champion RC12ECC (HEMI)",
        "torque": {
            "Lug Nuts": "130 ft-lb",
            "Drain Plug": "20 ft-lb",
            "Caliper Bolts": "32 ft-lb",
        },
        "intervals": {
            "Oil Change": "8,000 mi",
            "Engine Air Filter": "30,000 mi",
            "Spark Plugs": "30,000 mi (HEMI)",
            "Transmission Fluid": "60,000 mi",
            "Transfer Case": "60,000 mi",
        },
        "known_issues": [
            "HEMI tick on startup — common MDS lifter wear",
            "Uconnect system freezes requiring battery reset",
            "EcoDiesel 3.0L NOx emission recall — verify completion",
        ],
    },
    "toyota corolla": {
        "name": "Toyota Corolla (2020-2023)",
        "engines": ["2.0L 4-cyl M20A-FKS", "1.8L Hybrid 2ZR-FXE"],
        "oil": "0W-16 Full Synthetic",
        "oil_cap": "4.4 qt (2.0L) / 3.9 qt (Hybrid)",
        "coolant": "Toyota Pink SLLC",
        "spark_plug": "NGK ILKAR7L11",
        "torque": {
            "Lug Nuts": "76 ft-lb",
            "Drain Plug": "27 ft-lb",
            "Caliper Bolts": "25 ft-lb",
        },
        "intervals": {
            "Oil Change": "10,000 mi",
            "Cabin Air Filter": "15,000 mi",
            "Engine Air Filter": "30,000 mi",
            "Spark Plugs": "120,000 mi",
            "Hybrid Battery Check": "Annual (Hybrid)",
        },
        "known_issues": [
            "Rearview camera delay on cold starts",
            "Road noise from rear wheel wells — install additional deadening",
            "Hybrid battery warranty — 10 yr / 150k in ZEV states",
        ],
    },
    "honda cr-v": {
        "name": "Honda CR-V (2017-2022)",
        "engines": ["1.5L Turbo L15B7", "2.4L NA K24W (2017)"],
        "oil": "0W-20 Full Synthetic",
        "oil_cap": "3.4 qt",
        "coolant": "Honda Blue Type 2",
        "spark_plug": "NGK ILZKR7B11GS",
        "torque": {
            "Lug Nuts": "80 ft-lb",
            "Drain Plug": "29 ft-lb",
            "Caliper Bolts": "37 ft-lb",
        },
        "intervals": {
            "Oil Change": "7,500 mi",
            "Cabin Air Filter": "15,000 mi",
            "Engine Air Filter": "30,000 mi",
            "AWD Fluid": "30,000 mi",
        },
        "known_issues": [
            "1.5T oil dilution — worst on 2017-2018 in cold climates",
            "Infotainment screen delamination on 2017-2019",
            "CVT shudder at highway merge speeds",
        ],
    },
    "ford escape": {
        "name": "Ford Escape (2020-2023)",
        "engines": ["1.5L EcoBoost 3-cyl", "2.0L EcoBoost 4-cyl"],
        "oil": "5W-30 Full Synthetic",
        "oil_cap": "4.4 qt (1.5L) / 5.7 qt (2.0L)",
        "coolant": "Ford Orange VC-3-B",
        "spark_plug": "Motorcraft SP-534",
        "torque": {
            "Lug Nuts": "100 ft-lb",
            "Drain Plug": "19 ft-lb",
            "Caliper Bolts": "26 ft-lb",
        },
        "intervals": {
            "Oil Change": "7,500 mi",
            "Cabin Air Filter": "15,000 mi",
            "Engine Air Filter": "30,000 mi",
            "Spark Plugs": "60,000 mi",
        },
        "known_issues": [
            "1.5L 3-cyl coolant intrusion into cylinder — check TSB 21-2316",
            "PHEV range degradation in cold weather",
            "Reverse camera pixelation on 2020-2021",
        ],
    },
}

# ── Common Service Price Ranges ───────────────────────────────────────────────
# Used by repair estimator and preventive advisor to anchor cost estimates.

SERVICE_PRICES = {
    "Oil Change (conventional)":     "$35–$65",
    "Oil Change (synthetic)":        "$65–$110",
    "Oil Change (diesel)":           "$80–$130",
    "Cabin Air Filter":              "$25–$65 (parts+labor)",
    "Engine Air Filter":             "$20–$50 (parts+labor)",
    "Brake Pads (axle, parts+labor)":"$150–$300",
    "Brake Rotors (axle, parts+labor)":"$200–$400",
    "Brake Fluid Flush":             "$80–$130",
    "Spark Plugs (4-cyl)":          "$100–$200",
    "Spark Plugs (V6/V8)":          "$150–$350",
    "Coolant Flush":                 "$100–$180",
    "Transmission Service (ATF)":    "$150–$250",
    "Differential Fluid":            "$80–$150",
    "Power Steering Flush":          "$80–$130",
    "Tire Rotation":                 "$20–$50",
    "Wheel Alignment":               "$80–$150",
    "Battery Replacement":           "$150–$250 (parts+labor)",
    "Alternator Replacement":        "$400–$800",
    "Starter Replacement":           "$300–$600",
    "Serpentine Belt":               "$100–$200",
    "Timing Belt (4-cyl)":          "$400–$700",
    "Timing Belt (V6)":             "$600–$1,000",
    "Water Pump":                    "$300–$600",
    "Thermostat":                    "$150–$300",
    "Radiator Replacement":          "$400–$900",
    "AC Recharge":                   "$150–$300",
    "AC Compressor":                 "$700–$1,200",
    "Oxygen Sensor":                 "$200–$400",
    "Catalytic Converter":           "$900–$2,500",
    "Wheel Bearing (each)":          "$250–$500",
    "CV Axle":                       "$300–$600",
    "Struts/Shocks (each)":         "$200–$450",
    "Control Arm":                   "$250–$600",
    "Tie Rod End":                   "$150–$350",
    "Sway Bar Link":                 "$80–$200",
}


# ── Lookup helpers ────────────────────────────────────────────────────────────

def find_vehicle(query: str) -> dict | None:
    """Return vehicle data if query mentions a known make+model."""
    q = query.lower()
    for key, data in VEHICLES.items():
        parts = key.split()           # e.g. ["toyota", "camry"]
        if all(p in q for p in parts):
            return data
    return None


def vehicle_context(v: dict) -> str:
    """Format vehicle specs as a compact string for prompt injection."""
    torque_str = ", ".join(f"{k}: {v2}" for k, v2 in v["torque"].items())
    intervals_str = ", ".join(f"{k}: {v2}" for k, v2 in v["intervals"].items())
    issues_str = " | ".join(v["known_issues"])
    return (
        f"{v['name']} | Engines: {', '.join(v['engines'])} | "
        f"Oil: {v['oil']} ({v['oil_cap']}) | Coolant: {v['coolant']} | "
        f"Spark Plug: {v['spark_plug']} | Torque — {torque_str} | "
        f"Intervals — {intervals_str} | Known Issues — {issues_str}"
    )


def price_context() -> str:
    """Return common service prices as a compact string."""
    return " | ".join(f"{k}: {v}" for k, v in SERVICE_PRICES.items())
