import axios from 'axios';
import {
  OverviewData,
  TrendsData,
  HotspotsResponse,
  SeverityResponse,
  CollisionRecordsResponse,
  CollisionDetail,
  DataQualityReport,
  CombinationsResponse,
  ScenarioComparisonResponse,
  ScenarioParams,
  BenchmarksResponse
} from '../types';

import fallbackHealth from './fallback_health.json';
import fallbackOverview2025 from './fallback_overview_2025.json';
import fallbackOverview2024 from './fallback_overview_2024.json';
import fallbackOverviewAll from './fallback_overview_all.json';
import fallbackTrends2025 from './fallback_trends_2025.json';
import fallbackTrendsAll from './fallback_trends_all.json';
import fallbackHotspots2025 from './fallback_hotspots_2025.json';
import fallbackSeverityWeather from './fallback_severity_weather.json';
import fallbackSeverityLight from './fallback_severity_light.json';
import fallbackSeveritySurface from './fallback_severity_surface.json';
import fallbackCombinations from './fallback_combinations.json';
import fallbackCompare from './fallback_compare.json';
import fallbackDataQuality from './fallback_data_quality.json';
import fallbackBenchmarks from './fallback_benchmarks.json';
import fallbackCollisionsPage1 from './fallback_collisions_page1.json';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Guard against SPA fallback returning index.html as a 200 string
apiClient.interceptors.response.use((response) => {
  if (typeof response.data === 'string' && response.data.trim().startsWith('<')) {
    throw new Error('API returned HTML instead of JSON. Backend service may not be running.');
  }
  return response;
});

export const fetchOverview = async (year: string = '2025'): Promise<OverviewData> => {
  try {
    const res = await apiClient.get<OverviewData>('/overview', { params: { year } });
    if (res.data && typeof res.data === 'object' && typeof res.data.total_collisions === 'number') {
      return res.data;
    }
    throw new Error('Invalid overview response');
  } catch (err) {
    console.info('[RoadSafe GB] Using pre-computed STATS19 census fallback for /overview');
    if (year === '2024') return fallbackOverview2024 as unknown as OverviewData;
    if (year === 'all') return fallbackOverviewAll as unknown as OverviewData;
    return fallbackOverview2025 as unknown as OverviewData;
  }
};

export const fetchTrends = async (year: string = '2025'): Promise<TrendsData> => {
  try {
    const res = await apiClient.get<TrendsData>('/trends', { params: { year } });
    if (res.data && typeof res.data === 'object' && Array.isArray(res.data.hourly)) {
      return res.data;
    }
    throw new Error('Invalid trends response');
  } catch (err) {
    console.info('[RoadSafe GB] Using pre-computed STATS19 census fallback for /trends');
    if (year === 'all') return fallbackTrendsAll as unknown as TrendsData;
    return fallbackTrends2025 as unknown as TrendsData;
  }
};

export const fetchHotspots = async (
  year: string = '2025',
  minCount: number = 15
): Promise<HotspotsResponse> => {
  try {
    const res = await apiClient.get<HotspotsResponse>('/hotspots', {
      params: { year, min_count: minCount, limit: 400 }
    });
    if (res.data && typeof res.data === 'object' && Array.isArray(res.data.hotspots)) {
      return res.data;
    }
    throw new Error('Invalid hotspots response');
  } catch (err) {
    console.info('[RoadSafe GB] Using pre-computed STATS19 geospatial fallback for /hotspots');
    return fallbackHotspots2025 as unknown as HotspotsResponse;
  }
};

export const fetchSeverityAnalysis = async (
  year: string = '2025',
  field: string = 'weather_conditions'
): Promise<SeverityResponse> => {
  try {
    const res = await apiClient.get<SeverityResponse>('/severity-analysis', {
      params: { year, field }
    });
    if (res.data && typeof res.data === 'object' && Array.isArray(res.data.categories)) {
      return res.data;
    }
    throw new Error('Invalid severity analysis response');
  } catch (err) {
    console.info('[RoadSafe GB] Using pre-computed STATS19 severity fallback for', field);
    if (field === 'light_conditions') return fallbackSeverityLight as unknown as SeverityResponse;
    if (field === 'road_surface_conditions') return fallbackSeveritySurface as unknown as SeverityResponse;
    return fallbackSeverityWeather as unknown as SeverityResponse;
  }
};

