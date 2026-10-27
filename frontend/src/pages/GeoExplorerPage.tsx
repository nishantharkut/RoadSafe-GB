import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { 
  MapPin, 
  Sliders, 
  Info, 
  ShieldAlert, 
  AlertTriangle, 
  Users, 
  Navigation,
  Compass,
  Maximize2
} from 'lucide-react';
import { fetchHotspots } from '../services/api';
import { Hotspot, HotspotsResponse } from '../types';

interface GeoExplorerPageProps {
  selectedYear: string;
}

interface MetroRegion {
  name: string;
  coords: [number, number];
  zoom: number;
}

const METRO_REGIONS: MetroRegion[] = [
  { name: 'National Overview', coords: [54.5, -2.5], zoom: 6 },
  { name: 'Greater London', coords: [51.5074, -0.1278], zoom: 10 },
  { name: 'West Midlands', coords: [52.4862, -1.8904], zoom: 10 },
  { name: 'Greater Manchester', coords: [53.4808, -2.2426], zoom: 10 },
  { name: 'West Yorkshire', coords: [53.8008, -1.5491], zoom: 10 },
  { name: 'Central Scotland', coords: [55.9533, -3.1883], zoom: 9 },
];

export const GeoExplorerPage: React.FC<GeoExplorerPageProps> = ({ selectedYear }) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);

  const [hotspotsData, setHotspotsData] = useState<HotspotsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [minCount, setMinCount] = useState<number>(25);
  const [selectedHotspot, setSelectedHotspot] = useState<Hotspot | null>(null);
  const [activeRegion, setActiveRegion] = useState<string>('National Overview');

  // Initialize Leaflet Map once
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [54.5, -2.5],
      zoom: 6,
      minZoom: 5,
      maxZoom: 15,
      zoomControl: false
    });

    // Custom positioned zoom control
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Clean, public OpenStreetMap tiles (100% free, no API key required)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | UK DfT STATS19',
      maxZoom: 19
    }).addTo(map);

    const markersLayer = L.layerGroup().addTo(map);
    markersLayerRef.current = markersLayer;
    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Fetch hotspots data when year or minCount changes
  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    fetchHotspots(selectedYear, minCount)
      .then((res) => {
        if (isMounted) {
          setHotspotsData(res);
          if (res.hotspots.length > 0 && !selectedHotspot) {
            setSelectedHotspot(res.hotspots[0]);
          }
        }
      })
      .catch((err) => console.error('Failed to load hotspots:', err))
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => { isMounted = false; };
  }, [selectedYear, minCount]);

  // Update map markers when hotspotsData changes
  useEffect(() => {
    if (!mapInstanceRef.current || !markersLayerRef.current || !hotspotsData) return;

    markersLayerRef.current.clearLayers();

    hotspotsData.hotspots.forEach((h) => {
      // Color strictly based on severe outcome share
      let fillColor = '#0284C7'; // Default Slight-dominated (<22%)
      let strokeColor = '#0369A1';
      if (h.serious_fatal_share_pct >= 30) {
        fillColor = '#E11D48'; // Critical Severe (>=30%)
        strokeColor = '#9F1239';
      } else if (h.serious_fatal_share_pct >= 22) {
        fillColor = '#F59E0B'; // Elevated Severe (22-30%)
        strokeColor = '#B45309';
      }

      // Radius scaled smoothly by collision volume
      const radius = Math.min(Math.max(Math.sqrt(h.count) * 2.3, 5.5), 24);

      const circle = L.circleMarker([h.latitude, h.longitude], {
        radius: radius,
        fillColor: fillColor,
        color: strokeColor,
        weight: 1.5,
        opacity: 0.9,
        fillOpacity: 0.72
      });

      circle.bindTooltip(
        `<div style="font-family: inherit; font-size: 11px; padding: 2px;">` +
        `<div style="font-weight: 700; color: #0F172A; margin-bottom: 2px;">Grid Cell: ${h.grid_id}</div>` +
        `<div>Incidents: <strong>${h.count.toLocaleString()}</strong></div>` +
        `<div>Severe Share: <strong style="color: ${h.serious_fatal_share_pct >= 30 ? '#E11D48' : '#B45309'}">${h.serious_fatal_share_pct}%</strong></div>` +
        `<div>Casualties: <strong>${h.total_casualties.toLocaleString()}</strong></div>` +
        `</div>`,
        { direction: 'top', className: 'leaflet-tooltip-clean' }
      );

      circle.on('click', () => {
        setSelectedHotspot(h);
      });

      circle.addTo(markersLayerRef.current!);
    });
  }, [hotspotsData]);

  const handleRegionFlyTo = (region: MetroRegion) => {
    setActiveRegion(region.name);
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo(region.coords, region.zoom, {
        duration: 1.2,
        easeLinearity: 0.25
      });
    }
  };

  const handleCenterOnHotspot = (h: Hotspot) => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([h.latitude, h.longitude], 12, {
        duration: 0.8
      });
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Title & Spatial Engine Header */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                Spatial Partitioning Engine
              </span>
              <span className="text-xs text-slate-400 font-medium">
                • WGS84 ~0.10° Lat × 0.10° Lon Grid (~11 km resolution)
              </span>
            </div>
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
              Spatial Density & Incident Cluster Cartography
            </h1>
            <p className="text-xs text-slate-600 mt-1 max-w-3xl leading-relaxed">
              Synthesizes geospatial incident density across Great Britain. Grid cell marker radius represents localized collision volume; color encodes empirical severe outcome share (fatal + serious injury proportion).
            </p>
          </div>

          {/* Incident Threshold Segmented Controller */}
          <div className="flex items-center gap-2 bg-slate-50 p-2 rounded-lg border border-slate-200 self-start lg:self-center">
            <Sliders className="h-3.5 w-3.5 text-slate-500 ml-1" />
            <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
              Min Threshold:
            </span>
            <div className="inline-flex rounded-md shadow-sm" role="group">
              {[15, 25, 50, 100].map((val) => (
                <button
                  key={val}
                  onClick={() => setMinCount(val)}
                  className={`px-3 py-1 text-xs font-mono font-bold transition-all duration-150 active:scale-[0.98] border ${
                    minCount === val
                      ? 'bg-slate-900 text-white border-slate-900 z-10 shadow-sm'
                      : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                  } ${val === 15 ? 'rounded-l-md' : ''} ${val === 100 ? 'rounded-r-md' : ''} -ml-px first:ml-0`}
                >
                  ≥{val}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Metropolitan Focus Quick-Jump Bar */}
      <div className="bg-white border border-slate-200/80 rounded-xl px-4 py-3 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 text-slate-600 font-medium">
          <Navigation className="w-3.5 h-3.5 text-slate-500" />
          <span className="font-bold text-[11px] uppercase tracking-wider text-slate-500">
            Metropolitan Focus:
          </span>
        </div>
        <div className="flex items-center gap-1.5 flex-wrap">
          {METRO_REGIONS.map((region) => (
            <button
              key={region.name}
              onClick={() => handleRegionFlyTo(region)}
              className={`px-3 py-1 rounded-md text-xs font-semibold transition-all duration-150 active:scale-[0.98] border ${
                activeRegion === region.name
                  ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                  : 'bg-slate-50 text-slate-700 border-slate-200/70 hover:bg-slate-100'
              }`}
            >
              {region.name}
            </button>
          ))}
        </div>
      </div>

      {/* Map and Hotspot Inspector Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Leaflet Map Container */}
        <div className="lg:col-span-2 bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm flex flex-col min-h-[620px]">
          {/* Map Top Bar */}
          <div className="flex items-center justify-between px-2 py-2 border-b border-slate-100 mb-2">
            <span className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
              <MapPin className="h-4 w-4 text-slate-900" />
              <span>Great Britain Territorial Distribution</span>
              <span className="font-mono text-xs text-slate-500 font-bold ml-1 tabular-nums">
                ({hotspotsData?.total_hotspots || 0} active clusters)
              </span>
            </span>

            {/* Severity Legend */}
            <div className="hidden sm:flex items-center gap-3 text-xs font-medium text-slate-600 font-mono">
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-rose-600"></span>
                <span>≥30% Severe</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-amber-500"></span>
                <span>22–30%</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-sky-600"></span>
                <span>&lt;22%</span>
              </span>
            </div>
          </div>

          <div 
            ref={mapContainerRef} 
            className="flex-1 w-full rounded-lg border border-slate-200 overflow-hidden relative shadow-inner" 
          />
        </div>

        {/* Selected Hotspot Inspector Panel */}
        <div className="bg-white border border-slate-200/80 rounded-xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Cluster Inspector
                </span>
                <h2 className="text-base font-extrabold text-slate-900">
                  Grid Cell Breakdown
                </h2>
              </div>
              <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-800 border border-slate-200">
                WGS84 Partition
              </span>
            </div>

            {selectedHotspot ? (
              <div className="mt-4 space-y-4">
                {/* Cell Centroid Header */}
                <div className="bg-slate-50/80 p-3.5 rounded-lg border border-slate-200/80">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                      Grid Index ID
                    </span>
                    <button
                      onClick={() => handleCenterOnHotspot(selectedHotspot)}
                      className="inline-flex items-center gap-1 text-[11px] text-blue-700 hover:text-blue-800 font-semibold"
                    >
                      <Compass className="w-3 h-3" />
                      <span>Focus on Map</span>
                    </button>
                  </div>
                  <div className="text-xl font-mono font-extrabold text-slate-900 mt-0.5 tracking-tight">
                    {selectedHotspot.grid_id}
                  </div>
                  <div className="text-xs font-mono text-slate-500 mt-1 tabular-nums">
                    Centroid: Lat {selectedHotspot.latitude.toFixed(4)}°N · Lon {selectedHotspot.longitude.toFixed(4)}°E
                  </div>
                </div>

                {/* Primary Metric Ribbon */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-50/80 border border-slate-200/80 rounded-lg p-3">
                    <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                      Total Collisions
                    </span>
                    <div className="text-2xl font-bold font-mono text-slate-900 tabular-nums mt-0.5">
                      {selectedHotspot.count.toLocaleString()}
                    </div>
                  </div>
                  <div className="bg-slate-50/80 border border-slate-200/80 rounded-lg p-3">
                    <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                      Severe Share
                    </span>
                    <div className="text-2xl font-bold font-mono tabular-nums mt-0.5 text-rose-600">
                      {selectedHotspot.serious_fatal_share_pct}%
                    </div>
                  </div>
                </div>

                {/* Severity Breakdown Bar */}
                <div className="space-y-2 pt-2 border-t border-slate-100">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-700 uppercase tracking-wider text-[11px]">
                    <span>Outcome Distribution</span>
                    <span className="font-mono text-slate-400 font-normal">
                      {(selectedHotspot.fatal_count + selectedHotspot.serious_count + selectedHotspot.slight_count).toLocaleString()} total
                    </span>
                  </div>

                  <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden flex">
                    <div 
                      className="bg-rose-600 h-2" 
                      style={{ width: `${(selectedHotspot.fatal_count / selectedHotspot.count) * 100}%` }}
                      title={`Fatal: ${selectedHotspot.fatal_count}`}
                    />
                    <div 
                      className="bg-amber-500 h-2" 
                      style={{ width: `${(selectedHotspot.serious_count / selectedHotspot.count) * 100}%` }}
                      title={`Serious: ${selectedHotspot.serious_count}`}
                    />
                    <div 
                      className="bg-sky-600 h-2" 
                      style={{ width: `${(selectedHotspot.slight_count / selectedHotspot.count) * 100}%` }}
                      title={`Slight: ${selectedHotspot.slight_count}`}
                    />
                  </div>

                  <div className="divide-y divide-slate-100 text-xs">
                    <div className="flex justify-between items-center py-2">
                      <span className="flex items-center gap-1.5 text-slate-600">
                        <span className="h-2 w-2 rounded-full bg-rose-600"></span>
                        <span>Fatal Collisions</span>
                      </span>
                      <span className="font-mono font-bold text-slate-900 tabular-nums">
                        {selectedHotspot.fatal_count} ({((selectedHotspot.fatal_count / selectedHotspot.count) * 100).toFixed(1)}%)
                      </span>
                    </div>

                    <div className="flex justify-between items-center py-2">
                      <span className="flex items-center gap-1.5 text-slate-600">
                        <span className="h-2 w-2 rounded-full bg-amber-500"></span>
                        <span>Serious Collisions</span>
                      </span>
                      <span className="font-mono font-bold text-slate-900 tabular-nums">
                        {selectedHotspot.serious_count} ({((selectedHotspot.serious_count / selectedHotspot.count) * 100).toFixed(1)}%)
                      </span>
                    </div>

                    <div className="flex justify-between items-center py-2">
                      <span className="flex items-center gap-1.5 text-slate-600">
                        <span className="h-2 w-2 rounded-full bg-sky-600"></span>
                        <span>Slight Collisions</span>
                      </span>
                      <span className="font-mono font-bold text-slate-900 tabular-nums">
                        {selectedHotspot.slight_count} ({((selectedHotspot.slight_count / selectedHotspot.count) * 100).toFixed(1)}%)
                      </span>
                    </div>

                    <div className="flex justify-between items-center py-2 pt-2.5">
                      <span className="flex items-center gap-1.5 text-slate-700 font-semibold">
                        <Users className="h-3.5 w-3.5 text-slate-500" />
                        <span>Total Casualties</span>
                      </span>
                      <span className="font-mono font-bold text-slate-900 tabular-nums">
                        {selectedHotspot.total_casualties.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-16 text-center text-slate-400 text-xs">
                Select any grid marker on the map to inspect localized cluster metrics.
              </div>
            )}
          </div>

          <div className="mt-6 pt-3 border-t border-slate-100 bg-slate-50/70 rounded-lg p-3 text-[11px] text-slate-600 border border-slate-200/80 leading-relaxed">
            <strong className="text-slate-800">Spatial Normalization Note:</strong> High collision volumes in dense metropolitan centroids (e.g. Inner London, West Midlands conurbation) reflect vehicle movement exposure, whereas high severe share (% fatal/serious) frequently clusters along rural arterials and higher-speed corridors.
          </div>
        </div>
      </div>
    </div>
  );
};
