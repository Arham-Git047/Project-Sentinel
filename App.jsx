import { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'
import './App.css'

function App() {
  const [backendStatus, setBackendStatus] = useState('checking')

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch('http://localhost:8000/health')
        if (response.ok) {
          setBackendStatus('connected')
        } else {
          setBackendStatus('error')
        }
      } catch (error) {
        setBackendStatus('disconnected')
      }
    }

    checkBackend()
    const interval = setInterval(checkBackend, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="app">
      {backendStatus === 'disconnected' && (
        <div className="backend-warning">
          ⚠️ Backend not conected. Please start backend at http://localhost:8000
        </div>
      )}
      <Dashboard />
    </div>
  )
}

export default App
