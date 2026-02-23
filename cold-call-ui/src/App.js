import React, { useState } from 'react';
import './App.css';

function App() {
  const [loading, setLoading] = useState(false);
  const [outcome, setOutcome] = useState(null);
  const [status, setStatus] = useState('Idle');

  const startSimulation = async () => {
    setLoading(true);
    setOutcome(null);
    setStatus('Bot is calling...');

    try {
      const response = await fetch('http://localhost:8000/run-bot', {
        method: 'POST',
      });
      const data = await response.json();
      setOutcome(data);
      setStatus('Call Finished');
    } catch (error) {
      console.error("Error running simulation:", error);
      setStatus('Error connecting to server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>CloudSave AI Dashboard</h1>
        <div className="status-badge">{status}</div>

        <button 
          className={`run-button ${loading ? 'active' : ''}`} 
          onClick={startSimulation} 
          disabled={loading}
        >
          {loading ? 'Conversation in Progress...' : 'Start Cold Call Simulation'}
        </button>

        {outcome && (
          <div className="outcome-container">
            <h2>Call Outcome</h2>
            <div className="card">
              <p><strong>Qualified:</strong> {outcome.qualified ? '✅ Yes' : '❌ No'}</p>
              <p><strong>Reasoning:</strong> {outcome.reasoning}</p>
              <p><strong>Next Step:</strong> <span className="next-step">{outcome.next_step}</span></p>
            </div>
            <pre className="json-output">{JSON.stringify(outcome, null, 2)}</pre>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;