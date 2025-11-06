import React, { useRef, useEffect, useState } from 'react'
import './DrawingCanvas.css'

function DrawingCanvas({ onCanvasReady }) {
  const canvasRef = useRef(null)
  const [isDrawing, setIsDrawing] = useState(false)
  const [context, setContext] = useState(null)

  // Initialize canvas
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    
    // Set canvas size
    canvas.width = 512
    canvas.height = 512
    
    // White background
    ctx.fillStyle = 'white'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    // Drawing settings
    ctx.strokeStyle = 'black'
    ctx.lineWidth = 3
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
    
    setContext(ctx)
    
    // Send canvas reference to parent component
    if (onCanvasReady) {
      onCanvasReady(canvas)
    }
  }, [onCanvasReady])

  // Start drawing
  const startDrawing = (e) => {
    if (!context) return
    
    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    
    context.beginPath()
    context.moveTo(x, y)
    setIsDrawing(true)
  }

  // Draw
  const draw = (e) => {
    if (!isDrawing || !context) return
    
    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    
    context.lineTo(x, y)
    context.stroke()
  }

  // Stop drawing
  const stopDrawing = () => {
    if (!context) return
    context.closePath()
    setIsDrawing(false)
  }

  // Clear canvas
  const clearCanvas = () => {
    if (!context || !canvasRef.current) return
    
    const canvas = canvasRef.current
    context.fillStyle = 'white'
    context.fillRect(0, 0, canvas.width, canvas.height)
  }

  return (
    <div className="drawing-canvas-container">
      <canvas
        ref={canvasRef}
        className="drawing-canvas"
        onMouseDown={startDrawing}
        onMouseMove={draw}
        onMouseUp={stopDrawing}
        onMouseLeave={stopDrawing}
      />
      <button 
        className="clear-button"
        onClick={clearCanvas}
      >
        🗑️ Clear Canvas
      </button>
    </div>
  )
}

export default DrawingCanvas

