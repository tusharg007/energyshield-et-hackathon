const RISK_LEVELS = {
  critical: {
    label: "CRITICAL",
    color: "#ef4444",
    badge: "border-[#ef4444]/30 bg-[#ef4444]/10 text-[#fca5a5]",
  },
  elevated: {
    label: "ELEVATED",
    color: "#f59e0b",
    badge: "border-[#f59e0b]/30 bg-[#f59e0b]/10 text-[#fbbf24]",
  },
  moderate: {
    label: "MODERATE",
    color: "#10b981",
    badge: "border-[#10b981]/30 bg-[#10b981]/10 text-[#6ee7b7]",
  },
};

function riskLevel(score) {
  if (score >= 0.75) return RISK_LEVELS.critical;
  if (score >= 0.5) return RISK_LEVELS.elevated;
  return RISK_LEVELS.moderate;
}

function SkeletonCard() {
  return (
    <div className="animate-pulse rounded-xl border border-[#1f2937] bg-[#0d1425] p-5">
      <div className="mb-6 h-4 w-2/3 rounded bg-[#1f2937]" />
      <div className="mb-4 h-10 w-20 rounded bg-[#1f2937]" />
      <div className="mb-5 h-2 rounded-full bg-[#1f2937]" />
      <div className="h-8 rounded bg-[#1f2937]" />
    </div>
  );
}

export default function RiskCorridorPanel({
  corridors,
  riskAssessments,
  isLoading,
}) {
  const assessmentByCorridor = new Map(
    riskAssessments.map((item) => [item.corridor_name, item]),
  );
  const latestTimestamp = riskAssessments.length
    ? corridors
        .map((corridor) => corridor.last_updated)
        .filter(Boolean)
        .sort()
        .at(-1)
    : null;

  return (
    <section className="rounded-2xl border border-[#1f2937] bg-[#111827] p-5 shadow-[0_18px_50px_rgba(0,0,0,0.16)] sm:p-6">
      <div className="mb-5 flex flex-col justify-between gap-2 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-[10px] font-semibold uppercase tracking-[0.24em] text-[#3b82f6]">
            Live Threat Matrix
          </p>
          <h2 className="text-lg font-semibold text-[#f9fafb]">
            Live Corridor Risk Intelligence
          </h2>
        </div>
        <p className="text-xs text-[#9ca3af]">
          Updated by AI agent —{" "}
          {latestTimestamp
            ? new Date(latestTimestamp).toLocaleString()
            : "Awaiting run"}
        </p>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2">
          {Array.from({ length: 5 }, (_, index) => (
            <SkeletonCard key={index} />
          ))}
        </div>
      ) : corridors.length ? (
        <div className="grid gap-4 md:grid-cols-2">
          {corridors.map((corridor) => {
            const assessment = assessmentByCorridor.get(corridor.corridor_name);
            const score = assessment?.new_score ?? corridor.current_risk_score;
            const level = riskLevel(score);
            const reasoning = assessment?.reasoning_trace || "";
            return (
              <article
                key={corridor.id ?? corridor.corridor_name}
                className="rounded-xl border border-[#1f2937] border-l-4 bg-[#0d1425] p-5 transition hover:border-[#374151]"
                style={{ borderLeftColor: level.color }}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-semibold text-[#f9fafb]">
                      {corridor.corridor_name}
                    </h3>
                    <p className="mt-1 text-xs text-[#6b7280]">
                      {corridor.region}
                    </p>
                  </div>
                  <span
                    className={`rounded-full border px-2.5 py-1 text-[10px] font-bold tracking-wider ${level.badge}`}
                  >
                    {level.label}
                  </span>
                </div>

                <div className="mt-5 flex items-end justify-between gap-3">
                  <span
                    className="text-4xl font-bold tabular-nums tracking-tight"
                    style={{ color: level.color }}
                  >
                    {Number(score).toFixed(2)}
                  </span>
                  {assessment && (
                    <span
                      className={`text-sm font-semibold tabular-nums ${
                        assessment.delta >= 0
                          ? "text-[#ef4444]"
                          : "text-[#10b981]"
                      }`}
                    >
                      {assessment.delta >= 0 ? "▲" : "▼"}{" "}
                      {assessment.delta >= 0 ? "+" : ""}
                      {Number(assessment.delta).toFixed(2)}
                    </span>
                  )}
                </div>

                <div className="mt-3 h-2 overflow-hidden rounded-full bg-[#1f2937]">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{
                      backgroundColor: level.color,
                      width: `${Math.max(0, Math.min(100, score * 100))}%`,
                    }}
                  />
                </div>

                {assessment && (
                  <p className="mt-4 border-t border-[#1f2937] pt-3 text-xs italic leading-5 text-[#9ca3af]">
                    {reasoning.length > 120
                      ? `${reasoning.slice(0, 120)}...`
                      : reasoning}
                  </p>
                )}
              </article>
            );
          })}
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-[#374151] bg-[#0d1425] px-6 py-12 text-center">
          <p className="font-medium text-[#d1d5db]">No corridor data available</p>
          <p className="mt-1 text-sm text-[#6b7280]">
            Start the FastAPI backend to load live corridor intelligence.
          </p>
        </div>
      )}
    </section>
  );
}
