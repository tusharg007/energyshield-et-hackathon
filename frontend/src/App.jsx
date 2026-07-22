import { useEffect, useState } from "react";

import ControlPanel from "./components/ControlPanel";
import { API_BASE } from "./config";
import Header from "./components/Header";
import ProcurementTable from "./components/ProcurementTable";
import ReasoningTrace from "./components/ReasoningTrace";
import RiskCorridorPanel from "./components/RiskCorridorPanel";
import ScenarioPanel from "./components/ScenarioPanel";

async function requestJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // Preserve the status-based fallback for non-JSON errors.
    }
    throw new Error(detail);
  }
  return response.json();
}

function ErrorBanner({ message, onDismiss }) {
  return (
    <div
      role="alert"
      className="flex items-start justify-between gap-4 rounded-xl border border-[#ef4444]/50 bg-[#ef4444]/10 px-4 py-3 text-sm text-[#fecaca]"
    >
      <div className="flex gap-3">
        <svg
          aria-hidden="true"
          className="mt-0.5 size-5 shrink-0 text-[#ef4444]"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 9v4m0 4h.01M10.3 4.5 2.8 17.3A1.8 1.8 0 0 0 4.3 20h15.4a1.8 1.8 0 0 0 1.5-2.7L13.7 4.5a2 2 0 0 0-3.4 0Z"
          />
        </svg>
        <div>
          <p className="font-semibold">Intelligence pipeline error</p>
          <p className="mt-0.5 text-[#fca5a5]">{message}</p>
        </div>
      </div>
      <button
        type="button"
        onClick={onDismiss}
        className="rounded p-1 text-[#fca5a5] transition hover:bg-[#ef4444]/15 hover:text-white focus:outline-none focus:ring-2 focus:ring-[#ef4444]/50"
        aria-label="Dismiss error"
      >
        ✕
      </button>
    </div>
  );
}

export default function App() {
  const [corridors, setCorridors] = useState([]);
  const [comparisons, setComparisons] = useState([]);
  const [pipelineResult, setPipelineResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastRun, setLastRun] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;

    async function loadDashboardData() {
      try {
        const [corridorData, comparisonData] = await Promise.all([
          requestJson(`${API_BASE}/api/corridors`),
          requestJson(
            `${API_BASE}/api/scenarios/compare?closures=0.2,0.4,0.6,0.8`,
          ),
        ]);
        if (active) {
          setCorridors(corridorData);
          setComparisons(comparisonData);
        }
      } catch (loadError) {
        if (active) {
          setError(loadError.message || "Unable to load dashboard data.");
        }
      }
    }

    loadDashboardData();
    return () => {
      active = false;
    };
  }, []);

  async function handleRunPipeline(closurePercentage, scenarioName) {
    setIsLoading(true);
    setError(null);
    try {
      const result = await requestJson(
        `${API_BASE}/api/agents/full-pipeline/run`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            closure_percentage: closurePercentage,
            scenario_name: scenarioName,
          }),
        },
      );
      setPipelineResult(result);
      setLastRun(new Date());

      const refreshedCorridors = await requestJson(
        `${API_BASE}/api/corridors`,
      );
      setCorridors(refreshedCorridors);
    } catch (pipelineError) {
      setError(pipelineError.message || "The intelligence pipeline failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-[#f9fafb] selection:bg-[#f59e0b]/30 selection:text-white">
      <Header />
      <main className="mx-auto max-w-7xl space-y-6 px-4 py-6 sm:px-6 sm:py-8">
        <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-center">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.24em] text-[#6b7280]">
              National Energy Intelligence Console
            </p>
          </div>
          {lastRun && (
            <p className="text-xs text-[#6b7280]">
              Last pipeline run: {lastRun.toLocaleString()}
            </p>
          )}
        </div>

        <ControlPanel
          onRunPipeline={handleRunPipeline}
          isLoading={isLoading}
        />

        {error && (
          <ErrorBanner message={error} onDismiss={() => setError(null)} />
        )}

        <RiskCorridorPanel
          corridors={corridors}
          riskAssessments={pipelineResult?.risk_assessments || []}
          isLoading={isLoading}
        />
        <ScenarioPanel
          scenario={pipelineResult?.scenario || null}
          comparisons={comparisons}
          isLoading={isLoading}
        />
        <ProcurementTable
          recommendations={pipelineResult?.procurement_recommendations || []}
          importGap={pipelineResult?.scenario?.import_gap_mbd || 0}
          isLoading={isLoading}
        />
        <ReasoningTrace
          riskAssessments={pipelineResult?.risk_assessments || []}
          scenario={pipelineResult?.scenario || null}
          recommendations={pipelineResult?.procurement_recommendations || []}
        />
      </main>
      <footer className="border-t border-[#1f2937] px-4 py-5 text-center text-xs text-[#4b5563]">
        EnergyShield · India Energy Supply Chain Resilience System
      </footer>
    </div>
  );
}
