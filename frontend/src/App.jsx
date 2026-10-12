import { useEffect, useState } from 'react'
import { getLocations, optimizeRoute, parseDeliveries } from './api'
import DeliveryForm from './components/DeliveryForm'
import AddressReview from './components/AddressReview'
import RouteResults from './components/RouteResults'
import './App.css'

const EXAMPLE = ['Madhapur', 'Kondapur, Hyderabad', 'Gachibowli', 'Jubilee Hills', 'Ayyappa Society'].join('\n')
const MAX_DELIVERIES = 8

export default function App() {
  const [locations, setLocations] = useState([])
  const [deliveriesText, setDeliveriesText] = useState('')
  const [instructions, setInstructions] = useState('')
  const [depotId, setDepotId] = useState('hitec_hub')
  const [returnToDepot, setReturnToDepot] = useState(true)
  const [parsed, setParsed] = useState(null)
  const [acknowledged, setAcknowledged] = useState(false)
  const [route, setRoute] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    getLocations()
      .then(setLocations)
      .catch(() => setError('Could not load the supported locations. Is the backend running?'))
  }, [])

  function clearResults() {
    setParsed(null)
    setRoute(null)
    setAcknowledged(false)
    setError('')
  }

  function change(setter) {
    return (value) => {
      setter(value)
      clearResults()
    }
  }

  async function handleReview() {
    const lines = deliveriesText
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
    if (lines.length === 0) {
      setError('Enter at least one delivery address.')
      return
    }
    if (lines.length > MAX_DELIVERIES) {
      setError(`A maximum of ${MAX_DELIVERIES} deliveries is supported.`)
      return
    }
    setLoading(true)
    clearResults()
    try {
      const result = await parseDeliveries({
        deliveries: lines.map((text, index) => ({ id: `D${index + 1}`, text })),
        instructions: instructions.trim(),
      })
      setParsed(result)
    } catch (problem) {
      setError(problem.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleOptimize() {
    setLoading(true)
    setError('')
    setRoute(null)
    try {
      const result = await optimizeRoute({
        depot_id: depotId,
        return_to_depot: returnToDepot,
        deliveries: parsed.deliveries.map((item) => ({
          id: item.id,
          location_id: item.location_id,
        })),
      })
      setRoute(result)
    } catch (problem) {
      setError(problem.message)
    } finally {
      setLoading(false)
    }
  }

  const allResolved = parsed !== null && parsed.deliveries.every((item) => item.location_id)
  const notesDone = parsed !== null && (parsed.clarifications.length === 0 || acknowledged)
  const canOptimize = allResolved && notesDone
  const depot = locations.find((item) => item.id === depotId)

  return (
    <main className="page">
      <h1>LogiTrack</h1>
      <p className="scope">
        One delivery van, one depot and up to 8 stops. Only a catalogue of approximate demo
        locations in Hyderabad is supported. No live traffic, time windows or vehicle capacity.
      </p>

      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}

      <div className="layout">
        <div className="column">
          <DeliveryForm
            locations={locations}
            depotId={depotId}
            deliveriesText={deliveriesText}
            instructions={instructions}
            returnToDepot={returnToDepot}
            loading={loading}
            onDepotChange={change(setDepotId)}
            onDeliveriesChange={change(setDeliveriesText)}
            onInstructionsChange={change(setInstructions)}
            onReturnChange={change(setReturnToDepot)}
            onLoadExample={() => {
              setDeliveriesText(EXAMPLE)
              clearResults()
            }}
            onReview={handleReview}
          />
          {parsed && (
            <AddressReview
              parsed={parsed}
              acknowledged={acknowledged}
              canOptimize={canOptimize}
              loading={loading}
              onAcknowledge={setAcknowledged}
              onOptimize={handleOptimize}
            />
          )}
        </div>
        <div className="column">
          {route && parsed && (
            <RouteResults
              route={route}
              depotName={depot ? depot.name : depotId}
              parsed={parsed}
            />
          )}
        </div>
      </div>
    </main>
  )
}
