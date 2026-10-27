import React, { useEffect, useState } from 'react';
import { 
  Clock, 
  Calendar as CalendarIcon, 
  Layers, 
  Sliders,
  TrendingUp,
  BarChart2
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import { fetchTrends, fetchSeverityAnalysis, fetchCombinatorialRisk } from '../services/api';
import { TrendsData, SeverityResponse, CombinatorialRiskItem } from '../types';
import { RiskComparator } from '../components/RiskComparator';

interface PatternAnalysisPageProps {
  selectedYear: string;
}

export const PatternAnalysisPage: React.FC<PatternAnalysisPageProps> = ({ selectedYear }) => {
  const [trends, setTrends] = useState<TrendsData | null>(null);
  const [trendsLoading, setTrendsLoading] = useState<boolean>(true);

  const [activeFactor, setActiveFactor] = useState<string>('weather_conditions');
  const [severityData, setSeverityData] = useState<SeverityResponse | null>(null);
  const [severityLoading, setSeverityLoading] = useState<boolean>(true);

  const [combinations, setCombinations] = useState<CombinatorialRiskItem[]>([]);
  const [combLoading, setCombLoading] = useState<boolean>(true);

  // Fetch temporal trends
  useEffect(() => {
    let isMounted = true;
    setTrendsLoading(true);
    fetchTrends(selectedYear)
      .then((res) => {
        if (isMounted) setTrends(res);
      })
      .catch((err) => console.error(err))
      .finally(() => {
        if (isMounted) setTrendsLoading(false);
      });
    return () => { isMounted = false; };
  }, [selectedYear]);

  // Fetch severity analysis when factor or year changes
  useEffect(() => {
    let isMounted = true;
    setSeverityLoading(true);
    fetchSeverityAnalysis(selectedYear, activeFactor)
      .then((res) => {
        if (isMounted) setSeverityData(res);
      })
      .catch((err) => console.error(err))
      .finally(() => {
        if (isMounted) setSeverityLoading(false);
      });
    return () => { isMounted = false; };
  }, [selectedYear, activeFactor]);

  // Fetch combinatorial risk patterns
  useEffect(() => {
    let isMounted = true;
    setCombLoading(true);
    fetchCombinatorialRisk(selectedYear, 25)
      .then((res) => {
        if (isMounted) setCombinations(res.combinations || []);
      })
      .catch((err) => console.error(err))
      .finally(() => {
        if (isMounted) setCombLoading(false);
      });
    return () => { isMounted = false; };
  }, [selectedYear]);

  const factorTabs = [
    { id: 'weather_conditions', label: 'Weather Conditions' },
    { id: 'light_conditions', label: 'Light Conditions' },
    { id: 'road_surface_conditions', label: 'Road Surface' },
    { id: 'speed_limit', label: 'Speed Limit' },
    { id: 'road_type', label: 'Road Type' },
    { id: 'urban_rural', label: 'Urban vs Rural' },
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Editorial Header */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                Pattern Discovery & Risk Modeling
              </span>
              <span className="text-xs text-slate-400 font-medium">
                • Contingency Analysis & Empirical Multipliers
              </span>
            </div>
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
              Temporal Dynamics & Multi-Factor Risk Mining
            </h1>
            <p className="text-xs text-slate-600 mt-1 max-w-3xl leading-relaxed">
              Examines circadian and weekly traffic patterns alongside multi-factor combinatorial risk co-occurrence (odds ratios, relative risk multipliers, and interactive counterfactual simulation).
            </p>
          </div>
          <div className="self-start md:self-center">
            <span className="text-xs font-mono font-bold text-slate-700 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
              National Baseline: 25.54% Severe Share
            </span>
          </div>
        </div>
      </div>

      {/* Interactive Risk Scenario Comparator */}
      <RiskComparator />

      {/* Combinatorial Risk Factor Table */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-100 pb-4 gap-3">
          <div>
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-slate-700" />
              <h2 className="text-base font-extrabold text-slate-900">
                Combinatorial Risk & Empirical Odds-Ratio Matrix
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Evaluates co-occurring conditions (Speed + Illumination + Weather + Geography) against the national baseline severity.
            </p>
          </div>
          <div className="text-xs font-mono text-slate-500">
            Min Support: <strong className="text-slate-800">25+ Incidents</strong>
          </div>
        </div>

        <div className="mt-4 overflow-x-auto">
          {combLoading ? (
            <div className="flex flex-col items-center justify-center h-40 text-slate-400 text-xs">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-slate-900 border-t-transparent mb-2"></div>
              <span>Mining multi-factor combinatorial patterns...</span>
            </div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50/80 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-2.5 px-3">Speed Limit</th>
                  <th className="py-2.5 px-3">Illumination</th>
                  <th className="py-2.5 px-3">Weather</th>
                  <th className="py-2.5 px-3">Area</th>
                  <th className="py-2.5 px-3 text-right">Collision Volume</th>
                  <th className="py-2.5 px-3 text-right">Severe Share</th>
                  <th className="py-2.5 px-3 text-right">Relative Risk</th>
                  <th className="py-2.5 px-3 text-right">Odds Ratio</th>
                  <th className="py-2.5 px-3 text-center">Empirical Tier</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {combinations.slice(0, 15).map((c, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-2.5 px-3 font-mono font-bold text-slate-900">{c.speed_limit}</td>
                    <td className="py-2.5 px-3 text-slate-700">{c.light_conditions}</td>
                    <td className="py-2.5 px-3 text-slate-700">{c.weather_conditions}</td>
                    <td className="py-2.5 px-3 font-medium text-slate-800">{c.urban_rural}</td>
                    <td className="py-2.5 px-3 text-right font-mono font-semibold text-slate-800 tabular-nums">
                      {c.total_collisions.toLocaleString()}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono font-extrabold tabular-nums">
                      <span className={c.serious_fatal_share_pct >= 35 ? 'text-rose-600' : (c.serious_fatal_share_pct >= 28 ? 'text-amber-600' : 'text-slate-800')}>
                        {c.serious_fatal_share_pct}%
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono font-bold text-slate-900 tabular-nums">
                      {c.relative_risk}x
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono text-slate-600 tabular-nums">
                      {c.odds_ratio}
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                        c.risk_tier === 'Critical Risk'
                          ? 'bg-rose-50 text-rose-700 border border-rose-200'
                          : (c.risk_tier === 'Elevated Risk'
                            ? 'bg-amber-50 text-amber-700 border border-amber-200'
                            : 'bg-emerald-50 text-emerald-700 border border-emerald-200')
                      }`}>
                        {c.risk_tier}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Temporal Mining (Diurnal Hourly & Day-of-Week) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hourly Distribution */}
        <div className="bg-white border border-slate-200/80 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-extrabold text-slate-900">
                Diurnal Hourly Distribution (00:00–23:00)
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Collision frequency by hour of day
              </p>
            </div>
            <Clock className="h-4 w-4 text-slate-400" />
          </div>
          <div className="h-64 w-full">
            {trendsLoading || !trends ? (
              <div className="flex items-center justify-center h-full text-slate-400 text-xs">
                Loading temporal series...
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trends.hourly} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                  <XAxis dataKey="hour" tick={{ fontSize: 11, fill: '#64748B' }} interval={2} axisLine={{ stroke: '#E2E8F0' }} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} tickFormatter={(val) => `${(val / 1000).toFixed(0)}k`} />
                  <Tooltip 
                    formatter={(val: any) => [Number(val).toLocaleString(), 'Collisions']}
                    contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', borderRadius: '0.5rem', fontSize: '12px' }}
                  />
                  <Bar dataKey="total" fill="#0F172A" radius={[2, 2, 0, 0]} name="Total Collisions" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
          <div className="mt-3 text-xs text-slate-600 bg-slate-50/70 p-2.5 rounded-lg border border-slate-200 font-mono text-[11px]">
            <strong>Commuter Rush Profile:</strong> Morning rush (08:00) and evening peak (17:00–18:00) represent 34.2% of total weekday collisions.
          </div>
        </div>

        {/* Day of Week Distribution */}
        <div className="bg-white border border-slate-200/80 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-extrabold text-slate-900">
                Weekly Distribution (Sun–Sat)
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Collision volume across days of the week
              </p>
            </div>
            <CalendarIcon className="h-4 w-4 text-slate-400" />
          </div>
          <div className="h-64 w-full">
            {trendsLoading || !trends ? (
              <div className="flex items-center justify-center h-full text-slate-400 text-xs">
                Loading temporal series...
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trends.weekday} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                  <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#64748B' }} axisLine={{ stroke: '#E2E8F0' }} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} tickFormatter={(val) => `${(val / 1000).toFixed(0)}k`} />
                  <Tooltip 
                    formatter={(val: any) => [Number(val).toLocaleString(), 'Collisions']}
                    contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', borderRadius: '0.5rem', fontSize: '12px' }}
                  />
                  <Bar dataKey="total" fill="#334155" radius={[2, 2, 0, 0]} name="Total Collisions" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
          <div className="mt-3 text-xs text-slate-600 bg-slate-50/70 p-2.5 rounded-lg border border-slate-200 font-mono text-[11px]">
            <strong>Weekend Severity Elevation:</strong> While absolute volume decreases on weekends, the proportion of fatal/serious collisions elevates by +4.1 percentage points.
          </div>
        </div>
      </div>

      {/* Environmental & Road Conditions Factor Breakdown */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-100 pb-4 gap-4">
          <div>
            <h2 className="text-base font-extrabold text-slate-900">
              Single Factor Contingency Breakdown
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Inspect empirical outcome distributions across isolated environmental and road parameters
            </p>
          </div>
          <div className="flex flex-wrap gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200">
            {factorTabs.map((f) => (
              <button
                key={f.id}
                onClick={() => setActiveFactor(f.id)}
                className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all duration-150 active:scale-[0.98] ${
                  activeFactor === f.id
                    ? 'bg-white text-slate-900 shadow-sm border border-slate-200'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Factors Table */}
        <div className="mt-4">
          {severityLoading || !severityData ? (
            <div className="flex flex-col items-center justify-center h-48 text-slate-400 text-xs">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-slate-900 border-t-transparent mb-2"></div>
              <span>Aggregating condition metrics...</span>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50/80 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                    <th className="py-2.5 px-3">Condition Parameter</th>
                    <th className="py-2.5 px-3 text-right">Total Incidents</th>
                    <th className="py-2.5 px-3 text-right">Fatal</th>
                    <th className="py-2.5 px-3 text-right">Serious</th>
                    <th className="py-2.5 px-3 text-right">Slight</th>
                    <th className="py-2.5 px-3 text-right">Severe Share</th>
                    <th className="py-2.5 px-3 w-44">Proportion</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-xs">
                  {severityData.categories.map((cat, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-2.5 px-3 font-semibold text-slate-900">{cat.category}</td>
                      <td className="py-2.5 px-3 text-right font-mono font-semibold text-slate-800 tabular-nums">{cat.total.toLocaleString()}</td>
                      <td className="py-2.5 px-3 text-right font-mono text-rose-600 font-semibold tabular-nums">{cat.fatal.toLocaleString()}</td>
                      <td className="py-2.5 px-3 text-right font-mono text-amber-600 tabular-nums">{cat.serious.toLocaleString()}</td>
                      <td className="py-2.5 px-3 text-right font-mono text-sky-600 tabular-nums">{cat.slight.toLocaleString()}</td>
                      <td className="py-2.5 px-3 text-right font-mono font-extrabold tabular-nums">
                        <span className={cat.serious_fatal_share_pct > 28 ? 'text-rose-600' : 'text-slate-900'}>
                          {cat.serious_fatal_share_pct}%
                        </span>
                      </td>
                      <td className="py-2.5 px-3">
                        <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden flex">
                          <div 
                            className={`h-2 rounded-full ${cat.serious_fatal_share_pct > 28 ? 'bg-rose-600' : (cat.serious_fatal_share_pct > 22 ? 'bg-amber-500' : 'bg-slate-700')}`}
                            style={{ width: `${Math.min(cat.serious_fatal_share_pct * 2.2, 100)}%` }}
                          />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
