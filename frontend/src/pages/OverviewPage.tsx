import React, { useEffect, useState } from 'react';
import { 
  AlertTriangle, 
  Users, 
  Car, 
  TrendingUp, 
  ShieldAlert, 
  Calendar,
  Layers,
  ArrowUpRight
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';
import { fetchOverview } from '../services/api';
import { OverviewData } from '../types';

interface OverviewPageProps {
  selectedYear: string;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ selectedYear }) => {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    fetchOverview(selectedYear)
      .then((res) => {
        if (isMounted) {
          setData(res);
          setError(null);
        }
      })
      .catch((err) => {
        if (isMounted) setError(err.message || 'Failed to load overview data');
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });
    return () => { isMounted = false; };
  }, [selectedYear]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-7 w-7 border-2 border-slate-900 border-t-transparent mb-3"></div>
          <p className="text-xs font-semibold text-slate-600 tracking-wide uppercase">Executing Aggregation Pipeline...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 my-6 text-rose-800 text-sm">
        <h3 className="font-bold">Error Loading Overview</h3>
        <p className="mt-1">{error}</p>
      </div>
    );
  }

  const fatalSeriousCount = data.fatal_count + data.serious_count;

  return (
    <div className="space-y-6 pb-12">
      {/* Editorial Header Section */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                UK DfT STATS19 Census
              </span>
              <span className="text-xs text-slate-400 font-medium">
                • {selectedYear === 'all' ? '2024–2025 Multi-Year Census' : `${selectedYear} Calendar Period`}
              </span>
            </div>
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
              National Road Safety & Incident Mining Overview
            </h1>
            <p className="text-xs text-slate-600 mt-1 max-w-3xl leading-relaxed">
              Synthesized from official police-reported personal injury collisions across England, Scotland, and Wales. 
              All indicators are calculated directly via high-throughput MongoDB aggregation pipelines.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start md:self-auto">
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 border border-slate-200 text-xs font-semibold text-slate-800">
              <Layers className="w-3.5 h-3.5 text-slate-600" />
              <span>Full National Granularity</span>
            </span>
          </div>
        </div>
      </div>

      {/* Unified Institutional Metric Ribbon (Anti-Card Overuse) */}
      <div className="bg-white border border-slate-200/80 rounded-xl shadow-sm overflow-hidden">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 divide-y sm:divide-y-0 sm:divide-x divide-slate-200/70">
          {/* Metric 1 */}
          <div className="p-5 hover:bg-slate-50/50 transition-colors">
            <div className="flex items-center justify-between text-xs text-slate-500 font-semibold tracking-wider uppercase mb-1">
              <span>Recorded Collisions</span>
              <TrendingUp className="w-4 h-4 text-slate-400" />
            </div>
            <div className="text-3xl font-extrabold text-slate-900 font-mono tabular-nums tracking-tight">
              {data.total_collisions.toLocaleString()}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Personal injury incidents reported
            </p>
          </div>

          {/* Metric 2 */}
          <div className="p-5 hover:bg-slate-50/50 transition-colors">
            <div className="flex items-center justify-between text-xs text-slate-500 font-semibold tracking-wider uppercase mb-1">
              <span>Severe Outcome Share</span>
              <AlertTriangle className="w-4 h-4 text-amber-500" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-slate-900 font-mono tabular-nums tracking-tight">
                {data.serious_fatal_share_pct}%
              </span>
              <span className="text-xs font-bold text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                Fatal + Serious
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              {fatalSeriousCount.toLocaleString()} high-severity collisions
            </p>
          </div>

          {/* Metric 3 */}
          <div className="p-5 hover:bg-slate-50/50 transition-colors">
            <div className="flex items-center justify-between text-xs text-slate-500 font-semibold tracking-wider uppercase mb-1">
              <span>Recorded Casualties</span>
              <Users className="w-4 h-4 text-slate-400" />
            </div>
            <div className="text-3xl font-extrabold text-slate-900 font-mono tabular-nums tracking-tight">
              {data.total_casualties.toLocaleString()}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Average <span className="font-semibold text-slate-700">{data.avg_casualties_per_collision}</span> casualties / collision
            </p>
          </div>

          {/* Metric 4 */}
          <div className="p-5 hover:bg-slate-50/50 transition-colors">
            <div className="flex items-center justify-between text-xs text-slate-500 font-semibold tracking-wider uppercase mb-1">
              <span>Involved Vehicles</span>
              <Car className="w-4 h-4 text-slate-400" />
            </div>
            <div className="text-3xl font-extrabold text-slate-900 font-mono tabular-nums tracking-tight">
              {data.total_vehicles.toLocaleString()}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Average <span className="font-semibold text-slate-700">{(data.total_vehicles / data.total_collisions).toFixed(2)}</span> vehicles / incident
            </p>
          </div>
        </div>

        {/* Severity Composition Proportion Strip */}
        <div className="border-t border-slate-200/70 bg-slate-50/60 p-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <span className="font-bold text-slate-700 tracking-wide uppercase text-[11px]">
              National Severity Composition
            </span>
            <div className="flex items-center gap-4 text-xs font-mono tabular-nums">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-600"></span>
                <span className="text-slate-600">Fatal:</span>
                <strong className="text-slate-900">{data.fatal_count.toLocaleString()} ({((data.fatal_count / data.total_collisions) * 100).toFixed(2)}%)</strong>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                <span className="text-slate-600">Serious:</span>
                <strong className="text-slate-900">{data.serious_count.toLocaleString()} ({((data.serious_count / data.total_collisions) * 100).toFixed(2)}%)</strong>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-teal-600"></span>
                <span className="text-slate-600">Slight:</span>
                <strong className="text-slate-900">{data.slight_count.toLocaleString()} ({((data.slight_count / data.total_collisions) * 100).toFixed(2)}%)</strong>
              </span>
            </div>
          </div>

          {/* Integrated Multi-color Proportion Bar */}
          <div className="w-full bg-slate-200 rounded-full h-2 mt-2.5 overflow-hidden flex">
            <div 
              className="bg-rose-600 h-2 transition-all duration-500" 
              style={{ width: `${(data.fatal_count / data.total_collisions) * 100}%` }}
              title={`Fatal: ${data.fatal_count}`}
            />
            <div 
              className="bg-amber-500 h-2 transition-all duration-500" 
              style={{ width: `${(data.serious_count / data.total_collisions) * 100}%` }}
              title={`Serious: ${data.serious_count}`}
            />
            <div 
              className="bg-teal-600 h-2 transition-all duration-500" 
              style={{ width: `${(data.slight_count / data.total_collisions) * 100}%` }}
              title={`Slight: ${data.slight_count}`}
            />
          </div>
        </div>
      </div>

      {/* Asymmetric Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Monthly Trend Area Chart (2 Cols) */}
        <div className="lg:col-span-2 bg-white border border-slate-200/80 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">
                Monthly Incident Trajectory
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Observed longitudinal distribution across calendar months
              </p>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
              <Calendar className="h-3.5 w-3.5 text-slate-400" />
              <span>12-Month Distribution</span>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.monthly_trend} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="gradientCollision" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0F172A" stopOpacity={0.18} />
                    <stop offset="95%" stopColor="#0F172A" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                <XAxis 
                  dataKey="month" 
                  tick={{ fontSize: 11, fill: '#64748B' }} 
                  tickFormatter={(val) => val.slice(0, 3)}
                  axisLine={{ stroke: '#E2E8F0' }}
                  tickLine={false}
                />
                <YAxis 
                  tick={{ fontSize: 11, fill: '#64748B' }} 
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(val) => `${(val / 1000).toFixed(0)}k`}
                />
                <Tooltip 
                  formatter={(val: any) => [Number(val).toLocaleString(), 'Collisions']}
                  contentStyle={{ 
                    backgroundColor: '#FFFFFF', 
                    borderColor: '#E2E8F0', 
                    borderRadius: '0.5rem',
                    fontSize: '12px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="count" 
                  stroke="#0F172A" 
                  strokeWidth={2} 
                  fillOpacity={1} 
                  fill="url(#gradientCollision)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right: Severity Distribution Donut Chart */}
        <div className="bg-white border border-slate-200/80 rounded-xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 tracking-tight">
              Severity Hierarchy Breakdown
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Three-tier personal injury classification
            </p>
          </div>

          <div className="h-52 w-full my-auto flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.severity_composition}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="count"
                >
                  <Cell fill="#0D9488" />
                  <Cell fill="#EA580C" />
                  <Cell fill="#DC2626" />
                </Pie>
                <Tooltip 
                  formatter={(val: any) => [Number(val).toLocaleString(), 'Incidents']}
                  contentStyle={{ 
                    backgroundColor: '#FFFFFF', 
                    borderColor: '#E2E8F0', 
                    borderRadius: '0.5rem',
                    fontSize: '12px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Clean Legend */}
          <div className="space-y-1.5 text-xs border-t border-slate-100 pt-3">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-teal-600"></span>
                <span className="text-slate-600">Slight Injury</span>
              </span>
              <span className="font-mono font-bold text-slate-900">{data.slight_count.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                <span className="text-slate-600">Serious Injury</span>
              </span>
              <span className="font-mono font-bold text-slate-900">{data.serious_count.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-600"></span>
                <span className="text-slate-600">Fatal Outcome</span>
              </span>
              <span className="font-mono font-bold text-slate-900">{data.fatal_count.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
