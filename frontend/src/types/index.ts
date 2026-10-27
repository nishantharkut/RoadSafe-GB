export interface OverviewData {
  total_collisions: number;
  total_casualties: number;
  total_vehicles: number;
  fatal_count: number;
  serious_count: number;
  slight_count: number;
  serious_fatal_share_pct: number;
  avg_casualties_per_collision: number;
  monthly_trend: {
    month: string;
    month_number: number;
    count: number;
    fatal: number;
    serious: number;
    slight: number;
  }[];
  severity_composition: {
    name: string;
    count: number;
    color: string;
  }[];
  filters_applied?: {
    year: string;
    severity: string;
  };
}

export interface TrendsData {
  hourly: {
    hour: string;
    hour_number: number;
    total: number;
    fatal_serious: number;
    slight: number;
    serious_fatal_share_pct: number;
  }[];
  weekday: {
    day_number: number;
    day: string;
    total: number;
    fatal_serious: number;
    slight: number;
    serious_fatal_share_pct: number;
  }[];
  monthly: {
    month_number: number;
    month: string;
    total: number;
    fatal_serious: number;
    slight: number;
    serious_fatal_share_pct: number;
  }[];
}

export interface Hotspot {
  grid_id: string;
  count: number;
  fatal_count: number;
  serious_count: number;
  slight_count: number;
  total_casualties: number;
  serious_fatal_share_pct: number;
  latitude: number;
  longitude: number;
}

export interface HotspotsResponse {
  total_hotspots: number;
  min_count_threshold: number;
  year: string;
  severity: string;
  hotspots: Hotspot[];
}

export interface SeverityCategory {
  category: string;
  total: number;
  fatal: number;
  serious: number;
  slight: number;
  serious_fatal_share_pct: number;
}

export interface SeverityResponse {
  field: string;
  year: string;
  categories: SeverityCategory[];
}

export interface CombinatorialRiskItem {
  speed_limit: string;
  speed_raw: number;
  light_conditions: string;
  weather_conditions: string;
  urban_rural: string;
  total_collisions: number;
  fatal_count: number;
  serious_count: number;
  slight_count: number;
  serious_fatal_share_pct: number;
  avg_casualties_per_collision: number;
  relative_risk: number;
  odds_ratio: number;
  risk_tier: string;
}

export interface CombinationsResponse {
  year: string;
  total_combinations_mined: number;
  combinations: CombinatorialRiskItem[];
}

export interface ScenarioParams {
  speed_limit: number;
  light_conditions: string;
  weather_conditions: string;
  urban_rural: string;
  road_surface_conditions?: string;
}

export interface ScenarioResult {
  parameters: ScenarioParams;
  total_collisions: number;
  fatal_count: number;
  serious_count: number;
  slight_count: number;
  serious_fatal_share_pct: number;
  total_casualties: number;
  avg_casualties_per_collision: number;
}

export interface ScenarioComparisonResponse {
  scenario_a: ScenarioResult;
  scenario_b: ScenarioResult;
  comparison: {
    severe_share_diff_pct: number;
    risk_multiplier: number;
    higher_risk_scenario: string;
  };
}

export interface IndexBenchmarkDetail {
  index_name: string;
  stage: string;
  execution_time_ms: number;
  docs_examined: number;
  keys_examined: number;
  docs_returned: number;
}

export interface IndexBenchmarkItem {
  benchmark_id: string;
  name: string;
  query_filter: string;
  indexed: IndexBenchmarkDetail;
  unindexed: IndexBenchmarkDetail;
  speedup_factor: number;
}

export interface BenchmarksResponse {
  database: string;
  timestamp: string;
  total_documents_tested: number;
  benchmarks: IndexBenchmarkItem[];
}

export interface CollisionRecord {
  collision_index: string;
  collision_year: number;
  collision_ref_no: string;
  date: string;
  time: string;
  severity: string;
  number_of_vehicles: number;
  number_of_casualties: number;
  speed_limit: number | null;
  road_type: string;
  weather_conditions: string;
  light_conditions: string;
  road_surface_conditions: string;
  urban_rural: string;
  first_road_number: string;
  latitude: number | null;
  longitude: number | null;
}

export interface CollisionRecordsResponse {
  records: CollisionRecord[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Vehicle {
  vehicle_id: string;
  vehicle_reference: number;
  vehicle_type: string;
  age_of_driver: number | null;
  sex_of_driver: string;
  age_of_vehicle: number | null;
  engine_capacity_cc: number | null;
  generic_make_model?: string;
}

export interface Casualty {
  casualty_id: string;
  casualty_reference: number;
  casualty_class: string;
  severity: string;
  sex_of_casualty: string;
  age_of_casualty: number | null;
}

export interface CollisionDetail extends CollisionRecord {
  vehicles: Vehicle[];
  casualties: Casualty[];
}

export interface DataQualityReport {
  total_collisions: number;
  collisions_2024: number;
  collisions_2025: number;
  total_vehicles: number;
  total_casualties: number;
  valid_coordinates: number;
  invalid_coordinates: number;
  coordinate_completeness_pct: number;
  missing_time_count: number;
  missing_speed_limit_count: number;
  database_name: string;
  publisher: string;
  licence: string;
  indexes: {
    collisions: string[];
    vehicles: string[];
    casualties: string[];
  };
}
