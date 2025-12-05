import modal
import os
import sys
from modal import asgi_app
from dotenv import load_dotenv

load_dotenv()

app = modal.App("multi-model-env-backend")

# --------- ACTIVATE ZIP ENV ----------
def activate_env(env_dir): 
    for folder in os.listdir(env_dir):
        candidate = os.path.join(env_dir, folder)
        if os.path.isdir(candidate) and "lib" in os.listdir(candidate):
            lib_path = os.path.join(candidate, "lib")
            for pyfolder in os.listdir(lib_path):
                if pyfolder.startswith("python"):
                    site_packages = os.path.join(lib_path, pyfolder, "site-packages")
                    if os.path.exists(site_packages):
                        sys.path.insert(0, site_packages)
                        return site_packages
    raise RuntimeError(f"❌ Could not locate site-packages inside env: {env_dir}")

backend_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "libgl1",
        "libglib2.0-0"
    )
    .pip_install(
        "annotated-doc==0.0.4",
        "annotated-types==0.7.0",
        "anyio==4.11.0",
        "bcrypt==4.0.1",
        "click==8.3.1",
        "colorama==0.4.6",
        "dnspython==2.8.0",
        "email-validator==2.3.0",
        "fastapi==0.121.3",
        "h11==0.16.0",
        "idna==3.11",
        "motor==3.7.1",
        "passlib[bcrypt]==1.7.4",
        "pyasn1==0.6.1",
        "pycparser==2.23",
        "pydantic==2.12.4",
        "pydantic_core==2.41.5",
        "PyJWT==2.10.1",
        "pymongo==4.15.4",
        "python-dotenv==1.2.1",
        "python-multipart==0.0.20",
        "six==1.17.0",
        "sniffio==1.3.1",
        "starlette==0.50.0",
        "typing_extensions==4.15.0",
        "typing-inspection==0.4.2",
        "uvicorn==0.38.0",
        "openai",
        "requests",
        "pillow",
        "numpy<2",
        "torch",
        "transformers",
        "peft",
        "opencv-python"
    )
    .add_local_dir("src", remote_path="/root/src")
)




# -------- ZIP MODEL ENV IMAGES ---------
caption_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("unzip")                         # <== ADD THIS
    .run_commands("mkdir -p /captioning_env")
    .add_local_file("captioning.zip", "/captioning.zip", copy=True)
    .run_commands("unzip /captioning.zip -d /captioning_env")
)



vqa_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("unzip")                         # <== ADD THIS
    .run_commands("mkdir -p /vqa_env")
    .add_local_file("vqa.zip", "/vqa.zip", copy=True)
    .run_commands("unzip /vqa.zip -d /vqa_env")
)


grounding_image = (
    modal.Image.from_registry("nvidia/cuda:12.1.0-runtime-ubuntu22.04")
    .apt_install(
        "software-properties-common",
        "unzip"
    )
    .run_commands(
        "add-apt-repository ppa:deadsnakes/ppa -y",
        "apt-get update",
        "apt-get install -y python3.10 python3.10-distutils python3.10-venv",
        "ln -sf /usr/bin/python3.10 /usr/bin/python"
    )
    .run_commands("mkdir -p /grounding_env")
    .add_local_file("grounding.zip", "/grounding.zip", copy=True)
    .run_commands("unzip -q /grounding.zip -d /grounding_env")
)


@app.function(
    image=caption_image,
    gpu="A100",
    timeout=300,
    memory=4096
)

