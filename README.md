# Geospatial Retail Market Penetration & Cannibalization Engine

A location intelligence analytics engine combining spatial polygon buffer analysis and demographic catchment modeling to guide retail network expansion while preventing revenue cannibalization.

## Overview
Aggressive retail expansion risks opening new storefronts that siphon traffic from existing corporate outlets rather than stealing market share from competitors. This framework computes 5km/10km drive-time trade areas, determines spatial overlap geometry, and quantifies expected revenue displacement before capital expenditure is committed.

## Project Structure
- `spatial_cannibalization_pipeline.sql`: Production PostGIS SQL pipeline executing `ST_Buffer`, `ST_DWithin`, and `ST_Intersection` on store coordinates.
- `geospatial_expansion_engine.py`: Python mathematical engine calculating circular catchment lens overlaps and net accretive revenue contributions.
- `requirements.txt`: Python package dependencies.

## Key Spatial Metrics
1. **Catchment Buffer (`ST_Buffer`):** Generates 5km radius trade-area polygons around candidate and existing store locations.
2. **Catchment Overlap Index:** Quantifies the shared geographic surface area ($km^2$) between overlapping store radiuses.
3. **Net Accretive Revenue:** Subtracts cannibalized baseline revenue from projected new store gross sales to ensure genuine top-line expansion.

## How to Run

```bash
# Clone the repository
git clone [https://github.com/puneetgoswami1/geospatial-retail-penetration-engine.git](https://github.com/puneetgoswami1/geospatial-retail-penetration-engine.git)
cd geospatial-retail-penetration-engine

# Install dependencies
pip install -r requirements.txt

# Run geospatial expansion model
python geospatial_expansion_engine.py