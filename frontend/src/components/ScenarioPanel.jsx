import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function MetricCard({ label, value, detail, critical = false }) {
  return (
    <div
      className={`rounded-xl border bg-[#0d1425] p-4 ${
        critical ? "border-[#ef4444]/60" : "border-[#1f2937]"
      }`}
    >
      <p className="text-2xl font-bold tabular-nums text-[#f59e0b] sm:text-3xl">
        {value}
      </p>
      <p className="mt-2 text-xs font-semibold uppercase tracking-wider text-[#9ca3af]">
        {label}
      </p>
      {detail && <p className="mt-1 text-xs text-[#6b7280]">{detail}</p>}
    </div>
  );
}

function ScenarioSkeleton() {
  return (
    <div className="grid animate-pulse grid-cols-2 gap-3 lg:grid-cols-3">
      {Array.from({ length: 6 }, (_, index) => (
        <div
          key={index}
          className="h-28 rounded-xl border border-[#1f2937] bg-[#0d1425] p-4"
        >
          <div className="h-8 w-24 rounded bg-[#1f2937]" />
          <div className="mt-4 h-3 w-16 rounded bg-[#1f2937]" />
        </div>
      ))}
    </div>
  );
}

export default function ScenarioPanel({ scenario, comparisons, isLoading }) {
  const comparisonData = comparisons.map((item) => ({
    ...item,
    closureLabel: `${Math.round(item.closure_percentage * 100)}%`,
    gdpScaled: Math.abs(item.gdp_impact_pct) * 10,
  }));

  return (
    <section className="rounded-2xl border border-[#1f2937] bg-[#111827] p-5 shadow-[0_18px_50px_rgba(0,0,0,0.16)] sm:p-6">
      <div className="mb-5">
        <p className="mb-1 text-[10px] font-semibold uppercase tracking-[0.24em] text-[#f59e0b]">
          Deterministic Stress Model
        </p>
        <h2 className="text-lg font-semibold text-[#f9fafb]">
          Hormuz Disruption Impact Model
        </h2>
      </div>

      {isLoading ? (
        <ScenarioSkeleton />
      ) : scenario ? (
        <>
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
            <MetricCard
              label="Import Gap"
              value={`${Number(scenario.import_gap_mbd).toFixed(2)} MBD`}
              detail={`${(scenario.import_gap_pct * 100).toFixed(1)}% of imports`}
            />
            <MetricCard
              label="Brent Spike"
              value={`+${Number(scenario.price_impact_pct).toFixed(0)}%`}
              detail={`$${Number(scenario.new_brent_price).toFixed(0)}/bbl`}
            />
            <MetricCard
              label="Refinery Stress"
              value={`${Number(scenario.refinery_stress_score).toFixed(2)}/1.0`}
              critical={scenario.refinery_stress_score >= 0.5}
            />
            <MetricCard
              label="SPR Cover"
              value={`${Number(scenario.spr_days_remaining).toFixed(1)} days`}
              critical={scenario.spr_days_remaining < 5}
            />
            <MetricCard
              label="GDP Drag"
              value={`${Number(scenario.gdp_impact_pct).toFixed(2)}%`}
              critical={Math.abs(scenario.gdp_impact_pct) > 0.3}
            />
            <MetricCard
              label="Unmet Gap"
              value={`${Number(scenario.unmet_gap_mbd).toFixed(2)} MBD`}
            />
          </div>

          <div className="mt-4 rounded-xl border border-[#f59e0b]/35 bg-[#f59e0b]/5 p-5">
            <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.2em] text-[#f59e0b]">
              Ministerial Briefing Note
            </p>
            <p className="text-sm italic leading-7 text-[#f9fafb]">
              {scenario.narrative}
            </p>
          </div>
        </>
      ) : (
        <div className="rounded-xl border border-dashed border-[#374151] bg-[#0d1425] px-6 py-10 text-center">
          <p className="font-medium text-[#d1d5db]">
            No active disruption scenario
          </p>
          <p className="mt-1 text-sm text-[#6b7280]">
            Configure a closure level and run the intelligence pipeline.
          </p>
        </div>
      )}

      <div className="mt-6 border-t border-[#1f2937] pt-5">
        <div className="mb-4 flex flex-col justify-between gap-1 sm:flex-row sm:items-end">
          <div>
            <h3 className="text-sm font-semibold text-[#e5e7eb]">
              Closure Severity Comparison
            </h3>
            <p className="mt-1 text-xs text-[#6b7280]">
              GDP drag is scaled ×10 for visual comparison.
            </p>
          </div>
          <span className="text-[10px] uppercase tracking-wider text-[#6b7280]">
            MBD / days / scaled %
          </span>
        </div>

        {comparisonData.length ? (
          <div className="h-72 w-full rounded-xl bg-[#0a0f1e] p-2 sm:p-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData}>
                <CartesianGrid stroke="#1f2937" strokeDasharray="3 3" vertical={false} />
                <XAxis
                  dataKey="closureLabel"
                  axisLine={{ stroke: "#374151" }}
                  tick={{ fill: "#9ca3af", fontSize: 12 }}
                  tickLine={false}
                />
                <YAxis
                  axisLine={false}
                  tick={{ fill: "#6b7280", fontSize: 11 }}
                  tickLine={false}
                />
                <Tooltip
                  cursor={{ fill: "rgba(255,255,255,0.03)" }}
                  contentStyle={{
                    background: "#111827",
                    border: "1px solid #374151",
                    borderRadius: "10px",
                    color: "#f9fafb",
                  }}
                  labelStyle={{ color: "#f9fafb", fontWeight: 600 }}
                />
                <Legend wrapperStyle={{ color: "#9ca3af", fontSize: 11 }} />
                <Bar
                  dataKey="import_gap_mbd"
                  name="Import gap"
                  fill="#f59e0b"
                  radius={[4, 4, 0, 0]}
                />
                <Bar
                  dataKey="spr_days_remaining"
                  name="SPR days"
                  fill="#3b82f6"
                  radius={[4, 4, 0, 0]}
                />
                <Bar
                  dataKey="gdpScaled"
                  name="GDP drag ×10"
                  fill="#ef4444"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="rounded-xl border border-dashed border-[#374151] bg-[#0a0f1e] px-6 py-10 text-center text-sm text-[#6b7280]">
            Comparison data is unavailable.
          </div>
        )}
      </div>
    </section>
  );
}
