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

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const fetchOverview = async (year: string = '2025'): Promise<OverviewData> => {
  const res = await apiClient.get<OverviewData>('/overview', { params: { year } });
  return res.data;
};

export const fetchTrends = async (year: string = '2025'): Promise<TrendsData> => {
  const res = await apiClient.get<TrendsData>('/trends', { params: { year } });
  return res.data;
};

export const fetchHotspots = async (
  year: string = '2025',
  minCount: number = 15
): Promise<HotspotsResponse> => {
  const res = await apiClient.get<HotspotsResponse>('/hotspots', {
    params: { year, min_count: minCount, limit: 400 }
  });
  return res.data;
};

export const fetchSeverityAnalysis = async (
  year: string = '2025',
  field: string = 'weather_conditions'
): Promise<SeverityResponse> => {
  const res = await apiClient.get<SeverityResponse>('/severity-analysis', {
    params: { year, field }
  });
  return res.data;
};

export const fetchCombinatorialRisk = async (
  year: string = '2025',
  minCount: number = 25
): Promise<CombinationsResponse> => {
  const res = await apiClient.get<CombinationsResponse>('/severity/combinations', {
    params: { year, min_count: minCount }
  });
  return res.data;
};

export const compareScenarios = async (
  scenarioA: ScenarioParams,
  scenarioB: ScenarioParams
): Promise<ScenarioComparisonResponse> => {
  const res = await apiClient.post<ScenarioComparisonResponse>('/severity/compare', {
    scenario_a: scenarioA,
    scenario_b: scenarioB
  });
  return res.data;
};

export const fetchIndexBenchmarks = async (): Promise<BenchmarksResponse> => {
  const res = await apiClient.get<BenchmarksResponse>('/data-quality/benchmarks');
  return res.data;
};

export const fetchCollisionRecords = async (
  year: string = '2025',
  page: number = 1,
  pageSize: number = 25,
  search?: string,
  severity?: string
): Promise<CollisionRecordsResponse> => {
  const res = await apiClient.get<CollisionRecordsResponse>('/collisions', {
    params: { year, page, page_size: pageSize, search, severity }
  });
  return res.data;
};

export const fetchCollisionDetail = async (collisionIndex: string): Promise<CollisionDetail> => {
  const res = await apiClient.get<CollisionDetail>(`/collisions/${collisionIndex}`);
  return res.data;
};

export const fetchDataQuality = async (): Promise<DataQualityReport> => {
  const res = await apiClient.get<DataQualityReport>('/data-quality');
  return res.data;
};

export const checkHealth = async (): Promise<any> => {
  const res = await apiClient.get('/health');
  return res.data;
};
