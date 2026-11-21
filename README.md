# Retail Store Catchment & Revenue Cannibalization Analysis

A location analytics workflow using spatial buffer overlaps to estimate whether a proposed retail store adds net new revenue or pulls sales from nearby existing branches.

## Problem Context
Opening new stores too close to existing locations inflates capex while shifting existing customers between branches. This project calculates 5km/10km trade-area overlaps to estimate net incremental sales before site approval.

## Files
- `spatial_cannibalization_pipeline.sql`: PostGIS query using `ST_Buffer`, `ST_DWithin`, and `ST_Intersection` to measure overlapping store catchments.
- `geospatial_expansion_engine.py`: Calculates lens overlap area and net accretive revenue after subtracting cannibalized volume.
- `requirements.txt`: Python dependencies.

## How It Works
1. **Trade-Area Buffers:** Builds 5km radius polygons around candidate sites and existing stores.
2. **Overlap Measurement:** Computes shared catchment area to estimate traffic diversion from nearby branches.
3. **Net Revenue Check:** Deducts expected cannibalization from projected gross sales to rank expansion candidates.

## Run Locally

    git clone https://github.com/puneetgoswami1/geospatial-retail-penetration-engine.git
    cd geospatial-retail-penetration-engine
    pip install -r requirements.txt
    python geospatial_expansion_engine.py
