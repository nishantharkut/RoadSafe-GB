import React, { useEffect, useState } from 'react';
import { 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  X, 
  ExternalLink, 
  Car, 
  Users, 
  AlertTriangle,
  MapPin,
  Clock,
  Calendar,
  Code,
  FileText,
  ShieldCheck,
  Zap
} from 'lucide-react';
import { fetchCollisionRecords, fetchCollisionDetail } from '../services/api';
import { CollisionRecord, CollisionDetail } from '../types';

interface RecordsPageProps {
  selectedYear: string;
}

export const RecordsPage: React.FC<RecordsPageProps> = ({ selectedYear }) => {
  const [records, setRecords] = useState<CollisionRecord[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);

  const [searchTerm, setSearchTerm] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('all');

  const [selectedRecordIndex, setSelectedRecordIndex] = useState<string | null>(null);
  const [recordDetail, setRecordDetail] = useState<CollisionDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);
  const [modalTab, setModalTab] = useState<'relational' | 'raw_json'>('relational');

  // Load records
  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    fetchCollisionRecords(selectedYear, page, 25, searchTerm, severityFilter)
      .then((res) => {
        if (isMounted) {
          setRecords(res.records);
          setTotalCount(res.total_count);
          setTotalPages(res.total_pages);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => {
        if (isMounted) setLoading(false);
      });
    return () => { isMounted = false; };
  }, [selectedYear, page, searchTerm, severityFilter]);

  // Load detail when modal opened
  useEffect(() => {
    if (!selectedRecordIndex) {
      setRecordDetail(null);
      return;
    }
    let isMounted = true;
    setDetailLoading(true);
    fetchCollisionDetail(selectedRecordIndex)
      .then((res) => {
        if (isMounted) setRecordDetail(res);
      })
      .catch((err) => console.error(err))
      .finally(() => {
        if (isMounted) setDetailLoading(false);
      });
    return () => { isMounted = false; };
  }, [selectedRecordIndex]);

  const getSeverityBadge = (severity: string) => {
    if (severity === 'Fatal') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-bold rounded-md bg-rose-50 text-rose-700 border border-rose-200">
          <span className="h-1.5 w-1.5 rounded-full bg-rose-600"></span>
          <span>Fatal</span>
        </span>
      );
    }
    if (severity === 'Serious') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-bold rounded-md bg-amber-50 text-amber-700 border border-amber-200">
          <span className="h-1.5 w-1.5 rounded-full bg-amber-500"></span>
          <span>Serious</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-bold rounded-md bg-slate-100 text-slate-700 border border-slate-200">
        <span className="h-1.5 w-1.5 rounded-full bg-slate-400"></span>
        <span>Slight</span>
      </span>
    );
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Title & Schema Metadata Header */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                Document Query Terminal
              </span>
              <span className="text-xs text-slate-400 font-medium">
                • MongoDB Primary Shard: <code>roadsafe.collisions</code>
              </span>
            </div>
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
              Granular Collision Records Explorer
            </h1>
            <p className="text-xs text-slate-600 mt-1 max-w-3xl leading-relaxed">
              Direct BSON query interface into the STATS19 collision corpus. Supports fast primary key lookups via indexed <code>collision_index</code> or highway numbers, with dynamic one-to-many joined casualty and vehicle subdocuments.
            </p>
          </div>
          <div className="text-right self-start lg:self-center">
            <span className="text-xs font-mono font-bold text-slate-700 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
              {(totalCount ?? 0).toLocaleString()} Matching Incidents
            </span>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-4 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search index (e.g. 2025010...) or road..."
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}
            className="w-full pl-9 pr-8 py-2 rounded-lg border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent bg-slate-50/50 hover:bg-white transition-colors"
          />
          {searchTerm && (
            <button
              onClick={() => { setSearchTerm(''); setPage(1); }}
              className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600 p-0.5"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        {/* Severity Filter Segmented Group */}
        <div className="flex items-center gap-2 w-full md:w-auto justify-between md:justify-end">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
            Severity:
          </span>
          <div className="inline-flex rounded-lg shadow-sm" role="group">
            {[
              { id: 'all', label: 'All' },
              { id: 'Fatal', label: 'Fatal' },
              { id: 'Serious', label: 'Serious' },
              { id: 'Slight', label: 'Slight' }
            ].map((s) => (
              <button
                key={s.id}
                onClick={() => { setSeverityFilter(s.id); setPage(1); }}
                className={`px-3 py-1.5 text-xs font-semibold transition-all duration-150 active:scale-[0.98] border ${
                  severityFilter === s.id
                    ? 'bg-slate-900 text-white border-slate-900 z-10 shadow-sm'
                    : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                } ${s.id === 'all' ? 'rounded-l-lg' : ''} ${s.id === 'Slight' ? 'rounded-r-lg' : ''} -ml-px first:ml-0`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Records Table */}
      <div className="bg-white border border-slate-200/80 rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-64 text-slate-500 text-xs">
            <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-slate-900 border-t-transparent mb-2.5"></div>
            <span>Executing MongoDB query...</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50/80 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-3 px-4">Collision Index</th>
                  <th className="py-3 px-4">Date & Time</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Roadway & Speed</th>
                  <th className="py-3 px-4">Environment</th>
                  <th className="py-3 px-4 text-center">Vehicles</th>
                  <th className="py-3 px-4 text-center">Casualties</th>
                  <th className="py-3 px-4 text-right">Inspector</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {records.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-slate-400 text-xs">
                      No matching records found for "{searchTerm}".
                    </td>
                  </tr>
                ) : (
                  records.map((r) => (
                    <tr key={r.collision_index} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-3 px-4 font-mono font-bold text-slate-900 text-xs">
                        {r.collision_index}
                      </td>
                      <td className="py-3 px-4 text-slate-700 font-mono tabular-nums">
                        <div className="font-semibold text-slate-900">{r.date}</div>
                        <div className="text-[11px] text-slate-400">{r.time || 'Time unspecified'}</div>
                      </td>
                      <td className="py-3 px-4">
                        {getSeverityBadge(r.severity)}
                      </td>
                      <td className="py-3 px-4 text-slate-700">
                        <div className="font-semibold text-slate-900">
                          {r.first_road_number ? `Road ${r.first_road_number}` : r.road_type}
                        </div>
                        <div className="text-[11px] text-slate-500 font-mono">
                          {r.speed_limit ? `${r.speed_limit} mph` : 'N/A'} • {r.urban_rural}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-slate-700 max-w-xs">
                        <div className="font-medium text-slate-800 truncate">{r.weather_conditions}</div>
                        <div className="text-[11px] text-slate-400 truncate">{r.road_surface_conditions}</div>
                      </td>
                      <td className="py-3 px-4 text-center font-mono font-bold text-slate-800 tabular-nums">
                        {r.number_of_vehicles}
                      </td>
                      <td className="py-3 px-4 text-center font-mono font-extrabold text-slate-900 tabular-nums">
                        {r.number_of_casualties}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => setSelectedRecordIndex(r.collision_index)}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-900 hover:text-white text-slate-700 font-semibold text-xs transition-all duration-150 active:scale-[0.98] border border-slate-200"
                        >
                          <span>Inspect</span>
                          <ExternalLink className="h-3 w-3" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        <div className="bg-slate-50/70 border-t border-slate-200 px-4 py-3 flex items-center justify-between text-xs">
          <span className="font-medium text-slate-600 font-mono tabular-nums">
            Page {page} of {totalPages} ({(totalCount ?? 0).toLocaleString()} total documents)
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(p - 1, 1))}
              disabled={page <= 1}
              className="px-2.5 py-1.5 rounded-md border border-slate-200 bg-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 text-slate-700 font-semibold transition active:scale-[0.98] flex items-center gap-1"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
              <span>Previous</span>
            </button>
            <button
              onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
              disabled={page >= totalPages}
              className="px-2.5 py-1.5 rounded-md border border-slate-200 bg-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 text-slate-700 font-semibold transition active:scale-[0.98] flex items-center gap-1"
            >
              <span>Next</span>
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Record Details Modal */}
      {selectedRecordIndex && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl border border-slate-200 max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/60 shrink-0">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    MongoDB Record Inspector
                  </span>
                  <span className="font-mono text-[11px] text-slate-500 font-semibold">
                    _id / index:
                  </span>
                </div>
                <h3 className="text-lg font-extrabold font-mono text-slate-900 mt-0.5 tracking-tight">
                  {selectedRecordIndex}
                </h3>
              </div>

              {/* View Toggle (Relational vs Raw JSON) */}
              <div className="flex items-center gap-3">
                <div className="inline-flex rounded-lg border border-slate-200 bg-white p-0.5 shadow-sm text-xs">
                  <button
                    onClick={() => setModalTab('relational')}
                    className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-md font-semibold transition ${
                      modalTab === 'relational'
                        ? 'bg-slate-900 text-white'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    <FileText className="w-3.5 h-3.5" />
                    <span>Entity View</span>
                  </button>
                  <button
                    onClick={() => setModalTab('raw_json')}
                    className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-md font-semibold transition ${
                      modalTab === 'raw_json'
                        ? 'bg-slate-900 text-white'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    <Code className="w-3.5 h-3.5" />
                    <span>Raw JSON Document</span>
                  </button>
                </div>

                <button
                  onClick={() => setSelectedRecordIndex(null)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-6 flex-1 text-xs">
              {detailLoading || !recordDetail ? (
                <div className="py-16 text-center text-slate-400">
                  <div className="inline-block animate-spin rounded-full h-7 w-7 border-2 border-slate-900 border-t-transparent mb-3"></div>
                  <p className="font-mono">Resolving foreign keys across collections...</p>
                </div>
              ) : modalTab === 'raw_json' ? (
                /* Raw JSON Document Viewer */
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs text-slate-500 font-mono">
                    <span>Direct BSON Document Dump</span>
                    <span>Format: Application/JSON</span>
                  </div>
                  <pre className="bg-slate-900 text-slate-100 p-4 rounded-xl overflow-x-auto font-mono text-[11px] leading-relaxed max-h-[60vh] border border-slate-800">
                    {JSON.stringify(recordDetail, null, 2)}
                  </pre>
                </div>
              ) : (
                /* Relational Entity View */
                <>
                  {/* Primary Collision Summary Grid */}
                  <div className="bg-slate-50/80 rounded-xl border border-slate-200/80 p-4">
                    <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-3">
                      Collision Core Report
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                      <div>
                        <span className="text-[11px] font-medium text-slate-500">Date & Calendar Year</span>
                        <div className="font-bold text-slate-900 font-mono mt-0.5">{recordDetail.date} ({recordDetail.collision_year})</div>
                      </div>
                      <div>
                        <span className="text-[11px] font-medium text-slate-500">Incident Severity</span>
                        <div className="mt-0.5">{getSeverityBadge(recordDetail.severity)}</div>
                      </div>
                      <div>
                        <span className="text-[11px] font-medium text-slate-500">Posted Speed Limit</span>
                        <div className="font-bold font-mono text-slate-900 mt-0.5">{recordDetail.speed_limit ? `${recordDetail.speed_limit} mph` : 'Unspecified'}</div>
                      </div>
                      <div>
                        <span className="text-[11px] font-medium text-slate-500">Geographic Environment</span>
                        <div className="font-bold text-slate-900 mt-0.5">{recordDetail.urban_rural} Area</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-4 pt-4 border-t border-slate-200/60">
                      <div>
                        <span className="text-[11px] font-medium text-slate-500">Atmospheric Weather</span>
                        <div className="font-semibold text-slate-900 mt-0.5">{recordDetail.weather_conditions}</div>
                      </div>
                      <div>
                        <span className="text-[11px] font-medium text-slate-500">Road Surface</span>
                        <div className="font-semibold text-slate-900 mt-0.5">{recordDetail.road_surface_conditions}</div>
                      </div>
                      <div>
                        <span className="text-[11px] font-medium text-slate-500">Illumination</span>
                        <div className="font-semibold text-slate-900 mt-0.5">{recordDetail.light_conditions}</div>
                      </div>
                    </div>
                  </div>

                  {/* Joined Vehicles Table */}
                  <div>
                    <div className="flex items-center justify-between border-b border-slate-200 pb-2 mb-3">
                      <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                        <Car className="h-4 w-4 text-slate-700" />
                        <span>Involved Vehicles ({recordDetail.vehicles.length})</span>
                      </h4>
                      <span className="text-[11px] font-mono text-slate-400">
                        Collection: <code>vehicles</code>
                      </span>
                    </div>

                    {recordDetail.vehicles.length === 0 ? (
                      <p className="text-xs text-slate-400 py-3 text-center bg-slate-50 rounded-lg">
                        No vehicle sub-records associated with this incident index.
                      </p>
                    ) : (
                      <div className="border border-slate-200 rounded-lg overflow-hidden">
                        <table className="w-full text-left border-collapse">
                          <thead>
                            <tr className="bg-slate-50/80 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                              <th className="py-2.5 px-3">Vehicle #</th>
                              <th className="py-2.5 px-3">Classification</th>
                              <th className="py-2.5 px-3">Driver Profile</th>
                              <th className="py-2.5 px-3">Displacement</th>
                              <th className="py-2.5 px-3 font-mono text-right">System ID</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100">
                            {recordDetail.vehicles.map((v) => (
                              <tr key={v.vehicle_id} className="hover:bg-slate-50/60">
                                <td className="py-2.5 px-3 font-mono font-bold text-slate-900">
                                  #{v.vehicle_reference}
                                </td>
                                <td className="py-2.5 px-3 font-semibold text-slate-800">
                                  {v.vehicle_type}
                                </td>
                                <td className="py-2.5 px-3 text-slate-600">
                                  {v.sex_of_driver}, Age {v.age_of_driver || 'Unknown'}
                                </td>
                                <td className="py-2.5 px-3 font-mono text-slate-700">
                                  {v.engine_capacity_cc ? `${(v.engine_capacity_cc ?? 0).toLocaleString()} cc` : 'N/A'}
                                </td>
                                <td className="py-2.5 px-3 text-right font-mono text-slate-400 text-[11px]">
                                  {v.vehicle_id}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>

                  {/* Joined Casualties Table */}
                  <div>
                    <div className="flex items-center justify-between border-b border-slate-200 pb-2 mb-3">
                      <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                        <Users className="h-4 w-4 text-slate-700" />
                        <span>Injured Casualties ({recordDetail.casualties.length})</span>
                      </h4>
                      <span className="text-[11px] font-mono text-slate-400">
                        Collection: <code>casualties</code>
                      </span>
                    </div>

                    {recordDetail.casualties.length === 0 ? (
                      <p className="text-xs text-slate-400 py-3 text-center bg-slate-50 rounded-lg">
                        No individual injury records registered.
                      </p>
                    ) : (
                      <div className="border border-slate-200 rounded-lg overflow-hidden">
                        <table className="w-full text-left border-collapse">
                          <thead>
                            <tr className="bg-slate-50/80 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                              <th className="py-2.5 px-3">Casualty #</th>
                              <th className="py-2.5 px-3">Role / Class</th>
                              <th className="py-2.5 px-3">Injury Severity</th>
                              <th className="py-2.5 px-3">Demographics</th>
                              <th className="py-2.5 px-3 font-mono text-right">System ID</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100">
                            {recordDetail.casualties.map((c) => (
                              <tr key={c.casualty_id} className="hover:bg-slate-50/60">
                                <td className="py-2.5 px-3 font-mono font-bold text-slate-900">
                                  #{c.casualty_reference}
                                </td>
                                <td className="py-2.5 px-3 font-semibold text-slate-800">
                                  {c.casualty_class}
                                </td>
                                <td className="py-2.5 px-3">
                                  {getSeverityBadge(c.severity)}
                                </td>
                                <td className="py-2.5 px-3 text-slate-600">
                                  {c.sex_of_casualty}, Age {c.age_of_casualty || 'Unknown'}
                                </td>
                                <td className="py-2.5 px-3 text-right font-mono text-slate-400 text-[11px]">
                                  {c.casualty_id}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-3 border-t border-slate-200 bg-slate-50/60 flex items-center justify-between shrink-0">
              <span className="text-[11px] text-slate-500 font-mono">
                Source: DfT STATS19 Certified Record
              </span>
              <button
                onClick={() => setSelectedRecordIndex(null)}
                className="px-4 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold transition active:scale-[0.98]"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
