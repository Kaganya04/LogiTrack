import { shortPlaceName } from '../placeName'

const STATUS = {
  catalogue: { label: 'Recognized', className: 'ok' },
  geocoded: { label: 'Approximate (map search)', className: 'approx' },
  none: { label: 'Not found', className: 'bad' },
}

export default function AddressReview({
  parsed,
  acknowledged,
  canOptimize,
  loading,
  onAcknowledge,
  onOptimize,
}) {
  const hasUnresolved = parsed.deliveries.some((item) => item.source === 'none')
  const hasApproximate = parsed.deliveries.some((item) => item.source === 'geocoded')
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
          {parsed.deliveries.map((item) => {
            const status = STATUS[item.source] || STATUS.none
            const geocoded = item.source === 'geocoded' && item.display_address
            return (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.original_text}</td>
                <td title={geocoded ? item.display_address : undefined}>
                  {geocoded ? shortPlaceName(item.display_address) : item.display_address || '-'}
                </td>
                <td className={status.className}>{status.label}</td>
              </tr>
            )
          })}
        </tbody>
      </table>

      {hasApproximate && (
        <p className="hint">
          Approximate addresses were found by an OpenStreetMap search. Check that the matched
          place is the right one; house numbers often resolve only to the street or area.
        </p>
      )}

      {hasUnresolved && (
        <p className="hint">
          Fix the addresses that were not found and review again. Only addresses in Hyderabad
          are supported.
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
