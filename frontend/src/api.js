function describeError(data, status) {
  const detail = data && data.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((item) => item.msg).join('; ')
  }
  return `The request failed (status ${status}).`
}

async function send(url, options) {
  let response
  try {
    response = await fetch(url, options)
  } catch {
    throw new Error('Cannot reach the server. Check that the backend is running.')
  }
  let data
  try {
    data = await response.json()
  } catch {
    data = null
  }
  if (!response.ok) {
    throw new Error(describeError(data, response.status))
  }
  return data
}

function post(url, payload) {
  return send(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export const getLocations = () => send('/api/locations')
export const parseDeliveries = (payload) => post('/api/parse', payload)
export const optimizeRoute = (payload) => post('/api/optimize', payload)
