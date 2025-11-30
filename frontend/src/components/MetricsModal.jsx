import React, { useEffect, useState } from 'react';
import { X, Activity, Zap, BarChart3, CheckCircle, AlertCircle } from 'lucide-react';

const MetricsModal = ({ onClose }) => {
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchMetrics = async () => {
        try {
            setLoading(true);
            // const response = await fetch('http://127.0.0.1:8000/metrics');
const response = await fetch('/metrics');

            if (!response.ok) throw new Error('Failed to fetch metrics');
            const data = await response.json();
            setMetrics(data);
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 5000); // Refresh every 5s
        return () => clearInterval(interval);
    }, []);

    // Parse the performance report string into structured data if possible
    const parseReport = (report) => {
        if (!report || report === "No performance data available") return null;

        const lines = report.split('\n');
        const data = {};
        lines.forEach(line => {
            if (line.includes('Average Latency:')) data.avgLatency = line.split(':')[1].trim();
            if (line.includes('P95 Latency:')) data.p95Latency = line.split(':')[1].trim();
            if (line.includes('Status:')) data.status = line.split(':')[1].trim();
        });
        return data;
    };

    const reportData = metrics ? parseReport(metrics.performance_report) : null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-fade-in">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-scale-up">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-slate-100">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 bg-blue-100 rounded-lg">
                            <Activity className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-slate-800">System Metrics</h2>
                            <p className="text-sm text-slate-500">Real-time performance monitoring</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-slate-100 rounded-full transition-colors duration-200"
                    >
                        <X className="w-5 h-5 text-slate-400" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {loading && !metrics ? (
                        <div className="flex justify-center py-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                        </div>
                    ) : error ? (
                        <div className="bg-red-50 text-red-600 p-4 rounded-xl flex items-center space-x-3">
                            <AlertCircle className="w-5 h-5" />
                            <span>{error}</span>
                        </div>
                    ) : (
                        <>
                            {/* Key Stats Grid */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                                    <div className="flex items-center space-x-2 text-slate-500 mb-2">
                                        <BarChart3 className="w-4 h-4" />
                                        <span className="text-xs font-medium uppercase tracking-wider">Translations</span>
                                    </div>
                                    <div className="text-2xl font-bold text-slate-800">
                                        {metrics?.total_translations || 0}
                                    </div>
                                </div>
                                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                                    <div className="flex items-center space-x-2 text-slate-500 mb-2">
                                        <Zap className="w-4 h-4" />
                                        <span className="text-xs font-medium uppercase tracking-wider">Active Users</span>
                                    </div>
                                    <div className="text-2xl font-bold text-slate-800">
                                        {metrics?.active_connections || 0}
                                    </div>
                                </div>
                            </div>

                            {/* Performance Report */}
                            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-5 text-white shadow-lg">
                                <h3 className="text-sm font-medium text-slate-300 mb-4 flex items-center">
                                    <Activity className="w-4 h-4 mr-2" />
                                    Latency Analysis
                                </h3>

                                {reportData ? (
                                    <div className="space-y-4">
                                        <div className="flex justify-between items-end border-b border-slate-700 pb-3">
                                            <span className="text-slate-400 text-sm">Average Latency</span>
                                            <span className="text-2xl font-bold text-blue-400">{reportData.avgLatency}</span>
                                        </div>
                                        <div className="flex justify-between items-end border-b border-slate-700 pb-3">
                                            <span className="text-slate-400 text-sm">P95 Latency</span>
                                            <span className="text-xl font-semibold text-purple-400">{reportData.p95Latency}</span>
                                        </div>
                                        <div className="flex items-center justify-between pt-1">
                                            <span className="text-slate-400 text-sm">System Status</span>
                                            <span className={`flex items-center px-2 py-1 rounded text-xs font-bold ${reportData.status.includes('PASS') ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                                                }`}>
                                                {reportData.status.includes('PASS') ? <CheckCircle className="w-3 h-3 mr-1" /> : <AlertCircle className="w-3 h-3 mr-1" />}
                                                {reportData.status}
                                            </span>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="text-center py-4 text-slate-400 text-sm">
                                        No performance data available yet.
                                        <br />
                                        Start chatting to generate metrics!
                                    </div>
                                )}
                            </div>

                            <div className="text-xs text-center text-slate-400">
                                Metrics update automatically every 5 seconds
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MetricsModal;
