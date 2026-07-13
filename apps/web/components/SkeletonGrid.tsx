export function SkeletonGrid() {
  return (
    <section className="grid" aria-busy="true" aria-label="Loading analytics">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="card span-3 skeleton block" />
      ))}
      {Array.from({ length: 2 }).map((_, i) => (
        <div key={`wide-${i}`} className="card span-6 skeleton block tall" />
      ))}
    </section>
  );
}
