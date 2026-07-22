import { useState } from "react";

const QUICK_LEVELS = [20, 40, 60, 80];

export default function ControlPanel({ onRunPipeline, isLoading }) {
  const [sliderValue, setSliderValue] = useState(40);
  const [scenarioName, setScenarioName] = useState(
    "Hormuz Partial Closure — Live Analysis",
  );

  function handleSubmit(event) {
    event.preventDefault();
    onRunPipeline(sliderValue / 100, scenarioName.trim());
  }

  return (
    <section className="overflow-hidden rounded-2xl border border-[#1f2937] border-l-4 border-l-[#f59e0b] bg-[#111827] shadow-[0_18px_50px_rgba(0,0,0,0.2)]">
      <form onSubmit={handleSubmit} className="p-5 sm:p-6">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <p className="mb-1 text-[10px] font-semibold uppercase tracking-[0.24em] text-[#f59e0b]">
              Intelligence Control
            </p>
            <h2 className="text-lg font-semibold text-[#f9fafb]">
              Scenario Configuration
            </h2>
          </div>
          <div className="rounded-xl border border-[#f59e0b]/20 bg-[#0a0f1e] px-4 py-2 text-2xl font-bold tabular-nums text-[#f59e0b]">
            {sliderValue}%
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.25fr_1fr]">
          <div>
            <div className="mb-3 flex items-center justify-between">
              <label
                htmlFor="closure-level"
                className="text-sm font-medium text-[#d1d5db]"
              >
                Hormuz Closure Level
              </label>
              <span className="text-xs text-[#6b7280]">10%–90%</span>
            </div>
            <input
              id="closure-level"
              type="range"
              min="10"
              max="90"
              step="5"
              value={sliderValue}
              onChange={(event) => setSliderValue(Number(event.target.value))}
              className="h-2 w-full cursor-pointer accent-[#f59e0b]"
              aria-valuetext={`${sliderValue}% closure`}
            />
            <div className="mt-4 grid grid-cols-4 gap-2">
              {QUICK_LEVELS.map((level) => (
                <button
                  key={level}
                  type="button"
                  onClick={() => setSliderValue(level)}
                  className={`rounded-lg border px-3 py-2 text-xs font-semibold transition focus:outline-none focus:ring-2 focus:ring-[#f59e0b]/60 ${
                    sliderValue === level
                      ? "border-[#f59e0b] bg-[#f59e0b]/15 text-[#fbbf24]"
                      : "border-[#374151] bg-[#0a0f1e] text-[#9ca3af] hover:border-[#f59e0b]/50 hover:text-[#f9fafb]"
                  }`}
                >
                  {level}%
                </button>
              ))}
            </div>
          </div>

          <div>
            <label
              htmlFor="scenario-name"
              className="mb-3 block text-sm font-medium text-[#d1d5db]"
            >
              Scenario Name
            </label>
            <input
              id="scenario-name"
              type="text"
              value={scenarioName}
              onChange={(event) => setScenarioName(event.target.value)}
              required
              maxLength={200}
              className="w-full rounded-xl border border-[#374151] bg-[#0a0f1e] px-4 py-3 text-sm text-[#f9fafb] outline-none transition placeholder:text-[#6b7280] focus:border-[#f59e0b] focus:ring-2 focus:ring-[#f59e0b]/15"
            />
            <p className="mt-2 text-xs text-[#6b7280]">
              Runs geopolitical, impact, and procurement agents in sequence.
            </p>
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading || !scenarioName.trim()}
          className={`mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-[#f59e0b] px-5 py-3.5 text-sm font-bold text-[#0a0f1e] shadow-[0_10px_30px_rgba(245,158,11,0.18)] transition hover:bg-[#fbbf24] focus:outline-none focus:ring-2 focus:ring-[#fbbf24] focus:ring-offset-2 focus:ring-offset-[#111827] disabled:cursor-not-allowed disabled:opacity-60 ${isLoading ? "animate-pulse" : ""}`}
        >
          {isLoading ? (
            <>
              <svg
                aria-hidden="true"
                className="size-4 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4Z"
                />
              </svg>
              Analyzing...
            </>
          ) : (
            <>
              <span aria-hidden="true">▶</span>
              Run Full Intelligence Pipeline
            </>
          )}
        </button>
      </form>
    </section>
  );
}
