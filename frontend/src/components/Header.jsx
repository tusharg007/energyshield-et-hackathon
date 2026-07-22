export default function Header() {
  return (
    <header className="border-b border-[#1f2937] bg-[#0d1425]/95 shadow-[0_12px_40px_rgba(0,0,0,0.28)] backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex size-11 shrink-0 items-center justify-center rounded-xl border border-[#f59e0b]/30 bg-[#f59e0b]/10">
            <svg
              aria-hidden="true"
              className="size-7 text-[#f59e0b]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="1.7"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 3 4.8 6v5.3c0 4.5 2.9 8.1 7.2 9.7 4.3-1.6 7.2-5.2 7.2-9.7V6L12 3Z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="m13.2 7.3-4 5.2h3l-1.3 4.2 4-5.4h-3l1.3-4Z"
              />
            </svg>
          </div>
          <div className="min-w-0">
            <div className="flex items-baseline gap-2">
              <h1 className="truncate text-lg font-bold tracking-tight text-[#f9fafb] sm:text-xl">
                EnergyShield
              </h1>
              <span className="hidden rounded border border-[#f59e0b]/30 px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-[0.2em] text-[#f59e0b] sm:inline">
                India
              </span>
            </div>
            <p className="truncate text-xs text-[#9ca3af] sm:text-sm">
              AI-Driven Energy Supply Chain Resilience
            </p>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2 rounded-full border border-[#10b981]/25 bg-[#10b981]/10 px-3 py-1.5 text-xs font-medium text-[#a7f3d0] sm:text-sm">
          <span className="relative flex size-2">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-[#10b981] opacity-50" />
            <span className="relative inline-flex size-2 rounded-full bg-[#10b981]" />
          </span>
          <span className="hidden sm:inline">System Active</span>
          <span className="sm:hidden">Active</span>
        </div>
      </div>
    </header>
  );
}
