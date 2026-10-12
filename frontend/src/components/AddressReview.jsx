export default function AddressReview({
  parsed,
  acknowledged,
  canOptimize,
  loading,
  onAcknowledge,
  onOptimize,
}) {
  const hasUnresolved = parsed.deliveries.some((item) => !item.location_id)
  const hasNotes = parsed.clarifications.length > 0

  return (
    <section className="card">
      <h2>2. Review recognized addresses</h2>

      {hasNotes && (
        <div className="notice">
          <strong>Please note:</strong>
          <ul>
            {parsed.clarifications.map((note, index) => (
              <li key={index}>{note}</li>
            ))}
          </ul>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={acknowledged}
              onChange={(event) => onAcknowledge(event.target.checked)}
              disabled={loading}
            />
            I have read these notes
          </label>
        </div>
      )}

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>You entered</th>
            <th>Recognized as</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {parsed.deliveries.map((item) => (
            <tr key={item.id}>
              <td>{item.id}</td>
              <td>{item.original_text}</td>
              <td>{item.display_address || '-'}</td>
              <td className={item.location_id ? 'ok' : 'bad'}>
                {item.location_id ? 'Recognized' : 'Not supported'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {hasUnresolved && (
        <p className="hint">
          Fix the unsupported addresses above and review again. Only the listed demo
          locations are supported.
        </p>
      )}

      <button
        type="button"
        className="primary"
        onClick={onOptimize}
        disabled={!canOptimize || loading}
      >
        {loading ? 'Working...' : 'Optimize route'}
      </button>
    </section>
  )
}
