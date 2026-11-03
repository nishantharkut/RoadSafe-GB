import React, { useState, useEffect } from 'react';
import { 
  Sliders, 
  ArrowRight, 
  AlertTriangle, 
  ShieldCheck, 
  Gauge, 
  Users, 
  Sparkles,
  Layers
} from 'lucide-react';
import { compareScenarios } from '../services/api';
import { ScenarioParams, ScenarioComparisonResponse } from '../types';

export const RiskComparator: React.FC = () => {
  const [scenarioA, setScenarioA] = useState<ScenarioParams>({
    speed_limit: 30,
    light_conditions: 'Daylight',
    weather_conditions: 'Fine no high winds',
    urban_rural: 'Urban'
  });

  const [scenarioB, setScenarioB] = useState<ScenarioParams>({
    speed_limit: 60,
    light_conditions: 'Darkness - no lighting',
    weather_conditions: 'Raining no high winds',
    urban_rural: 'Rural'
  });

  const [comparison, setComparison] = useState<ScenarioComparisonResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const runComparison = async () => {
    setLoading(true);
    try {
      const data = await compareScenarios(scenarioA, scenarioB);
      setComparison(data);
    } catch (err) {
      console.error('Failed to run scenario comparison:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runComparison();
  }, [scenarioA, scenarioB]);

  const loadPreset = (presetNumber: number) => {
    if (presetNumber === 1) {
      setScenarioA({
        speed_limit: 30,
        light_conditions: 'Daylight',
        weather_conditions: 'Fine no high winds',
        urban_rural: 'Urban'
      });
      setScenarioB({
        speed_limit: 60,
        light_conditions: 'Darkness - no lighting',
        weather_conditions: 'Raining no high winds',
        urban_rural: 'Rural'
      });
    } else if (presetNumber === 2) {
      setScenarioA({
        speed_limit: 20,
        light_conditions: 'Daylight',
        weather_conditions: 'Fine no high winds',
        urban_rural: 'Urban'
      });
      setScenarioB({
        speed_limit: 30,
        light_conditions: 'Daylight',
        weather_conditions: 'Fine no high winds',
        urban_rural: 'Urban'
      });
    } else if (presetNumber === 3) {
      setScenarioA({
        speed_limit: 50,
        light_conditions: 'Daylight',
        weather_conditions: 'Fine no high winds',
        urban_rural: 'Rural'
      });
      setScenarioB({
        speed_limit: 50,
        light_conditions: 'Darkness - lights unlit',
        weather_conditions: 'Fog or mist',
        urban_rural: 'Rural'
      });
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm p-6 mb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-slate-700" />
            <h3 className="text-base font-bold text-slate-900 tracking-tight">
              Interactive Risk Differential Engine
            </h3>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200 uppercase tracking-wider">
              Simulation Model
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Simulate and contrast empirical outcome probabilities across differing environmental and road classifications.
          </p>
        </div>

        {/* Quick Presets */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-xs font-semibold text-slate-400 mr-1 text-[11px] uppercase tracking-wider">Presets:</span>
          <button
            onClick={() => loadPreset(1)}
            className="text-xs px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold transition active:scale-95 border border-slate-200/60"
          >
            Urban 30 vs Rural 60 Dark
          </button>
          <button
            onClick={() => loadPreset(2)}
            className="text-xs px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold transition active:scale-95 border border-slate-200/60"
          >
            20mph vs 30mph Zone
          </button>
          <button
            onClick={() => loadPreset(3)}
            className="text-xs px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold transition active:scale-95 border border-slate-200/60"
          >
            Daylight vs Fog 50mph
          </button>
        </div>
      </div>

      {/* Selectors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        {/* Scenario A Card */}
        <div className="bg-slate-50/60 p-5 rounded-lg border border-slate-200/80">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[11px] font-bold uppercase tracking-wider text-teal-800 bg-teal-50 px-2 py-0.5 rounded border border-teal-200">
              Scenario A (Baseline)
            </span>
            <ShieldCheck className="w-4 h-4 text-teal-600" />
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label className="block text-[11px] font-medium text-slate-600 mb-1">Speed Limit</label>
              <select
                value={scenarioA.speed_limit}
                onChange={(e) => setScenarioA({ ...scenarioA, speed_limit: Number(e.target.value) })}
                className="w-full bg-white border border-slate-300 rounded px-2.5 py-1.5 text-xs text-slate-900 font-medium focus:ring-1 focus:ring-slate-400 focus:outline-none"
              >
                <option value={20}>20 mph</option>
                <option value={30}>30 mph</option>
                <option value={40}>40 mph</option>
                <option value={50}>50 mph</option>
                <option value={60}>60 mph</option>
                <option value={70}>70 mph</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-medium text-slate-600 mb-1">Environment</label>
              <select
                value={scenarioA.urban_rural}
                onChange={(e) => setScenarioA({ ...scenarioA, urban_rural: e.target.value })}
                className="w-full bg-white border border-slate-300 rounded px-2.5 py-1.5 text-xs text-slate-900 font-medium focus:ring-1 focus:ring-slate-400 focus:outline-none"
              >
                <option value="Urban">Urban</option>
                <option value="Rural">Rural</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-medium text-slate-600 mb-1">Light Conditions</label>
              <select
                value={scenarioA.light_conditions}
                onChange={(e) => setScenarioA({ ...scenarioA, light_conditions: e.target.value })}
                className="w-full bg-white border border-slate-300 rounded px-2.5 py-1.5 text-xs text-slate-900 font-medium focus:ring-1 focus:ring-slate-400 focus:outline-none"
              >
                <option value="Daylight">Daylight</option>
                <option value="Darkness - lights lit">Darkness - lights lit</option>
                <option value="Darkness - no lighting">Darkness - no lighting</option>
                <option value="Darkness - lights unlit">Darkness - lights unlit</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-medium text-slate-600 mb-1">Weather Conditions</label>
              <select
                value={scenarioA.weather_conditions}
                onChange={(e) => setScenarioA({ ...scenarioA, weather_conditions: e.target.value })}
                className="w-full bg-white border border-slate-300 rounded px-2.5 py-1.5 text-xs text-slate-900 font-medium focus:ring-1 focus:ring-slate-400 focus:outline-none"
              >
                <option value="Fine no high winds">Fine no high winds</option>
                <option value="Raining no high winds">Raining no high winds</option>
                <option value="Snowing no high winds">Snowing no high winds</option>
                <option value="Fog or mist">Fog or mist</option>
                <option value="Fine + high winds">Fine + high winds</option>
                <option value="Raining + high winds">Raining + high winds</option>
              </select>
            </div>
          </div>
        </div>

        {/* Scenario B Card */}
        <div className="bg-slate-50/60 p-5 rounded-lg border border-slate-200/80">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[11px] font-bold uppercase tracking-wider text-rose-800 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
              Scenario B (Test Profile)
            </span>
            <AlertTriangle className="w-4 h-4 text-rose-600" />
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label className="block text-[11px] font-medium text-slate-600 mb-1">Speed Limit</label>
              <select
                value={scenarioB.speed_limit}
                onChange={(e) => setScenarioB({ ...scenarioB, speed_limit: Number(e.target.value) })}
                className="w-full bg-white border border-slate-300 rounded px-2.5 py-1.5 text-xs text-slate-900 font-medium focus:ring-1 focus:ring-slate-400 focus:outline-none"
              >
                <option value={20}>20 mph</option>
                <option value={30}>30 mph</option>
                <option value={40}>40 mph</option>
                <option value={50}>50 mph</option>
                <option value={60}>60 mph</option>
                <option value={70}>70 mph</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-medium text-slate-600 mb-1">Environment</label>
              <select
                value={scenarioB.urban_rural}
                onChange={(e) => setScenarioB({ ...scenarioB, urban_rural: e.target.value })}
                className="w-full bg-white border border-slate-300 rounded px-2.5 py-1.5 text-xs text-slate-900 font-medium focus:ring-1 focus:ring-slate-400 focus:outline-none"
              >
                <option value="Urban">Urban</option>
                <option value="Rural">Rural</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-medium text-slate-600 mb-1">Light Conditions</label>
              <select
                value={scenarioB.light_conditions}
                onChange={(e) => setScenarioB({ ...scenarioB, light_conditions: e.target.value })}
                className="w-full bg-white border border-slate-300 rounded px-2.5 py-1.5 text-xs text-slate-900 font-medium focus:ring-1 focus:ring-slate-400 focus:outline-none"
              >
                <option value="Daylight">Daylight</option>
                <option value="Darkness - lights lit">Darkness - lights lit</option>
                <option value="Darkness - no lighting">Darkness - no lighting</option>
                <option value="Darkness - lights unlit">Darkness - lights unlit</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-medium text-slate-600 mb-1">Weather Conditions</label>
              <select
                value={scenarioB.weather_conditions}
                onChange={(e) => setScenarioB({ ...scenarioB, weather_conditions: e.target.value })}
                className="w-full bg-white border border-slate-300 rounded px-2.5 py-1.5 text-xs text-slate-900 font-medium focus:ring-1 focus:ring-slate-400 focus:outline-none"
              >
                <option value="Fine no high winds">Fine no high winds</option>
                <option value="Raining no high winds">Raining no high winds</option>
                <option value="Snowing no high winds">Snowing no high winds</option>
                <option value="Fog or mist">Fog or mist</option>
                <option value="Fine + high winds">Fine + high winds</option>
                <option value="Raining + high winds">Raining + high winds</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Comparison Results */}
      {comparison && (
        <div className="mt-6 pt-6 border-t border-slate-100">
          {/* Main Risk Multiplier Banner */}
          <div className="flex flex-col sm:flex-row items-center justify-between p-4 bg-slate-900 text-white rounded-xl mb-6 gap-3 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-lg bg-white/10 text-white flex items-center justify-center font-mono font-bold text-xl tabular-nums border border-white/20">
                {comparison.comparison.risk_multiplier}x
              </div>
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Empirical Relative Risk Multiplier
                </span>
                <p className="text-xs font-medium text-slate-200 mt-0.5">
                  Collisions under <strong>{comparison.comparison.higher_risk_scenario}</strong> carry a{' '}
                  <span className="text-emerald-400 font-bold">
                    {comparison.comparison.risk_multiplier}× higher likelihood
                  </span>{' '}
                  of severe casualty ({comparison.comparison.severe_share_diff_pct > 0 ? `+${comparison.comparison.severe_share_diff_pct}%` : `${comparison.comparison.severe_share_diff_pct}%`}).
                </p>
              </div>
            </div>

            <div className="text-[11px] text-slate-400 text-right font-mono">
              Confidence Base: {((comparison.scenario_a?.total_collisions ?? 0) + (comparison.scenario_b?.total_collisions ?? 0)).toLocaleString()} incidents
            </div>
          </div>

          {/* Side-by-Side Detailed Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Scenario A Metrics */}
            <div className="border border-slate-200/80 rounded-lg p-4 bg-white">
              <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2">
                Scenario A Empirical Outcomes
              </div>
              <div className="text-2xl font-bold font-mono text-slate-900 tabular-nums mb-1">
                {comparison.scenario_a.serious_fatal_share_pct}%
                <span className="text-xs font-normal text-slate-500 ml-1.5 font-sans">Severe Share</span>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-slate-100 rounded-full h-1.5 mb-4">
                <div 
                  className="bg-teal-600 h-1.5 rounded-full transition-all duration-500" 
                  style={{ width: `${Math.min(100, comparison.scenario_a.serious_fatal_share_pct)}%` }}
                />
              </div>

              <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono border-t border-slate-100 pt-3">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-sans">Fatal</span>
                  <span className="font-bold text-slate-900 tabular-nums">{comparison.scenario_a.fatal_count}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-sans">Serious</span>
                  <span className="font-bold text-slate-900 tabular-nums">{comparison.scenario_a.serious_count}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-sans">Sample Size</span>
                  <span className="font-bold text-slate-900 tabular-nums">{(comparison.scenario_a?.total_collisions ?? 0).toLocaleString()}</span>
                </div>
              </div>
            </div>

            {/* Scenario B Metrics */}
            <div className="border border-slate-200/80 rounded-lg p-4 bg-white">
              <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2">
                Scenario B Empirical Outcomes
              </div>
              <div className="text-2xl font-bold font-mono text-slate-900 tabular-nums mb-1">
                {comparison.scenario_b.serious_fatal_share_pct}%
                <span className="text-xs font-normal text-slate-500 ml-1.5 font-sans">Severe Share</span>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-slate-100 rounded-full h-1.5 mb-4">
                <div 
                  className="bg-rose-600 h-1.5 rounded-full transition-all duration-500" 
                  style={{ width: `${Math.min(100, comparison.scenario_b.serious_fatal_share_pct)}%` }}
                />
              </div>

              <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono border-t border-slate-100 pt-3">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-sans">Fatal</span>
                  <span className="font-bold text-slate-900 tabular-nums">{comparison.scenario_b.fatal_count}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-sans">Serious</span>
                  <span className="font-bold text-slate-900 tabular-nums">{comparison.scenario_b.serious_count}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-sans">Sample Size</span>
                  <span className="font-bold text-slate-900 tabular-nums">{(comparison.scenario_b?.total_collisions ?? 0).toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
