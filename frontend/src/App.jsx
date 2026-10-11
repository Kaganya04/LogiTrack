import { useState } from 'react'

export default function App() {
  const [message, setMessage] = useState('Not checked')

  async function check() {
    try {
      const response = await fetch('/api/health')
      if (!response.ok) throw new Error('Backend unavailable')
      const data = await response.json()
      setMessage(data.status)
    } catch {
      setMessage('Cannot reach backend. Check port 8000.')
    }
  }

  return (
    <>
      <button onClick={check}>Check backend</button>
      <p>{message}</p>
    </>
  )
}