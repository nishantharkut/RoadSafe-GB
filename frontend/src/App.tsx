import React, { useState, useEffect } from 'react';
import { Navbar, NavTab } from './components/Navbar';
import { OverviewPage } from './pages/OverviewPage';
import { GeoExplorerPage } from './pages/GeoExplorerPage';
import { PatternAnalysisPage } from './pages/PatternAnalysisPage';
import { RecordsPage } from './pages/RecordsPage';
import { MethodologyPage } from './pages/MethodologyPage';
import { checkHealth } from './services/api';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavTab>('overview');
  const [selectedYear, setSelectedYear] = useState<string>('2025');
  const [dbHealthy, setDbHealthy] = useState<boolean>(true);
  const [totalRecordsCount, setTotalRecordsCount] = useState<number>(202452);

  useEffect(() => {
    checkHealth()
      .then((res) => {
        setDbHealthy(res.database_connected === true);
        if (res.collections && res.collections.collisions) {
          setTotalRecordsCount(res.collections.collisions);
        }
      })
      .catch(() => {
        setDbHealthy(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col font-sans">
      <Navbar
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        selectedYear={selectedYear}
        onYearChange={setSelectedYear}
        dbHealthy={dbHealthy}
        totalRecordsCount={totalRecordsCount}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        {currentTab === 'overview' && <OverviewPage selectedYear={selectedYear} />}
        {currentTab === 'geo' && <GeoExplorerPage selectedYear={selectedYear} />}
        {currentTab === 'patterns' && <PatternAnalysisPage selectedYear={selectedYear} />}
        {currentTab === 'records' && <RecordsPage selectedYear={selectedYear} />}
        {currentTab === 'methodology' && <MethodologyPage />}
      </main>

      <footer className="bg-white border-t border-slate-200 py-6 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <div>
            <strong>RoadSafe GB</strong> — Spatial and Temporal Mining of Road Accident Patterns in Great Britain
          </div>
          <div>
            Data: UK Department for Transport (STATS19) • Open Government Licence v3.0
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