def run_caption(image_path: str, max_tokens: int = 512, temperature: float = 0.7):
    """
    Generate caption using Florence-2 Caption Service
    
    Args:
        image_path: Path to image file
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Returns:
        {"caption": "Generated caption text"}
    """
    print(f"📝 Caption Service - Processing: {image_path}")
    
    # Activate caption environment
    activate_env("/captioning_env")
    
    # Import service from activated environment
    from src.services.florence2_caption_service import get_caption_service
    
    try:
        # Get caption service (singleton)
        service = get_caption_service()
        
        # Generate caption
        caption = service.generate_caption(
            image=image_path,
            max_new_tokens=max_tokens,
            temperature=temperature
        )
        
        print(f"✅ Caption generated: {caption[:100]}...")
        return {"caption": caption}
        
    except Exception as e:
        print(f"❌ Caption error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "caption": "Failed to generate caption"}


@app.function(
    image=vqa_image,
    gpu="A100",
    timeout=300,
    memory=4096
)

def run_vqa(image_path: str, question: str, max_tokens: int = 128, temperature: float = 0.7):
    """
    Answer question using Florence-2 VQA Service
    
    Args:
        image_path: Path to image file
        question: Question to answer
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Returns:
        {"answer": "Answer text"}
    """
    print(f"❓ VQA Service - Question: {question}")
    
    # Activate VQA environment
    activate_env("/vqa_env")
    
    # Import service from activated environment
    from src.services.florence2_vqa_service import get_vqa_service
    
    try:
        # Get VQA service (singleton)
        service = get_vqa_service()
        
        # Answer question
        answer = service.answer_question(
            image=image_path,
            question=question,
            max_new_tokens=max_tokens,
            temperature=temperature
        )
        
        print(f"✅ Answer: {answer}")
        return {"answer": answer}
        
    except Exception as e:
        print(f"❌ VQA error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "answer": "Failed to answer question"}


@app.function(
    image=grounding_image,
    gpu="A100",  # Use A100 for grounding
    timeout=600,
    memory=16384
)
def run_grounding(image_path: str, query: str, max_boxes: int = 10):
    """
    Detect objects using GeoGround Service
    
    Args:
        image_path: Path to image file
        query: Natural language query
        max_boxes: Maximum boxes to return
        
    Returns:
        {"detections": [{"object_id": "1", "obbox": [...]}]}
    """
    print(f"🎯 Grounding Service - Query: {query}")
    
    # Activate grounding environment
    activate_env("/grounding_env")
    
    # Import service from activated environment
    from src.services.grounding_service import get_grounding_service
    
    try:
        # Get grounding service (singleton)
        service = get_grounding_service()
        
        # Detect objects - returns List[Tuple[str, List[float]]]
        detections = service.detect_objects(
            image=image_path,
            query=query,
            max_boxes=max_boxes
        )
        
        # Format detections to match API response
        formatted_detections = [
            {
                "object_id": obj_id,
                "obbox": obbox
            }
            for obj_id, obbox in detections
        ]
        
        print(f"✅ Detected {len(formatted_detections)} objects")
        return {"detections": formatted_detections}
        
    except Exception as e:
        print(f"❌ Grounding error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "detections": []}


# ========================================================================================
# SIMPLE ROUTER ENDPOINT (For direct service calls)
# ========================================================================================

@app.function(image=backend_image)
@modal.fastapi_endpoint(method="POST")
def router(request: dict):
    """
    Simple router for individual service calls
    
    Request format:
    {
        "service": "caption" | "vqa" | "grounding",
        "image": "path/to/image.jpg",
        "query": "question or query text",  // For VQA and Grounding
        "max_tokens": 512,  // Optional
        "temperature": 0.7,  // Optional
        "max_boxes": 10  // Optional for grounding
    }
    
    Returns:
        Service-specific response
    """
    service = request.get("service")
    image = request.get("image")
    query = request.get("query", "")
    max_tokens = request.get("max_tokens", 512)
    temperature = request.get("temperature", 0.7)
    max_boxes = request.get("max_boxes", 10)
    
    print(f"\n🔀 Router - Service: {service}")
    
    if service == "caption":
        return run_caption.remote(image, max_tokens, temperature)
    
    elif service == "vqa":
        if not query:
            return {"error": "Query/question is required for VQA"}
        return run_vqa.remote(image, query, max_tokens, temperature)
    
    elif service == "grounding":
        if not query:
            return {"error": "Query is required for grounding"}
        return run_grounding.remote(image, query, max_boxes)
    
    else:
        return {
            "error": "Unknown service. Choose: caption / vqa / grounding",
            "available_services": ["caption", "vqa", "grounding"]
        }


# ========================================================================================
# FASTAPI BACKEND (Complete GeoNLI Evaluation)
# ========================================================================================

@app.function(
    image=backend_image,
    timeout=600,
    memory=2048
)
@modal.asgi_app()
def fastapi_backend():
    """
    Complete FastAPI backend with GeoNLI evaluation endpoint
    
    This hosts the full backend including:
    - Authentication
    - Session management
    - GeoNLI evaluation endpoint
    - All other API endpoints
    """
    print("🚀 Starting FastAPI backend...")
    
    # Set Modal environment flag
    os.environ["MODAL_ENV"] = "true"
    
    # Import FastAPI app
    from src.server import app as fastapi_app
    
    print("✅ FastAPI backend ready")
    return fastapi_app


# ========================================================================================
# HEALTH CHECK
# ========================================================================================

@app.function(image=backend_image)
@modal.fastapi_endpoint(method="GET")
def health():
    """Health check endpoint"""
    import torch
    
    return {
        "status": "healthy",
        "service": "GeoNLI Multi-Model Backend",
        "environment": "Modal",
        "cuda_available": torch.cuda.is_available(),
        "services": {
            "caption": "available",
            "vqa": "available",
            "grounding": "available (A100)"
        }
    }