# ✨ Sketch-to-Image AI

A full-stack web application that transforms simple sketches into realistic images using Stable Diffusion with ControlNet, running entirely on your local machine.

![Demo](https://img.shields.io/badge/Status-Fully_Functional-success)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![React](https://img.shields.io/badge/React-18.2-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688)

## 🎯 Overview

Draw a simple sketch on the canvas, optionally add a text prompt, and watch as AI generates a photorealistic image based on your drawing. The entire pipeline runs locally on Apple Silicon (M1/M2/M3) Macs, with no external API calls or subscriptions required.

**Example:**
- **Input:** Simple sketch of stars, barn, and cow
- **Prompt:** "A farm at night with a barn and a cow and stars"
- **Output:** Photorealistic image of a red barn under starry sky with Milky Way, green grass, and a cow

## 🏗️ Architecture

### Tech Stack

**Backend (Python):**
- **FastAPI** - Modern async web framework
- **PyTorch** - Deep learning framework with Apple Silicon (MPS) support
- **Diffusers** - Hugging Face's Stable Diffusion implementation
- **ControlNet** - Guides image generation using sketch structure
- **controlnet-aux** - HED edge detection preprocessing

**Frontend (React + Vite):**
- **React 18** - UI framework with hooks
- **Vite** - Lightning-fast dev server and build tool
- **HTML5 Canvas API** - Drawing interface
- **Fetch API** - HTTP requests to backend

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  React Frontend (localhost:5173)                     │   │
│  │  • Drawing Canvas (HTML5)                            │   │
│  │  • User draws sketch                                 │   │
│  │  • Optional text prompt input                        │   │
│  │  • Click "Generate"                                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ HTTP POST /generate
                          │ (FormData: sketch.png + prompt)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (localhost:8000)                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. Receive sketch image + prompt                    │   │
│  │  2. Preprocess: Resize to 512x512                    │   │
│  │  3. Apply HED edge detection                         │   │
│  │  4. Load Stable Diffusion + ControlNet models        │   │
│  │  5. Run inference (~10-30 seconds on M3)             │   │
│  │  6. Return base64-encoded generated image            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ GPU Acceleration
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Apple Silicon (M1/M2/M3)                        │
│  • MPS (Metal Performance Shaders) backend                   │
│  • ~5GB model weights cached in ~/.cache/huggingface        │
│  • 16-core Neural Engine acceleration                        │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Implementation Strategy

### 1. Model Selection
- **Base Model:** `runwayml/stable-diffusion-v1-5` - Proven, well-optimized for various hardware
- **ControlNet:** `lllyasviel/sd-controlnet-hed` - HED (Holistically-Nested Edge Detection) variant
  - Excellent at preserving sketch structure while allowing creative freedom
  - Balances control vs. creativity better than canny or depth models

### 2. Backend Pipeline

**Image Preprocessing:**
```python
1. Input sketch (any size) → Convert to RGB
2. Resize to 512x512 (SD v1.5 optimal resolution)
3. Apply HED edge detection to extract structural edges
4. Feed processed edges to ControlNet
```

**Inference Configuration:**
- **Inference Steps:** 20 (balance between speed and quality)
- **Guidance Scale:** 7.5 (moderate prompt adherence)
- **MPS Device:** Apple Silicon GPU acceleration
- **Float16:** Reduced memory usage without quality loss

**Performance Optimizations:**
- Model loaded once at startup (not per-request)
- Cached in memory for instant subsequent generations
- NumPy < 2.0 for PyTorch compatibility
- Async FastAPI endpoints for non-blocking I/O

### 3. Frontend Architecture

**Component Structure:**
```
App.jsx (Main orchestrator)
  ├─ DrawingCanvas.jsx (Canvas drawing logic)
  │    ├─ Mouse event handlers
  │    ├─ Canvas context management
  │    └─ Clear/Export functionality
  │
  └─ ImageDisplay.jsx (Result rendering)
       ├─ Loading state (spinner)
       ├─ Placeholder state
       └─ Image display (base64 decode)
```

**State Management:**
- **React Hooks (useState)** for local component state
- **Refs (useRef)** for canvas element access
- **Props** for parent-child communication
- No external state library needed (simple app)

**Data Flow:**
```
User draws → Canvas stores pixels → Export to Blob →
FormData → POST to backend → Await response →
Base64 image → Display in <img> tag
```

### 4. API Design

**Endpoint:** `POST /generate`

**Request:**
```
Content-Type: multipart/form-data
- file: sketch.png (binary)
- prompt: "descriptive text" (string, optional)
```

**Response:**
```json
{
  "image": "base64_encoded_png_string",
  "generation_time": 12.34,
  "message": "Image generated successfully"
}
```

**CORS Configuration:**
- Allows `localhost:5173` and `localhost:3000`
- Necessary for frontend-backend communication during development

## 📋 Features

✅ **Drawing Canvas**
- Freehand drawing with mouse
- Crosshair cursor for precision
- Clear canvas button
- Auto-exports to PNG

✅ **AI Image Generation**
- Stable Diffusion v1.5 with ControlNet
- Optional text prompts for guidance
- Preserves sketch structure
- Photorealistic output

✅ **User Experience**
- Real-time drawing feedback
- Loading spinner with progress indicator
- Error handling and user-friendly messages
- Responsive layout (works on different screen sizes)

✅ **Performance**
- Self-hosted (no API costs)
- Apple Silicon GPU acceleration
- 10-30 second generation time
- Models cached locally

## 🛠️ Setup Instructions

### Prerequisites

- **macOS** with Apple Silicon (M1/M2/M3)
- **Python 3.11+**
- **Node.js 18+** and npm
- **~10GB free disk space** (for model weights)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (takes 3-5 minutes)
pip3 install -r requirements.txt

# Start the server
python3 app.py
```

Backend will run on `http://localhost:8000`

**First run:** Models will auto-download to `~/.cache/huggingface/` (~5GB)

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on `http://localhost:5173`

### Testing

Open browser to `http://localhost:5173`

1. Draw a simple sketch (house, face, animal, etc.)
2. Optionally add a text prompt (e.g., "realistic photo, detailed")
3. Click "🚀 Generate Image"
4. Wait 10-30 seconds
5. View the AI-generated result!

## 📁 Project Structure

```
sketch-to-image-ai/
├── backend/
│   ├── app.py                 # FastAPI server + endpoints
│   ├── model_handler.py       # AI model loading & inference
│   ├── requirements.txt       # Python dependencies
│   └── venv/                  # Virtual environment (gitignored)
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx           # React entry point
│   │   ├── App.jsx            # Main app component
│   │   ├── App.css            # Styling
│   │   └── components/
│   │       ├── DrawingCanvas.jsx       # Canvas drawing
│   │       ├── DrawingCanvas.css
│   │       ├── ImageDisplay.jsx        # Result display
│   │       └── ImageDisplay.css
│   ├── index.html             # HTML entry point
│   ├── package.json           # npm dependencies
│   └── node_modules/          # npm packages (gitignored)
│
├── .gitignore                 # Git exclusions
└── README.md                  # This file
```

## 🎨 Usage Tips

**For Best Results:**
- Draw clear, simple outlines (not shaded/filled)
- Use bold strokes for main objects
- Add descriptive prompts ("realistic", "detailed", "sunset lighting")
- Experiment with different sketch styles

**Example Prompts:**
- "realistic photo, high quality, detailed"
- "oil painting, impressionist style"
- "digital art, concept art, artstation"
- "sunset lighting, golden hour"
- "black and white photography"

## 🔧 Configuration

### Backend Configuration

Edit `backend/model_handler.py`:

```python
# Adjust generation quality
num_inference_steps=20    # Higher = better quality, slower (10-50)
guidance_scale=7.5        # Higher = closer to prompt (1-20)

# Change models
model_id = "runwayml/stable-diffusion-v1-5"
controlnet_model = "lllyasviel/sd-controlnet-hed"
```

### Frontend Configuration

Edit `frontend/src/App.jsx`:

```javascript
// Backend URL
const response = await fetch('http://localhost:8000/generate', {
  // Change if backend runs on different port
})
```

## 🐛 Troubleshooting

**Issue:** "ModuleNotFoundError: No module named 'fastapi'"
- **Solution:** Activate virtual environment: `source venv/bin/activate`

**Issue:** "React is not defined"
- **Solution:** Ensure all component files import React: `import React from 'react'`

**Issue:** "CORS error" in browser console
- **Solution:** Ensure backend is running and CORS is configured for your frontend port

**Issue:** Generation takes too long (>60 seconds)
- **Solution:** Reduce `num_inference_steps` to 10-15 in `model_handler.py`

**Issue:** Out of memory errors
- **Solution:** Close other apps, or reduce image resolution to 256x256

## 📊 Performance Benchmarks

**Hardware:** M3 MacBook Pro (16GB RAM)

| Task | Time |
|------|------|
| Model loading (first time) | ~30 seconds |
| Model loading (cached) | Instant |
| Image generation | 10-30 seconds |
| Model download (first run) | 5-10 minutes |

**Memory Usage:**
- Backend idle: ~500MB
- Backend with models loaded: ~5GB
- Frontend: ~100MB

## 🔐 Privacy & Security

✅ **Completely Local**
- No data sent to external servers
- No API keys required
- No usage tracking or analytics
- Your sketches and images stay on your machine

✅ **Open Source**
- All code visible and auditable
- Models from Hugging Face (open source)

## 🚧 Future Enhancements

Potential improvements:
- [ ] Multiple ControlNet models (canny, depth, pose)
- [ ] Adjustable brush size and color
- [ ] Image-to-image mode (upload reference)
- [ ] Gallery to save/view previous generations
- [ ] Export generated images as PNG/JPG
- [ ] Real-time generation progress bar
- [ ] Support for Stable Diffusion XL
- [ ] Mobile touch support

## 📚 Technical Resources

**Papers:**
- [Stable Diffusion](https://arxiv.org/abs/2112.10752) (Rombach et al., 2022)
- [ControlNet](https://arxiv.org/abs/2302.05543) (Zhang et al., 2023)
- [HED Edge Detection](https://arxiv.org/abs/1504.06375) (Xie & Tu, 2015)

**Documentation:**
- [Hugging Face Diffusers](https://huggingface.co/docs/diffusers)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Stable Diffusion** by Stability AI
- **ControlNet** by Lvmin Zhang
- **Hugging Face** for model hosting and diffusers library


---

**Built with ❤️ for creative experimentation**

*Self-hosted AI on Apple Silicon - No cloud, no cost, no limits.*

