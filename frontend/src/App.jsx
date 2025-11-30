import React from 'react'
import ChatInterface from './components/ChatInterface'

function App() {
  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4">
      <div className="w-full max-w-4xl h-[90vh] glass rounded-2xl shadow-2xl overflow-hidden">
        <ChatInterface />
      </div>
    </div>
  )
}

export default App
