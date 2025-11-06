import React, { useState } from 'react'
import DrawingCanvas from './components/DrawingCanvas.jsx'
import ImageDisplay from './components/ImageDisplay.jsx'
import './App.css'

function App() {
  // State management
  const [prompt, setPrompt] = useState('')
  const [generatedImage, setGeneratedImage] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [canvasRef, setCanvasRef] = useState(null)

  // Handle form submission
  const handleGenerate = async () => {
    if (!canvasRef) {
      setError('Canvas not ready. Please try again.')
      return
    }

    // Get the canvas as a blob
    canvasRef.toBlob(async (blob) => {
      if (!blob) {
        setError('Failed to export canvas. Please draw something first.')
        return
      }

      setLoading(true)
      setError(null)
      setGeneratedImage(null)

      try {
        // Create form data to send to backend
        const formData = new FormData()
        formData.append('file', blob, 'sketch.png')
        formData.append('prompt', prompt)

        // Send request to backend
        const response = await fetch('http://localhost:8000/generate', {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`)
        }

        const data = await response.json()
        
        // Set the generated image (base64 encoded)
        setGeneratedImage(data.image)
        
      } catch (err) {
        console.error('Error generating image:', err)
        setError(err.message || 'Failed to generate image. Make sure the backend is running.')
      } finally {
        setLoading(false)
      }
    }, 'image/png')
  }

  return (
    <div className="app">
      <header className="header">
        <h1>✨ Sketch to Image AI</h1>
        <p>Draw something and bring it to life!</p>
      </header>

      <div className="container">
        {/* Left side - Drawing Canvas */}
        <div className="panel canvas-panel">
          <h2>🎨 Draw Your Sketch</h2>
          <DrawingCanvas onCanvasReady={setCanvasRef} />
          
          {/* Prompt input */}
          <div className="prompt-section">
            <label htmlFor="prompt">💬 Optional Prompt (describe what you want):</label>
            <input
              id="prompt"
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g., realistic photo, sunset lighting, detailed..."
              className="prompt-input"
              disabled={loading}
            />
          </div>

          {/* Generate button */}
          <button 
            className="generate-button"
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? '⏳ Generating...' : '🚀 Generate Image'}
          </button>

          {/* Error message */}
          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* Right side - Generated Image */}
        <div className="panel result-panel">
          <h2>🖼️ Generated Result</h2>
          <ImageDisplay 
            image={generatedImage}
            loading={loading}
          />
        </div>
      </div>

      <footer className="footer">
        <p>Powered by Stable Diffusion + ControlNet | Running on your Mac M3 🚀</p>
      </footer>
    </div>
  )
}

export default App

