export default function RouteResults({ route, depotName, parsed }) {
  const names = {}
  parsed.deliveries.forEach((item) => {
    names[item.id] = item.display_address || item.original_text
  })

  return (
    <section className="card">
      <h2>3. Optimized route</h2>
      <ol>
        <li>Start: {depotName}</li>
        {route.ordered_delivery_ids.map((id) => (
          <li key={id}>
            {id}: {names[id]}
          </li>
        ))}
        {route.return_to_depot && <li>Return to: {depotName}</li>}
      </ol>

      <p>
        <strong>Estimated road distance:</strong> {route.total_distance_km.toFixed(1)} km
        <br />
        <strong>Estimated driving time:</strong>{' '}
        {Math.round(route.driving_time_minutes)} minutes
      </p>

      <div className="notice">
        <strong>Assumptions</strong>
        <ul>
          {route.assumptions.map((text, index) => (
            <li key={index}>{text}</li>
          ))}
          <li>One vehicle. Time windows and vehicle capacity are not supported.</li>
        </ul>
      </div>
    </section>
  )
}
