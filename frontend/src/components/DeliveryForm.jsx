export default function DeliveryForm({
  locations,
  depotId,
  deliveriesText,
  instructions,
  returnToDepot,
  loading,
  onDepotChange,
  onDeliveriesChange,
  onInstructionsChange,
  onReturnChange,
  onLoadExample,
  onReview,
}) {
  return (
    <section className="card">
      <h2>1. Enter deliveries</h2>

      <label htmlFor="depot">Depot (start of the route)</label>
      <select
        id="depot"
        value={depotId}
        onChange={(event) => onDepotChange(event.target.value)}
        disabled={loading}
      >
        {locations.map((location) => (
          <option key={location.id} value={location.id}>
            {location.name}
          </option>
        ))}
      </select>

      <label htmlFor="deliveries">Delivery addresses (one per line, up to 8)</label>
      <textarea
        id="deliveries"
        rows={7}
        value={deliveriesText}
        onChange={(event) => onDeliveriesChange(event.target.value)}
        disabled={loading}
        placeholder="Madhapur&#10;Kondapur, Hyderabad"
      />

      <label htmlFor="instructions">Instructions (optional)</label>
      <textarea
        id="instructions"
        rows={2}
        value={instructions}
        onChange={(event) => onInstructionsChange(event.target.value)}
        disabled={loading}
      />

      <label className="checkbox">
        <input
          type="checkbox"
          checked={returnToDepot}
          onChange={(event) => onReturnChange(event.target.checked)}
          disabled={loading}
        />
        Return to the depot at the end
      </label>

      <div className="buttons">
        <button type="button" onClick={onLoadExample} disabled={loading}>
          Load example
        </button>
        <button type="button" className="primary" onClick={onReview} disabled={loading}>
          {loading ? 'Working...' : 'Review deliveries'}
        </button>
      </div>
    </section>
  )
}
