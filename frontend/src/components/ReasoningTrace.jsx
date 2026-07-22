import { useState } from "react";

function CollapsibleSection({ title, accent, isOpen, onToggle, children }) {
  return (
    <div className="overflow-hidden rounded-xl border border-[#1f2937] bg-[#0d1425]">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between gap-4 px-4 py-4 text-left transition hover:bg-[#1f2937]/35 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-[#3b82f6]/50"
        aria-expanded={isOpen}
      >
        <span className="flex items-center gap-3 font-semibold text-[#f9fafb]">
          <span className="h-5 w-1 rounded-full" style={{ backgroundColor: accent }} />
          {title}
        </span>
        <span className="text-xs text-[#9ca3af]" aria-hidden="true">
          {isOpen ? "▲" : "▼"}
        </span>
      </button>
      {isOpen && <div className="border-t border-[#1f2937] p-4">{children}</div>}
    </div>
  );
}

function TraceCard({ heading, text, accent, mono = false }) {
  return (
    <article
      className="rounded-lg border border-[#1f2937] border-l-2 bg-[#0a0f1e] p-4"
      style={{ borderLeftColor: accent }}
    >
      {heading && (
        <h4 className="mb-2 text-sm font-semibold text-[#e5e7eb]">{heading}</h4>
      )}
      <p
        className={`text-xs leading-6 text-[#9ca3af] ${
          mono ? "font-mono" : ""
        }`}
      >
        {text}
      </p>
    </article>
  );
}

function EmptyTrace({ message }) {
  return (
    <p className="rounded-lg border border-dashed border-[#374151] px-4 py-6 text-center text-sm text-[#6b7280]">
      {message}
    </p>
  );
}

export default function ReasoningTrace({
  riskAssessments,
  scenario,
  recommendations,
}) {
  const [openSections, setOpenSections] = useState({
    risk: true,
    scenario: true,
    procurement: true,
  });
  const topRecommendations = recommendations.filter(
    (item) => item.rank <= 3 && item.reasoning_trace,
  );

  function toggle(section) {
    setOpenSections((current) => ({
      ...current,
      [section]: !current[section],
    }));
  }

  return (
    <section className="rounded-2xl border border-[#1f2937] bg-[#111827] p-5 shadow-[0_18px_50px_rgba(0,0,0,0.16)] sm:p-6">
      <div className="mb-5">
        <p className="mb-1 text-[10px] font-semibold uppercase tracking-[0.24em] text-[#3b82f6]">
          Explainable Intelligence
        </p>
        <h2 className="text-lg font-semibold text-[#f9fafb]">
          Agent Reasoning Traces
        </h2>
        <p className="mt-1 text-xs text-[#9ca3af]">
          Transparent AI — every decision explained
        </p>
      </div>

      <div className="space-y-3">
        <CollapsibleSection
          title="🌐 Geopolitical Risk Agent"
          accent="#3b82f6"
          isOpen={openSections.risk}
          onToggle={() => toggle("risk")}
        >
          {riskAssessments.length ? (
            <div className="space-y-3">
              {riskAssessments.map((assessment) => (
                <TraceCard
                  key={assessment.corridor_name}
                  heading={assessment.corridor_name}
                  text={assessment.reasoning_trace}
                  accent="#3b82f6"
                  mono
                />
              ))}
            </div>
          ) : (
            <EmptyTrace message="Risk-agent reasoning will appear after the first pipeline run." />
          )}
        </CollapsibleSection>

        <CollapsibleSection
          title="⚡ Scenario Impact Agent"
          accent="#f59e0b"
          isOpen={openSections.scenario}
          onToggle={() => toggle("scenario")}
        >
          {scenario?.narrative ? (
            <TraceCard text={scenario.narrative} accent="#f59e0b" />
          ) : (
            <EmptyTrace message="The scenario briefing will appear after the impact model runs." />
          )}
        </CollapsibleSection>

        <CollapsibleSection
          title="🛢️ Procurement Orchestrator"
          accent="#10b981"
          isOpen={openSections.procurement}
          onToggle={() => toggle("procurement")}
        >
          {topRecommendations.length ? (
            <div className="space-y-3">
              {topRecommendations.map((recommendation) => (
                <TraceCard
                  key={`${recommendation.rank}-${recommendation.supplier_name}`}
                  heading={`Rank ${recommendation.rank} — ${recommendation.supplier_name}`}
                  text={recommendation.reasoning_trace}
                  accent="#10b981"
                />
              ))}
            </div>
          ) : (
            <EmptyTrace message="Top-three sourcing rationale will appear after procurement ranking." />
          )}
        </CollapsibleSection>
      </div>
    </section>
  );
}
