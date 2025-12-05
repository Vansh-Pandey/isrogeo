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

# --------- BACKEND IMAGE (FASTAPI) ----------
backend_image = (
    modal.Image.debian_slim(python_version="3.11")
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
        "openai"
    )
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




# ---------- MODEL FUNCTIONS -------------
@app.function(image=caption_image)
def run_caption(image_path: str):
    activate_env("/captioning_env")
    from src.services.florence2_caption_service import get_caption_service
    return get_caption_service().generate_caption(image_path)

@app.function(image=vqa_image)
def run_vqa(image_path: str, question: str):
    activate_env("/vqa_env")
    from src.services.florence2_vqa_service import get_vqa_service
    return get_vqa_service().answer_question(image_path, question)

@app.function(image=grounding_image, gpu="A10G")
def run_grounding(image_path: str, query: str):
    activate_env("/grounding_env")
    from src.services.grounding_service import get_grounding_service
    return get_grounding_service().detect_objects(image_path, query)

# ---------- SIMPLE ROUTER (OPTIONAL) -------------
@app.function(image=backend_image)
@modal.fastapi_endpoint(method="POST")
def router(request: dict):
    service = request.get("service")
    image = request.get("image")
    query = request.get("query")

    if service == "caption":
        return run_caption.remote(image)
    elif service == "vqa":
        return run_vqa.remote(image, query)
    elif service == "grounding":
        return run_grounding.remote(image, query)
    else:
        return {"error": "Unknown service. Choose: caption / vqa / grounding"}


# ---------- RUN BACKEND FASTAPI VIA MODAL ----------
@app.function(image=backend_image)
@asgi_app()
def backend():
    from src.server import app as fastapi_app
    return fastapi_app