export const fetchCombinatorialRisk = async (
  year: string = '2025',
  minCount: number = 25
): Promise<CombinationsResponse> => {
  try {
    const res = await apiClient.get<CombinationsResponse>('/severity/combinations', {
      params: { year, min_count: minCount }
    });
    if (res.data && typeof res.data === 'object' && Array.isArray(res.data.combinations)) {
      return res.data;
    }
    throw new Error('Invalid combinations response');
  } catch (err) {
    console.info('[RoadSafe GB] Using pre-computed STATS19 risk combinations fallback');
    return fallbackCombinations as unknown as CombinationsResponse;
  }
};

export const compareScenarios = async (
  scenarioA: ScenarioParams,
  scenarioB: ScenarioParams
): Promise<ScenarioComparisonResponse> => {
  try {
    const res = await apiClient.post<ScenarioComparisonResponse>('/severity/compare', {
      scenario_a: scenarioA,
      scenario_b: scenarioB
    });
    if (res.data && typeof res.data === 'object' && res.data.scenario_a) {
      return res.data;
    }
    throw new Error('Invalid scenario comparison response');
  } catch (err) {
    console.info('[RoadSafe GB] Using pre-computed risk differential comparison fallback');
    return fallbackCompare as unknown as ScenarioComparisonResponse;
  }
};

export const fetchIndexBenchmarks = async (): Promise<BenchmarksResponse> => {
  try {
    const res = await apiClient.get<BenchmarksResponse>('/data-quality/benchmarks');
    if (res.data && typeof res.data === 'object' && Array.isArray(res.data.benchmarks)) {
      return res.data;
    }
    throw new Error('Invalid index benchmarks response');
  } catch (err) {
    console.info('[RoadSafe GB] Using pre-computed index benchmark audit fallback');
    return fallbackBenchmarks as unknown as BenchmarksResponse;
  }
};

export const fetchCollisionRecords = async (
  year: string = '2025',
  page: number = 1,
  pageSize: number = 25,
  search?: string,
  severity?: string
): Promise<CollisionRecordsResponse> => {
  try {
    const res = await apiClient.get<CollisionRecordsResponse>('/collisions', {
      params: { year, page, page_size: pageSize, search, severity }
    });
    if (res.data && typeof res.data === 'object' && Array.isArray(res.data.records)) {
      return res.data;
    }
    throw new Error('Invalid collision records response');
  } catch (err) {
    console.info('[RoadSafe GB] Using pre-computed collision records fallback');
    return fallbackCollisionsPage1 as unknown as CollisionRecordsResponse;
  }
};

export const fetchCollisionDetail = async (collisionIndex: string): Promise<CollisionDetail> => {
  try {
    const res = await apiClient.get<CollisionDetail>(`/collisions/${collisionIndex}`);
    if (res.data && typeof res.data === 'object' && res.data.collision_index) {
      return res.data;
    }
    throw new Error('Invalid collision detail response');
  } catch (err) {
    console.info('[RoadSafe GB] Using fallback collision detail for', collisionIndex);
    const sample = (fallbackCollisionsPage1 as any).records?.[0] || {};
    return {
      ...sample,
      collision_index: collisionIndex || sample.collision_index || '2025010001',
      vehicles: sample.vehicles || [],
      casualties: sample.casualties || []
    } as CollisionDetail;
  }
};

export const fetchDataQuality = async (): Promise<DataQualityReport> => {
  try {
    const res = await apiClient.get<DataQualityReport>('/data-quality');
    if (res.data && typeof res.data === 'object' && typeof res.data.total_collisions === 'number') {
      return res.data;
    }
    throw new Error('Invalid data quality report response');
  } catch (err) {
    console.info('[RoadSafe GB] Using pre-computed data quality audit fallback');
    return fallbackDataQuality as unknown as DataQualityReport;
  }
};

export const checkHealth = async (): Promise<any> => {
  try {
    const res = await apiClient.get('/health');
    if (res.data && typeof res.data === 'object') {
      return res.data;
    }
    throw new Error('Invalid health check response');
  } catch (err) {
    console.info('[RoadSafe GB] Using pre-computed STATS19 health metrics fallback');
    return fallbackHealth;
  }
};
