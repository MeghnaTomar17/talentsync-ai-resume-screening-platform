export function Progress({ value }: { value: number }) {
  const bounded = Math.max(0, Math.min(100, value));
  return (
    <div className="progress" aria-label={`Progress ${bounded}%`}>
      <div className="progress-bar" style={{ width: `${bounded}%` }} />
    </div>
  );
}
