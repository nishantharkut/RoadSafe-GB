import React from 'react';
import { 
  BarChart3, 
  MapPin, 
  Calendar, 
  Table2, 
  ShieldCheck, 
  Database,
  ArrowUpRight
} from 'lucide-react';

export type NavTab = 'overview' | 'geo' | 'patterns' | 'records' | 'methodology';

interface NavbarProps {
  currentTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  selectedYear: string;
  onYearChange: (year: string) => void;
  dbHealthy: boolean;
  totalRecordsCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onTabChange,
  selectedYear,
  onYearChange,
  dbHealthy,
  totalRecordsCount
}) => {
  const tabs = [
    { id: 'overview' as NavTab, label: 'Overview', icon: BarChart3 },
    { id: 'geo' as NavTab, label: 'Spatial Concentrations', icon: MapPin },
    { id: 'patterns' as NavTab, label: 'Risk Patterns & Scenarios', icon: Calendar },
    { id: 'records' as NavTab, label: 'Record Explorer', icon: Table2 },
    { id: 'methodology' as NavTab, label: 'Governance & Benchmarks', icon: Database },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.02)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & Context */}
          <div 
            className="flex items-center gap-3 cursor-pointer select-none group" 
            onClick={() => onTabChange('overview')}
          >
            <div className="h-9 w-9 rounded-lg bg-slate-900 flex items-center justify-center text-white shadow-sm transition-transform duration-150 group-hover:scale-105">
              <ShieldCheck className="h-5 w-5 text-slate-100" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-extrabold tracking-tight text-slate-900">
                  RoadSafe<span className="text-slate-500 font-normal ml-0.5">GB</span>
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 tracking-wider uppercase border border-slate-200">
                  STATS19 Census
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium hidden md:block tracking-tight">
                Department for Transport Road Casualty Mining Platform
              </p>
            </div>
          </div>

          {/* Controls: Year Filter + Live Database Indicator */}
          <div className="flex items-center gap-3">
            {/* Year Selector Segmented Control */}
            <div className="flex items-center bg-slate-100/90 p-0.5 rounded-lg border border-slate-200/70 text-xs">
              {(['2025', '2024', 'all'] as const).map((yr) => {
                const isActive = selectedYear === yr;
                return (
                  <button
                    key={yr}
                    onClick={() => onYearChange(yr)}
                    className={`px-3 py-1 rounded-md font-semibold transition-all duration-150 active:scale-95 ${
                      isActive
                        ? 'bg-white text-slate-900 shadow-sm border border-slate-200/80'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    {yr === 'all' ? '2024–2025' : yr}
                  </button>
                );
              })}
            </div>

            {/* Live Database Pill */}
            <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-50 border border-slate-200/80 text-[11px] font-medium text-slate-700">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="font-mono tabular-nums text-slate-900 font-semibold">
                {totalRecordsCount > 0 ? totalRecordsCount.toLocaleString() : '514,283'}
              </span>
              <span className="text-slate-400">docs</span>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 border-t border-slate-100 pt-1 -mb-px overflow-x-auto no-scrollbar">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = currentTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`flex items-center gap-2 py-2.5 px-3.5 border-b-2 text-xs font-semibold whitespace-nowrap transition-all duration-150 ${
                  isActive
                    ? 'border-slate-900 text-slate-900 bg-slate-50/80'
                    : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? 'text-slate-900' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
