-- =====================================================================
-- POSTGIS SPATIAL TRADE AREA & STORE CANNIBALIZATION PIPELINE
-- Author: Puneet Goswami
-- Description: Generates 5km/10km catchment buffers around retail outlets
--              and calculates geographic polygon overlap and revenue risk.
-- =====================================================================

WITH store_trade_buffers AS (
    SELECT 
        store_id,
        store_name,
        market_city,
        store_status, -- 'EXISTING', 'PROPOSED_NEW'
        annual_gross_revenue_usd,
        geom_point,
        -- Generate 5km primary drive-time buffer (EPSG:3857 metric projection)
        ST_Buffer(geom_point::geography, 5000)::geometry AS catchment_5km_geom
    FROM spatial_dw.dim_store_locations
    WHERE is_active = TRUE
),

store_pairwise_intersections AS (
    SELECT 
        s1.store_id AS target_store_id,
        s1.store_name AS target_store_name,
        s1.market_city,
        s1.store_status AS target_status,
        s1.annual_gross_revenue_usd AS target_base_revenue_usd,
        s2.store_id AS overlapping_store_id,
        s2.store_name AS overlapping_store_name,
        s2.annual_gross_revenue_usd AS overlapping_store_rev_usd,
        
        -- Exact distance in kilometers between store centroids
        ROUND((ST_Distance(s1.geom_point::geography, s2.geom_point::geography) / 1000.0)::NUMERIC, 2) AS distance_km,

        -- Calculate area of intersection between catchment polygons in sq km
        ROUND((ST_Area(ST_Intersection(s1.catchment_5km_geom, s2.catchment_5km_geom)::geography) / 1000000.0)::NUMERIC, 2) AS overlap_area_sq_km,

        -- Base area of 5km radius buffer (pi * 5^2 ≈ 78.54 sq km)
        ROUND((ST_Area(s1.catchment_5km_geom::geography) / 1000000.0)::NUMERIC, 2) AS primary_catchment_sq_km
    FROM store_trade_buffers s1
    JOIN store_trade_buffers s2 
      ON s1.store_id <> s2.store_id 
     AND ST_DWithin(s1.geom_point::geography, s2.geom_point::geography, 10000) -- Only evaluate stores within 10km radius
),

cannibalization_impact_metrics AS (
    SELECT 
        target_store_id,
        target_store_name,
        market_city,
        target_status,
        target_base_revenue_usd,
        overlapping_store_id,
        overlapping_store_name,
        distance_km,
        overlap_area_sq_km,
        
        -- Catchment Overlap Ratio (% of target store catchment captured by neighbour)
        ROUND((overlap_area_sq_km * 100.0) / NULLIF(primary_catchment_sq_km, 0), 2) AS territory_overlap_pct,

        -- Estimated cannibalized sales drag (proportional to spatial overlap weight)
        ROUND((target_base_revenue_usd * 0.40) * (overlap_area_sq_km / NULLIF(primary_catchment_sq_km, 0)), 2) AS estimated_revenue_cannibalization_usd
    FROM store_pairwise_intersections
)

SELECT 
    target_store_id,
    target_store_name,
    market_city,
    target_status,
    overlapping_store_name,
    distance_km,
    overlap_area_sq_km,
    territory_overlap_pct,
    estimated_revenue_cannibalization_usd,
    
    -- Real Estate Strategic Expansion Flag
    CASE 
        WHEN territory_overlap_pct >= 45.0 THEN 'HIGH_CANNIBALIZATION_HALT_EXPANSION'
        WHEN territory_overlap_pct >= 20.0 THEN 'MODERATE_OVERLAP_ADJUST_FOOTPRINT'
        ELSE 'ACCRETIVE_EXPANSION_ZONE'
    END AS expansion_decision_verdict
FROM cannibalization_impact_metrics
WHERE target_status = 'PROPOSED_NEW'
ORDER BY estimated_revenue_cannibalization_usd DESC;