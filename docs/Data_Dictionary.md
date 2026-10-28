# RoadSafe GB — Comprehensive Data Dictionary

> **Source:** UK Department for Transport (DfT) STATS19 Road Safety Open Data (2024–2025)  
> **Licence:** Open Government Licence (OGL v3.0)  
> **Database:** MongoDB Community (`roadsafe`) & Power BI Fact/Dim Tables

---

## 1. Collisions Collection (`collisions` & `fact_collisions.csv`)

**Grain:** One document/row per recorded personal injury road collision.

| Attribute | Data Type | MongoDB Index | Description & Coding |
| :--- | :--- | :--- | :--- |
| `collision_index` | String | **Unique PK** | Unique 12-character UK police collision identifier (e.g. `2025010000001`). Combines year and incident ref. |
| `collision_year` | Integer | Compound | Year the collision occurred (`2024` or `2025`). |
| `collision_ref_no` | String | None | Within-year incident reference number allocated by reporting police force. |
| `date` | String / Date | Compound | Calendar date of collision (`YYYY-MM-DD`). |
| `month` | Integer | None | Calendar month number (`1` to `12`). |
| `month_name` | String | None | Full English month name (`January` to `December`). |
| `day` | Integer | None | Day of month (`1` to `31`). |
| `time` | String | None | 24-hour recorded time of incident (`HH:MM`). |
| `hour` | Integer | None | Extracted hour integer (`0` to `23`) for diurnal pattern mining. |
| `day_of_week` | Integer | None | Weekday code: 1 = Sunday, 2 = Monday, 3 = Tuesday, 4 = Wednesday, 5 = Thursday, 6 = Friday, 7 = Saturday. |
| `day_of_week_name`| String | None | Full English weekday name (`Sunday` through `Saturday`). |
| `collision_severity`| Integer | Compound | Numeric severity code: `1` = Fatal, `2` = Serious, `3` = Slight. |
| `severity` | String | None | Standard severity category (`Fatal`, `Serious`, `Slight`). |
| `is_fatal_or_serious` | Boolean | None | Flag: `true` if severity is Fatal or Serious (KSI), `false` if Slight. |
| `number_of_vehicles` | Integer | None | Total vehicles involved in this collision event. |
| `number_of_casualties`| Integer | None | Total individuals injured or killed in this collision event. |
| `speed_limit` | Integer | None | Posted speed limit in mph (`20`, `30`, `40`, `50`, `60`, `70`). Missing/unrecorded coded as `null`. |
| `weather_conditions` | String | None | Mapped environmental weather: `Fine no high winds`, `Raining no high winds`, `Snowing`, `Fog or mist`, `Other`, `Unknown`. |
| `light_conditions` | String | None | Lighting status: `Daylight`, `Darkness - lights lit`, `Darkness - lights unlit`, `Darkness - no lighting`. |
| `road_surface_conditions`| String | None | Surface state: `Dry`, `Wet or damp`, `Snow`, `Frost or ice`, `Flood over 3cm deep`. |
| `road_type` | String | None | Carriageway type: `Single carriageway`, `Dual carriageway`, `Roundabout`, `One way street`, `Slip road`. |
| `urban_rural` | String | None | Area classification: `Urban`, `Rural`, `Unallocated`. |
| `has_valid_coordinates`| Boolean | Index | Geospatial audit flag. `true` if coordinates are numeric and strictly within Great Britain bounds (`49.8°N - 60.9°N`, `-8.6°W - 1.8°E`). |
| `latitude` | Float | None | WGS84 Latitude coordinate (decimal degrees, rounded to 6 decimal places). |
| `longitude` | Float | None | WGS84 Longitude coordinate (decimal degrees, rounded to 6 decimal places). |
| `location` | GeoJSON Point | **2dsphere** | Standard GeoJSON format: `{"type": "Point", "coordinates": [longitude, latitude]}`. Only present when coordinates are valid. |
| `grid_cell` | String | Compound | Discrete spatial clustering identifier (e.g. `51.5_-0.1`), rounded to ~0.1° (~11 km grid). |

