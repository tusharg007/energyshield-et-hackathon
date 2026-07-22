function scoreColor(score) {
  if (score > 0.7) return "#10b981";
  if (score >= 0.5) return "#f59e0b";
  return "#ef4444";
}

function ScoreBreakdown({ recommendation }) {
  const segments = [
    {
      label: "Price",
      score: recommendation.price_score,
      weight: 0.25,
      color: "#3b82f6",
    },
    {
      label: "Time",
      score: recommendation.time_score,
      weight: 0.25,
      color: "#10b981",
    },
    {
      label: "Grade",
      score: recommendation.grade_score,
      weight: 0.3,
      color: "#f59e0b",
    },
    {
      label: "Safety",
      score: recommendation.corridor_safety_score,
      weight: 0.2,
      color: "#ef4444",
    },
  ];
  const contributionTotal = segments.reduce(
    (total, segment) => total + segment.score * segment.weight,
    0,
  );

  return (
    <div className="flex h-2.5 min-w-28 overflow-hidden rounded-full bg-[#1f2937]">
      {segments.map((segment) => {
        const contribution = segment.score * segment.weight;
        return (
          <span
            key={segment.label}
            title={`${segment.label}: ${segment.score.toFixed(2)} (${(
              contribution * 100
            ).toFixed(1)} weighted points)`}
            className="h-full first:rounded-l-full last:rounded-r-full"
            style={{
              backgroundColor: segment.color,
              width: `${contributionTotal ? (contribution / contributionTotal) * 100 : 25}%`,
            }}
          />
        );
      })}
    </div>
  );
}

function SkeletonRows() {
  return Array.from({ length: 5 }, (_, index) => (
    <tr key={index} className="animate-pulse border-t border-[#1f2937]">
      {Array.from({ length: 9 }, (_, cell) => (
        <td key={cell} className="px-4 py-4">
          <div className="h-4 rounded bg-[#1f2937]" />
        </td>
      ))}
    </tr>
  ));
}

export default function ProcurementTable({ recommendations, importGap, isLoading }) {
  return (
    <section className="overflow-hidden rounded-2xl border border-[#1f2937] bg-[#111827] shadow-[0_18px_50px_rgba(0,0,0,0.16)]">
      <div className="p-5 sm:p-6">
        <div className="flex flex-col justify-between gap-2 lg:flex-row lg:items-end">
          <div>
            <p className="mb-1 text-[10px] font-semibold uppercase tracking-[0.24em] text-[#10b981]">
              Supply Reallocation
            </p>
            <h2 className="text-lg font-semibold text-[#f9fafb]">
              Procurement Alternatives — Ranked by Composite Score
            </h2>
            <p className="mt-2 text-xs leading-5 text-[#9ca3af]">
              Hormuz suppliers excluded | Ranked: price (25%) + time (25%) +
              grade (30%) + corridor safety (20%)
            </p>
          </div>
          {importGap > 0 && (
            <div className="rounded-lg border border-[#f59e0b]/25 bg-[#f59e0b]/5 px-3 py-2 text-xs text-[#fbbf24]">
              Gap allocation: <strong>{Number(importGap).toFixed(2)} MBD</strong>
            </div>
          )}
        </div>
      </div>

      <div className="overflow-x-auto border-t border-[#1f2937]">
        <table className="w-full min-w-[1100px] border-collapse text-left text-sm">
          <thead className="bg-[#0a0f1e] text-[10px] uppercase tracking-wider text-[#6b7280]">
            <tr>
              <th className="px-4 py-3 font-semibold">Rank</th>
              <th className="px-4 py-3 font-semibold">Supplier</th>
              <th className="px-4 py-3 font-semibold">Country</th>
              <th className="px-4 py-3 font-semibold">Grade</th>
              <th className="px-4 py-3 font-semibold">Price $/bbl</th>
              <th className="px-4 py-3 font-semibold">Lead Time</th>
              <th className="px-4 py-3 font-semibold">Composite Score</th>
              <th className="px-4 py-3 font-semibold">Score Breakdown</th>
              <th className="px-4 py-3 font-semibold">Volume MBD</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <SkeletonRows />
            ) : recommendations.length ? (
              recommendations.map((item) => {
                const topRank = item.rank <= 3;
                const color = scoreColor(item.composite_score);
                return (
                  <tr
                    key={`${item.rank}-${item.supplier_name}`}
                    className={`border-t border-[#1f2937] transition hover:bg-[#1f2937]/35 ${
                      topRank
                        ? "border-l-2 border-l-[#f59e0b] bg-[#f59e0b]/[0.025]"
                        : "border-l-2 border-l-transparent"
                    }`}
                  >
                    <td className="px-4 py-4">
                      <span
                        className={`inline-flex size-7 items-center justify-center rounded-full text-xs font-bold ${
                          topRank
                            ? "bg-[#f59e0b]/15 text-[#fbbf24]"
                            : "bg-[#1f2937] text-[#9ca3af]"
                        }`}
                      >
                        {item.rank}
                      </span>
                    </td>
                    <td className="max-w-48 px-4 py-4 font-medium text-[#f9fafb]">
                      {item.supplier_name}
                    </td>
                    <td className="px-4 py-4 text-[#9ca3af]">{item.country}</td>
                    <td className="px-4 py-4 text-[#d1d5db]">{item.crude_grade}</td>
                    <td className="px-4 py-4 tabular-nums text-[#d1d5db]">
                      ${Number(item.base_price_usd_bbl).toFixed(2)}
                    </td>
                    <td className="px-4 py-4 tabular-nums text-[#d1d5db]">
                      {item.lead_time_days} days
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-16 overflow-hidden rounded-full bg-[#1f2937]">
                          <div
                            className="h-full rounded-full"
                            style={{
                              backgroundColor: color,
                              width: `${item.composite_score * 100}%`,
                            }}
                          />
                        </div>
                        <span
                          className="font-semibold tabular-nums"
                          style={{ color }}
                        >
                          {Number(item.composite_score).toFixed(3)}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <ScoreBreakdown recommendation={item} />
                    </td>
                    <td className="px-4 py-4 font-semibold tabular-nums text-[#f9fafb]">
                      {topRank ? Number(item.volume_mbd).toFixed(3) : "—"}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="9" className="px-6 py-12 text-center">
                  <p className="font-medium text-[#d1d5db]">
                    No procurement recommendations yet
                  </p>
                  <p className="mt-1 text-sm text-[#6b7280]">
                    Run the full pipeline to rank alternative suppliers.
                  </p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
