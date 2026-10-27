"""
Geospatial Retail Market Penetration & Cannibalization Engine
Author: Puneet Goswami
Description: Models retail store networks, calculates spatial catchment overlap 
             percentages, and estimates revenue cannibalization on existing outlets.
"""

import numpy as np
import pandas as pd


def haversine_distance_km(lat1, lon1, lat2, lon2):
    """Calculates great-circle distance between coordinate pairs in kilometers."""
    R = 6371.0  # Earth's radius in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat / 2) ** 2 +
         np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2)
    return 2 * R * np.arcsin(np.sqrt(a))


def circle_intersection_area(d, r1=5.0, r2=5.0):
    """Calculates lens intersection area between two overlapping circular buffers."""
    if d >= r1 + r2:
        return 0.0
    if d <= abs(r1 - r2):
        return np.pi * min(r1, r2) ** 2

    alpha = 2 * np.arccos((d**2 + r1**2 - r2**2) / (2 * d * r1))
    beta = 2 * np.arccos((d**2 + r2**2 - r1**2) / (2 * d * r2))
    area1 = 0.5 * r1**2 * (alpha - np.sin(alpha))
    area2 = 0.5 * r2**2 * (beta - np.sin(beta))
    return area1 + area2


def run_expansion_simulation():
    np.random.seed(42)

    # Simulated metropolitan market (existing retail store network)
    existing_stores = pd.DataFrame({
        "store_id": [f"STR-EX-{101 + i}" for i in range(10)],
        "name": [f"Retail Hub #{i+1}" for i in range(10)],
        "lat": np.random.uniform(28.45, 28.70, size=10),
        "lon": np.random.uniform(77.05, 77.30, size=10),
        "annual_revenue_usd": np.random.uniform(1800000, 3200000, size=10)
    })

    # Proposed new candidate sites under evaluation
    candidate_sites = pd.DataFrame({
        "candidate_id": ["SITE-NEW-01", "SITE-NEW-02", "SITE-NEW-03"],
        "proposed_name": ["Sector 44 Express", "Cyber Park Flagship", "Airport Aerocity Hub"],
        "lat": [28.52, 28.61, 28.58],
        "lon": [77.12, 77.22, 77.10],
        "projected_revenue_usd": [2200000, 2600000, 2400000]
    })

    catchment_radius_km = 5.0
    catchment_area_sq_km = np.pi * (catchment_radius_km ** 2)

    print("==========================================================================")
    print("GEOSPATIAL EXPANSION ANALYSIS: STORE CANNIBALIZATION AUDIT")
    print("==========================================================================")
    print(f"Trade Area Buffer Definition: {catchment_radius_km:.1f} km Drive-Time Radius ({catchment_area_sq_km:.1f} sq km Area)\n")

    for _, site in candidate_sites.iterrows():
        print(f"--- Evaluating Proposed Site: {site['proposed_name']} ({site['candidate_id']}) ---")
        site_lat, site_lon = site["lat"], site["lon"]

        distances = haversine_distance_km(site_lat, site_lon, existing_stores["lat"], existing_stores["lon"])
        nearby_mask = distances <= (catchment_radius_km * 2)

        if not nearby_mask.any():
            print("  Result: 100% Incremental Catchment. Zero cannibalization detected.")
            print(f"  Net Projected Accretive Revenue: ${site['projected_revenue_usd']:,.2f}\n")
            continue

        total_revenue_cannibalized = 0.0

        for idx in np.where(nearby_mask)[0]:
            store = existing_stores.iloc[idx]
            dist = distances.iloc[idx]
            overlap_sq_km = circle_intersection_area(dist, catchment_radius_km, catchment_radius_km)
            overlap_pct = (overlap_sq_km / catchment_area_sq_km) * 100

            # Revenue drag modeled at 40% margin sensitivity on overlap
            revenue_drag = store["annual_revenue_usd"] * 0.40 * (overlap_sq_km / catchment_area_sq_km)
            total_revenue_cannibalized += revenue_drag

            print(f"  * Overlap with {store['name']:18s} | Distance: {dist:.2f} km | Buffer Overlap: {overlap_pct:.1f}% | Revenue Drag: ${revenue_drag:,.2f}")

        net_accretive_revenue = site["projected_revenue_usd"] - total_revenue_cannibalized
        cannibalization_rate = (total_revenue_cannibalized / site["projected_revenue_usd"]) * 100

        print(f"  Total Cannibalized Revenue Risk : ${total_revenue_cannibalized:,.2f}")
        print(f"  Net Accretive New Revenue       : ${net_accretive_revenue:,.2f} ({100 - cannibalization_rate:.1f}% Net Incremental)")
        verdict = "APPROVE (Accretive)" if cannibalization_rate < 25.0 else "REVISE LOCATION (High Overlap Risk)"
        print(f"  Real Estate Investment Committee : {verdict}\n")


if __name__ == "__main__":
    run_expansion_simulation()