---

## 2. Vehicles Collection (`vehicles`)

**Grain:** One document per involved vehicle.

| Attribute | Data Type | MongoDB Index | Description & Coding |
| :--- | :--- | :--- | :--- |
| `vehicle_id` | String | **Unique PK** | Composite primary key: `{collision_index}_{vehicle_reference}`. |
| `collision_index` | String | **Foreign Key**| Join key referencing parent `collisions.collision_index`. |
| `collision_year` | Integer | Compound | Year of incident (`2025`). |
| `vehicle_reference` | Integer | None | Ordinal index of vehicle within the collision (`1`, `2`, `3`...). |
| `vehicle_type` | String | Compound | Mapped vehicle category: `Car`, `Van / Goods 3.5t or under`, `Pedal cycle`, `Motorcycle over 500cc`, `Bus or coach`, `Taxi`, etc. |
| `age_of_driver` | Integer | None | Driver age in completed years (null if unknown/unreported). |
| `sex_of_driver` | String | None | Driver gender: `Male`, `Female`, `Unknown`. |
| `age_of_vehicle` | Integer | None | Vehicle age in years based on registration year (null if unrecorded). |
| `engine_capacity_cc`| Integer | None | Engine displacement in cubic centimeters (e.g. `1598`, `1995`). |
| `generic_make_model`| String | None | Generic vehicle make and model where recorded. |

---

## 3. Casualties Collection (`casualties`)

**Grain:** One document per injured or deceased individual.

| Attribute | Data Type | MongoDB Index | Description & Coding |
| :--- | :--- | :--- | :--- |
| `casualty_id` | String | **Unique PK** | Composite primary key: `{collision_index}_{casualty_reference}`. |
| `collision_index` | String | **Foreign Key**| Join key referencing parent `collisions.collision_index`. |
| `collision_year` | Integer | Compound | Year of incident (`2025`). |
| `vehicle_reference` | Integer | None | Ordinal index of vehicle in which casualty was traveling (or struck by, for pedestrians). |
| `casualty_reference`| Integer | None | Ordinal index of casualty within the collision (`1`, `2`...). |
| `casualty_severity` | Integer | Compound | Numeric severity: `1` = Fatal, `2` = Serious, `3` = Slight. |
| `severity` | String | None | Category label: `Fatal`, `Serious`, `Slight`. |
| `casualty_class` | String | None | Role in collision: `Driver or rider`, `Passenger`, `Pedestrian`. |
| `sex_of_casualty` | String | None | Casualty gender: `Male`, `Female`, `Unknown`. |
| `age_of_casualty` | Integer | None | Casualty age in completed years (null if unrecorded). |

---

## 4. Calendar Dimension Table (`dim_calendar.csv`)

**Grain:** One row per calendar day across 2024 and 2025 (731 days).

| Attribute | Data Type | Power BI Role | Description |
| :--- | :--- | :--- | :--- |
| `date` | Date (YYYY-MM-DD)| **Primary Key** | Calendar date joined to `fact_collisions[date]`. |
| `year` | Integer | Slicer | Year integer (`2024` or `2025`). |
| `month_number` | Integer | Sort Column | Numeric month (`1` to `12`). Used to sort `month_name`. |
| `month_name` | String | Axis | Month name (`January` to `December`). |
| `day_of_month` | Integer | None | Day number (`1` to `31`). |
| `day_of_week` | Integer | Sort Column | ISO weekday (`1` = Monday, `7` = Sunday). |
| `weekday_name` | String | Axis / Slicer | Day name (`Monday` through `Sunday`). |
| `is_weekend` | Integer | Filter | Flag: `1` if Saturday/Sunday, `0` if weekday. |
| `quarter` | String | Drilldown | Fiscal/calendar quarter (`Q1`, `Q2`, `Q3`, `Q4`). |
| `year_month` | String | Trend Axis | Formatted period (`2024-01` to `2025-12`). |
