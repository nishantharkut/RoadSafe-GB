# RoadSafe GB — Viva & Evaluation Presentation Guide

> **Course:** Big Data Management (BDM)  
> **Topic:** Spatial and Temporal Mining of Road Accident Patterns in Great Britain  
> **Target Time:** 5 to 6 Minutes Live Demonstration

---

## 1. Five-Minute Presentation Script & Flow

### Minute 1: Problem Definition & Data Provenance (0:00 – 1:00)
- **Problem Statement:** "Road traffic injuries represent one of the leading causes of preventable mortality globally. However, road safety datasets are inherently complex: they involve high document volumes, multi-table cardinality (one collision involves multiple vehicles and casualties), spatio-temporal coordinates, and extensive categorical coding."
- **Authoritative Provenance:** "Rather than using an unverified Kaggle CSV or synthetic toy data, RoadSafe GB is built directly on the **UK Department for Transport (DfT) STATS19** national open dataset. We ingested the complete 2024 and 2025 collision records, alongside 2025 vehicles and casualties — totaling over **514,000 real records**."
- **Licence & Integrity:** "The data is published under the UK Open Government Licence (OGL v3.0). Every raw file's SHA-256 hash was verified during automated ETL."

### Minute 2: Big Data Architecture & MongoDB (1:00 – 2:15)
- **Show Compass / Terminal:** "Our pipeline is strictly decoupled into an ETL layer, a document database, a read-only Flask REST API, a light-mode React web client, and an imported Power BI star schema."
- **Why MongoDB?**:
  1. *Flexible Document Modeling:* Source STATS19 records contain 44 attributes including nested coordinates, temporal splits, and categorical status codes.
  2. *Geospatial 2dsphere Indexing:* We constructed standard GeoJSON `Point` geometries (`[longitude, latitude]`) with strict bounding-box validation for Great Britain (`49.8°N - 60.9°N`, `-8.6°W - 1.8°E`).
  3. *High-Performance Aggregations:* Instead of pulling raw data into frontend memory, MongoDB server-side aggregation pipelines compute monthly trends, hourly distributions, and grid-cell densities in single-digit milliseconds.
  4. *Multi-Table Join Handling:* We prevent join count inflation by pre-aggregating child vehicles and casualties before linking to parent collision IDs.

### Minute 3: Web Dashboard Demonstration (2:15 – 3:45)
- **Overview Page:**
  - Show the KPI band: **202,452 total collisions**, **25.54% Serious/Fatal Share**, **252k+ casualties**.
  - Show the Monthly volume curve: seasonal peaks in autumn/winter and diurnal commuter rush.
  - Switch Year filter from `2025` to `2024` or `All Years` — demonstrate that live MongoDB queries update all charts instantly.
- **Geographic Hotspot Visualizer:**
  - Open the Leaflet map: Show Great Britain's clustering.
  - Adjust the incident threshold slider (`min_count: 15, 25, 50, 100`).
  - Click a high-density cluster (e.g. Central London or Birmingham): Show the cluster inspector slide-out displaying exact centroid coordinates, volume, and serious/fatal share %.
- **Pattern Analysis & Records:**
  - Show diurnal peak hours (08:00 and 17:00 commuter spikes).
  - Open the Collision Records table: Search for `M25` or `A1`, click **Inspect** to reveal the joined vehicle and casualty child documents stored in MongoDB.

### Minute 4: Power BI Desktop Report (3:45 – 4:45)
- **Open Power BI / Guide:**
  - Show the clean star schema: `fact_collisions` linked via 1-to-many relationship to `dim_calendar` on `[date]`.
  - Explain why standalone tables (`agg_hotspots_grid`, `agg_severity_conditions`) are kept separate: to preserve fact table granularity and eliminate ambiguous many-to-many joins.
  - Show the verified DAX measures: `Total Collisions`, `Serious/Fatal Collision Share %`, `Avg Casualties per Collision`.
  - Reconcile numbers: Prove that Power BI's KPI cards match MongoDB's totals to the exact digit (**202,452 collisions**, **25.54% KSI share**).

### Minute 5: Critical Limitations & Conclusion (4:45 – 5:30)
- **Academic Boundaries:**
  - "Our findings are descriptive data mining, not causal claims or predictive machine learning."
  - "A hotspot cell does not inherently prove a road is unsafe; urban areas naturally accumulate higher incident counts due to population and traffic exposure denominators."
  - "The project represents personal injury collisions reported to police; property-damage-only incidents are outside statutory reporting scope."

---

## 2. Common Viva Examination Questions & Answers

### Q1: Why did you choose MongoDB instead of a traditional relational SQL database like PostgreSQL?
> **Answer:** "MongoDB provides optimal characteristics for this project:  
> 1. Ingestion flexibility: DfT STATS19 records contain dozens of attributes with occasional missing or revision codes that document storage accommodates natively.  
> 2. Native Geospatial Indexing: MongoDB’s `2dsphere` index allows spherical coordinate calculations and bounding queries directly on GeoJSON `Point` objects.  
> 3. Powerful Aggregation Framework: MongoDB’s `$group`, `$facet`, and `$bucket` stages allow us to execute complex temporal and spatial rollups on 500,000+ documents on the database server, returning lightweight, pre-computed JSON payloads to our web application."

### Q2: Why build a Power BI report if you already built a React web application?
> **Answer:** "They serve two distinct architectural purposes:  
> - The **React application** is an exploratory, operational interface providing interactive geographic clustering, dynamic API filtering, and drill-down inspection of individual database documents.  
> - **Power BI** is an enterprise reporting and business intelligence artifact. It validates that our data engineering pipeline produces clean, governed star-schema tables that business stakeholders can consume in Microsoft Fabric or Desktop without direct database dependencies."

### Q3: Did you use live DirectQuery or imported data in Power BI?
> **Answer:** "We implemented an imported snapshot architecture via refreshable CSV exports from MongoDB. In enterprise big data environments, connecting desktop BI tools directly to document databases can cause connection timeouts and complex ODBC schema-mapping issues. Exporting normalized fact and dimension tables guarantees deterministic DAX calculation performance and allows straightforward data refreshes whenever the ETL pipeline runs."

### Q4: How did you avoid join count multiplication when linking vehicles and casualties?
> **Answer:** "In road safety data, one collision can involve 3 vehicles and 4 casualties. A naive SQL-style flat join would duplicate the collision row 12 times, severely inflating total collision counts. In our MongoDB data model:  
> - Collisions, vehicles, and casualties are stored in separate collections with composite keys (`collision_index + vehicle_reference`).  
> - For aggregate collision metrics, we query the `collisions` collection directly.  
> - When multi-table metrics are required (such as vehicle fleet breakdown), we pre-aggregate child collections before joining, or calculate distinct `collision_index` counts."

### Q5: How do you know your numbers are authentic and not AI-generated mock data?
> **Answer:** "Every metric is verifiable end-to-end:  
> 1. We provide the automated download script (`etl/download_data.py`) with official DfT URLs and SHA-256 hashes.  
> 2. The database contains 202,452 actual collision documents that can be inspected directly in MongoDB Compass or via `mongosh`.  
> 3. Our test suite (`backend/tests/test_api.py`) runs automated assertions verifying that API responses match the database counts.  
> 4. Power BI imports the identical row counts and calculates identical DAX figures down to the decimal point."
