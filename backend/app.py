"""
FastAPI Backend for Sketch-to-Image Generation
Provides HTTP endpoints for the React frontend to generate images from sketches
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import io
import base64
import time

# Import our model handler
from model_handler import generate_image, load_model

# Initialize FastAPI app
app = FastAPI(
    title="Sketch-to-Image API",
    description="Generate realistic images from sketches using Stable Diffusion + ControlNet",
    version="1.0.0"
)

# Configure CORS to allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative React port
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Helper function: Convert PIL Image to base64 string
def pil_to_base64(image: Image.Image) -> str:
    """
    Convert a PIL Image to base64 string for JSON transmission.
    
    Args:
        image: PIL Image object
        
    Returns:
        Base64 encoded string of the image
    """
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return img_base64


# Helper function: Convert uploaded file to PIL Image
async def upload_to_pil(file: UploadFile) -> Image.Image:
    """
    Convert FastAPI UploadFile to PIL Image.
    
    Args:
        file: Uploaded file from FastAPI
        
    Returns:
        PIL Image object
    """
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    return image


@app.on_event("startup")
async def startup_event():
    """
    Load models when server starts (optional - models load on first request if not done here).
    This can make the first request faster.
    """
    print("🚀 Server starting up...")
    print("💡 Models will load on first generation request")
    print("✓ Server ready!")


@app.get("/")
def root():
    """
    Root endpoint - Health check.
    Returns server status and basic info.
    """
    return {
        "status": "running",
        "message": "Sketch-to-Image API is operational",
        "endpoints": {
            "health": "/health",
            "generate": "/generate (POST)"
        }
    }


@app.get("/health")
def health_check():
    """
    Detailed health check endpoint.
    Returns system status and model information.
    """
    import torch
    
    return {
        "status": "healthy",
        "gpu_available": torch.backends.mps.is_available(),
        "gpu_type": "MPS (Metal)" if torch.backends.mps.is_available() else "CPU",
        "endpoints_active": True
    }


@app.post("/generate")
async def generate_endpoint(
    file: UploadFile = File(..., description="Sketch image file (PNG/JPG)"),
    prompt: str = Form("", description="Optional text prompt to guide generation")
):
    """
    Main generation endpoint.
    
    Accepts:
        - file: Sketch image uploaded from frontend
        - prompt: Optional text description (e.g., "realistic photo, detailed")
        
    Returns:
        JSON with generated image as base64 and metadata
    """
    
    start_time = time.time()
    
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Please upload an image."
            )
        
        print(f"📥 Received sketch: {file.filename}")
        print(f"📝 Prompt: '{prompt}'" if prompt else "📝 No prompt provided")
        
        # Convert uploaded file to PIL Image
        sketch_image = await upload_to_pil(file)
        print(f"✓ Image loaded: {sketch_image.size}")
        
        # Generate image using our model handler
        print("🎨 Generating image...")
        generated_image = generate_image(
            sketch_image=sketch_image,
            prompt=prompt if prompt else "high quality, detailed, realistic",
            num_inference_steps=20,
            guidance_scale=7.5
        )
        print("✓ Generation complete!")
        
        # Convert generated image to base64 for JSON response
        image_base64 = pil_to_base64(generated_image)
        
        generation_time = time.time() - start_time
        print(f"⏱️  Total time: {generation_time:.2f}s")
        
        # Return success response
        return JSONResponse(content={
            "success": True,
            "image": image_base64,
            "prompt": prompt,
            "generation_time": round(generation_time, 2),
            "image_size": generated_image.size,
            "message": "Image generated successfully"
        })
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
        
    except Exception as e:
        # Handle any other errors
        print(f"❌ Error during generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )


@app.get("/models/status")
def model_status():
    """
    Check if models are loaded.
    Useful for frontend to show loading states.
    """
    from model_handler import pipeline
    
    return {
        "models_loaded": pipeline is not None,
        "status": "ready" if pipeline is not None else "not_loaded"
    }


# Run the server
if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("🚀 Starting Sketch-to-Image API Server")
    print("="*60)
    print("📍 Server: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("🎨 Ready to generate images!")
    print("="*60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",  # Listen on all interfaces
        port=8000,
        log_level="info"
    )

