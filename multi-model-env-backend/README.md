# GeoNLI Backend - Complete Setup Guide

> AI-powered satellite image analysis platform with FastAPI backend supporting Caption, VQA, and Grounding services

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121.3-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4%2B-green.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Running Locally](#running-locally)
7. [API Documentation](#api-documentation)
8. [Modal Deployment](#modal-deployment)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)
11. [Project Structure](#project-structure)
12. [Contributing](#contributing)

---

## 🎯 Overview

The GeoNLI backend is a FastAPI application that provides AI-powered satellite image analysis through three specialized AI services:

### **Core Services**

| Service | Model | Purpose | Output Format |
|---------|-------|---------|---------------|
| **Caption** | Florence-2 | Generate detailed descriptions | Text caption |
| **VQA** | Florence-2 | Answer questions about images | Text answers |
| **Grounding** | GeoGround + YOLO | Detect objects with oriented bounding boxes | 8-point OBB coordinates |

### **Key Features**

✅ RESTful API with FastAPI  
✅ Multi-model AI inference pipeline  
✅ MongoDB database integration  
✅ JWT-based authentication  
✅ CORS-enabled for frontend  
✅ Local & Cloud deployment options  
✅ GPU acceleration support  
✅ Comprehensive error handling  

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GeoNLI Backend                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   FastAPI    │  │   MongoDB    │  │     JWT      │    │
│  │   Server     │──│   Database   │──│     Auth     │    │
│  └──────┬───────┘  └──────────────┘  └──────────────┘    │
│         │                                                   │
│  ┌──────▼──────────────────────────────────────────────┐  │
│  │           GeoNLI Controller                         │  │
│  │  (Orchestrates AI services for evaluation)         │  │
│  └──────┬──────────────────────────────────────────────┘  │
│         │                                                   │
│  ┌──────▼──────────┬──────────────┬──────────────────┐   │
│  │                 │              │                   │   │
│  │  Caption        │  VQA         │  Grounding       │   │
│  │  Service        │  Service     │  Service         │   │
│  │  (Florence-2)   │  (Florence-2)│  (YOLO+GeoGround)│   │
│  │                 │              │                   │   │
│  └─────────────────┴──────────────┴──────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Request Flow:**
```
User → FastAPI Route → Controller → AI Service → Model → Response
```

---

## 🔧 Prerequisites

### **Required Software**

| Software | Version | Purpose | Installation |
|----------|---------|---------|--------------|
| **Python** | 3.10 or 3.11 | Backend runtime | [Download](https://www.python.org/downloads/) |
| **MongoDB** | 4.4+ | Database | [Atlas](https://www.mongodb.com/cloud/atlas) or [Local](https://www.mongodb.com/try/download/community) |
| **Git** | Latest | Version control | [Download](https://git-scm.com/downloads) |
| **CUDA** | 12.1+ (optional) | GPU acceleration | [Download](https://developer.nvidia.com/cuda-downloads) |

### **Hardware Requirements**

**Minimum (CPU-only):**
- 16GB RAM
- 50GB storage
- 4 CPU cores

**Recommended (with GPU):**
- 32GB RAM
- 100GB storage
- NVIDIA GPU with 16GB+ VRAM (RTX 3090, A5000, A100)
- 8 CPU cores

### **Required Accounts**

1. **MongoDB Atlas** (free tier) - [Sign up](https://www.mongodb.com/cloud/atlas)
2. **Modal** (for deployment) - [Sign up](https://modal.com) *(optional)*
3. **Google Account** - For downloading model environments

---

## 📥 Installation

### **Step 1: Clone Repository**

```bash
# Clone your repository
git clone https://github.com/yourusername/geonli-backend.git
cd geonli-backend/multi-model-env-backend

# Or initialize new project
mkdir -p multi-model-env-backend
cd multi-model-env-backend
```

---

### **Step 2: Download Model Environments (if not already in the zip)**

The AI model environments are packaged as zip files hosted on Google Drive. Download all three files:

#### **Download Links**

| Environment | Size | Description | Download Link |
|-------------|------|-------------|---------------|
| **captioning.zip** | ~2-3GB | Florence-2 caption model + dependencies | [PASTE_YOUR_GOOGLE_DRIVE_LINK_1] |
| **vqa.zip** | ~2-3GB | Florence-2 VQA model + dependencies | [PASTE_YOUR_GOOGLE_DRIVE_LINK_2] |
| **grounding.zip** | ~15-20GB | GeoGround + YOLO models + dependencies | [PASTE_YOUR_GOOGLE_DRIVE_LINK_3] |

#### **Method 1: Using `gdown` (Recommended)**

```bash
# Install gdown
pip install gdown

# Download captioning environment
gdown <YOUR_GOOGLE_DRIVE_LINK_1>

# Download VQA environment
gdown <YOUR_GOOGLE_DRIVE_LINK_2>

# Download grounding environment
gdown <YOUR_GOOGLE_DRIVE_LINK_3>
```

#### **Method 2: Manual Download**

1. Click each Google Drive link
2. Download to your computer
3. Move all three zip files to `multi-model-env-backend/`

#### **Verify Downloads**

```bash
# Check files are present
ls -lh *.zip

# Expected output:
# captioning.zip  (~2-3GB)
# vqa.zip        (~2-3GB)
# grounding.zip  (~15-20GB)
```

---

### **Step 3: Create Virtual Environment**

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify Python version
python --version
# Should show: Python 3.11.x
```

---

### **Step 4: Install Backend Dependencies**

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
# Should show: fastapi==0.121.3
```

**Core Dependencies:**
- `fastapi==0.121.3` - Web framework
- `uvicorn==0.38.0` - ASGI server
- `motor==3.7.1` - Async MongoDB driver
- `pymongo==4.15.4` - MongoDB driver
- `PyJWT==2.10.1` - JWT authentication
- `passlib[bcrypt]==1.7.4` - Password hashing
- `python-dotenv==1.2.1` - Environment variables 

---

### **Step 5: Extract Model Environments**

**For Local Development:**

```bash
# Extract caption environment
mkdir -p captioning_env
unzip captioning.zip -d captioning_env/

# Extract VQA environment
mkdir -p vqa_env
unzip vqa.zip -d vqa_env/

# Extract grounding environment
mkdir -p grounding_env
unzip grounding.zip -d grounding_env/

# Verify extraction
ls -la captioning_env/ vqa_env/ grounding_env/
```

**Note:** For Modal deployment, you **DON'T** need to extract the zip files. Modal will handle them automatically.

---

## ⚙️ Configuration

### **Step 1: Create `.env` File**

```bash
# Create .env file in project root
cd multi-model-env-backend
touch .env
```

---

### **Step 2: Add Environment Variables**

Open `.env` and add the following:

```bash
# ====================================================================
# DATABASE CONFIGURATION
# ====================================================================

# MongoDB Connection String
# Get this from MongoDB Atlas: Clusters → Connect → Connect your application
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=geonli_db

# Collection names (default values - don't change unless needed)
USERS_COLLECTION=users
SESSIONS_COLLECTION=sessions
PROJECTS_COLLECTION=projects
MESSAGES_COLLECTION=messages
IMAGES_COLLECTION=images


# ====================================================================
# AUTHENTICATION
# ====================================================================

# JWT Secret Key (IMPORTANT: Generate a secure key!)
# Generate with: openssl rand -hex 32
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7


# ====================================================================
# SERVER CONFIGURATION
# ====================================================================

# Server host and port
HOST=0.0.0.0
PORT=8000
NODE_ENV=development

# Frontend URL for CORS
# Update this to match your frontend URL
FRONTEND_URL=http://localhost:5173


# ====================================================================
# AI MODEL CONFIGURATION (Local Development)
# ====================================================================

# Caption Model Paths
CAPTION_MODEL_PATH=./checkpoints/caption_model
MAX_CAPTION_TOKENS=512
CAPTION_TEMPERATURE=0.7

# VQA Model Paths
VQA_MODEL_PATH=./checkpoints/vqa_model
MAX_VQA_TOKENS=128
VQA_TEMPERATURE=0.7

# Grounding Model Paths
GROUNDING_MODEL_PATH=./models/geoground
GROUNDING_MODEL_BASE=./models/llava-base
GROUNDING_CONV_MODE=llava_v1
GROUNDING_MAX_BOXES=10

# YOLO Model Path
YOLO_MODEL_PATH=./training_output/vrsbench_v2_obb2/weights/best.pt

# Image Processing
IMAGE_DOWNLOAD_TIMEOUT=30

 


# ====================================================================
# MODAL DEPLOYMENT (Optional - for cloud deployment)
# ====================================================================

MODAL_ENV=false
MODAL_GPU=A100
```

---

### **Step 3: Set Up MongoDB**

#### **Option A: MongoDB Atlas (Recommended)**

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free account
3. Create a new cluster (M0 free tier)
4. Create a database user:
   - Database Access → Add New Database User
   - Set username and password
5. Whitelist your IP address:
   - Network Access → Add IP Address
   - Add `0.0.0.0/0` for development (allow from anywhere)
6. Get connection string:
   - Clusters → Connect → Connect your application
   - Copy the connection string
   - Replace `<password>` with your database user password
7. Update `MONGODB_URL` in `.env`

#### **Option B: Local MongoDB**

```bash
# Install MongoDB locally

# On Ubuntu/Debian:
sudo apt-get install mongodb-community

# On macOS:
brew install mongodb-community

# Start MongoDB service
sudo systemctl start mongodb

# Use local connection string in .env
MONGODB_URL=mongodb://localhost:27017
```

---

### **Step 4: Generate JWT Secret**

```bash
# Generate a secure JWT secret
openssl rand -hex 32

# Copy the output and paste it as JWT_SECRET in .env
```

Example output:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

Update `.env`:
```bash
JWT_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

---

## 🚀 Running Locally

### **Method 1: Direct Python Execution**

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Run the server
python -m uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
# 🚀 Starting GeoNLI Backend...
# 📍 Environment: Local
# ✅ Database initialized
```

---

### **Method 2: Using Python Script**

```bash
# The server.py has built-in run support
python src/server.py
```

---

### **Method 3: Development Script**

Create `start.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Starting GeoNLI Backend..."

# Activate virtual environment
source venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run server with auto-reload
uvicorn src.server:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info
```

Make executable and run:
```bash
chmod +x start.sh
./start.sh
```

---

### **Access the Application**

Once running, you can access:

| Endpoint | URL | Description |
|----------|-----|-------------|
| **API Root** | http://localhost:8000 | Welcome message |
| **Health Check** | http://localhost:8000/health | System status |
| **Swagger Docs** | http://localhost:8000/docs | Interactive API documentation |
| **ReDoc** | http://localhost:8000/redoc | Alternative API documentation |
| **GeoNLI Eval** | http://localhost:8000/geoNLI/eval | Main evaluation endpoint |

---

### **Verify Installation**

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "cuda_available": true,
  "gpu_count": 1,
  "gpu_name": "NVIDIA GeForce RTX 3090"
}

# Test GeoNLI health
curl http://localhost:8000/geoNLI/health

# Expected response:
{
  "status": "healthy",
  "service": "GeoNLI Evaluation",
  "version": "1.0.0"
}
```

---

## 📡 API Documentation

### **Authentication Endpoints**

#### **1. Signup**
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "fullName": "John Doe",
  "password": "password123"
}
```

**Response (201 Created):**
```json
{
  "_id": "60f7ff78f7762f1a20d8c4a7",
  "email": "user@example.com",
  "fullName": "John Doe",
  "profilePic": null,
  "createdAt": "2024-01-01T00:00:00Z"
}
```

#### **2. Login**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### **3. Check Auth**
```http
GET /api/auth/check
Cookie: jwt=<token>
```

#### **4. Logout**
```http
POST /api/auth/logout
Cookie: jwt=<token>
```

---

### **Session Endpoints**

#### **1. Create Session**
```http
POST /api/sessions
Cookie: jwt=<token>
Content-Type: application/json

{
  "name": "Analysis Session 1",
  "archived": false,
  "projectId": null
}
```

#### **2. Get All Sessions**
```http
GET /api/sessions
Cookie: jwt=<token>
```

#### **3. Update Session**
```http
PUT /api/sessions/{session_id}
Cookie: jwt=<token>
Content-Type: application/json

{
  "name": "Updated Name",
  "archived": true
}
```

#### **4. Delete Session**
```http
DELETE /api/sessions/{session_id}
Cookie: jwt=<token>
```

---

### **GeoNLI Evaluation Endpoint**

#### **Complete Evaluation**

```http
POST /geoNLI/eval
Content-Type: application/json

{
  "input_image": {
    "image_id": "sample1.png",
    "image_url": "https://bit.ly/4ouV45l",
    "metadata": {
      "width": 512,
      "height": 512,
      "spatial_resolution_m": 1.57
    }
  },
  "queries": {
    "caption_query": {
      "instruction": "Generate a detailed caption describing all visible elements"
    },
    "grounding_query": {
      "instruction": "Locate all storage tanks in the image"
    },
    "attribute_query": {
      "binary": {
        "instruction": "Are there any digits visible in the image?"
      },
      "numeric": {
        "instruction": "How many storage tanks are visible?"
      },
      "semantic": {
        "instruction": "What color are the storage tanks?"
      }
    }
  }
}
```

**Response (200 OK):**
```json
{
  "input_image": {
    "image_id": "sample1.png",
    "image_url": "https://bit.ly/4ouV45l",
    "metadata": {
      "width": 512,
      "height": 512,
      "spatial_resolution_m": 1.57
    }
  },
  "queries": {
    "caption_query": {
      "instruction": "Generate a detailed caption...",
      "response": "The satellite image shows an industrial area with multiple cylindrical storage tanks arranged in rows. The tanks appear to be white or light-colored with dark roofs..."
    },
    "grounding_query": {
      "instruction": "Locate all storage tanks...",
      "response": [
        {
          "object-id": "1",
          "obbox": [0.234, 0.123, 0.267, 0.145, 0.289, 0.178, 0.256, 0.156]
        },
        {
          "object-id": "2",
          "obbox": [0.456, 0.234, 0.489, 0.256, 0.511, 0.289, 0.478, 0.267]
        }
      ]
    },
    "attribute_query": {
      "binary": {
        "instruction": "Are there any digits visible?",
        "response": "Yes"
      },
      "numeric": {
        "instruction": "How many storage tanks?",
        "response": 8.0
      },
      "semantic": {
        "instruction": "What color are the tanks?",
        "response": "White with dark roofs"
      }
    }
  }
}
```

**Note:** The `obbox` format is 8-point normalized coordinates:
- `[x1, y1, x2, y2, x3, y3, x4, y4]`
- All values normalized to [0, 1] range
- Represents the four corners of an oriented bounding box

---

### **cURL Examples**

```bash
# Health check
curl http://localhost:8000/health

# Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "fullName": "Test User",
    "password": "testpass123"
  }'

# GeoNLI evaluation
curl -X POST http://localhost:8000/geoNLI/eval \
  -H "Content-Type: application/json" \
  -d '{
    "input_image": {
      "image_id": "test.png",
      "image_url": "https://bit.ly/4ouV45l",
      "metadata": {
        "width": 512,
        "height": 512,
        "spatial_resolution_m": 1.57
      }
    },
    "queries": {
      "caption_query": {
        "instruction": "Generate a caption"
      }
    }
  }'
```

---

### **Interactive API Documentation**

For complete API documentation with interactive testing:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- ✅ Full endpoint documentation
- ✅ Request/response schemas
- ✅ Interactive "Try it out" feature
- ✅ Authentication handling
- ✅ Example requests

---

## ☁️ Modal Deployment

### **Prerequisites**

```bash
# Install Modal CLI
pip install modal

# Authenticate with Modal
modal token new
```

Follow the prompts to authenticate with your Modal account.

---

### **Deployment Steps**

#### **Step 1: Prepare Files**

Ensure you have these files in your project root:

```bash
# Verify zip files are present
ls -lh captioning.zip vqa.zip grounding.zip

# Expected:
# captioning.zip  (~2-3GB)
# vqa.zip        (~2-3GB)
# grounding.zip  (~15-20GB)
```

**Note:** For Modal deployment, keep the zip files **compressed**. Modal will extract them automatically.

---

#### **Step 2: Configure Modal Secrets**

```bash
# Create Modal secrets for environment variables
modal secret create geonli-secrets \
  MONGODB_URL="mongodb+srv://username:password@cluster.mongodb.net/" \
  DATABASE_NAME="geonli_db" \
  JWT_SECRET="your-jwt-secret-from-openssl-rand-hex-32" \
  FRONTEND_URL="https://your-frontend-domain.com" \ 
```

---

#### **Step 3: Deploy to Modal**

```bash
# Deploy the application
modal deploy modal_app.py

# Expected output:
# ✓ Created objects.
# ├── 🔨 Created mount /path/to/captioning.zip
# ├── 🔨 Created mount /path/to/vqa.zip
# ├── 🔨 Created mount /path/to/grounding.zip
# ├── 🔨 Created function run_caption
# ├── 🔨 Created function run_vqa
# ├── 🔨 Created function run_grounding
# ├── 🔨 Created web function router => https://username--multi-model-env-backend-router.modal.run
# ├── 🔨 Created web function backend => https://username--multi-model-env-backend-backend.modal.run
# └── 🔨 Created web function health => https://username--multi-model-env-backend-health.modal.run
# 
# ✓ App deployed! 🎉
```

**Save these URLs!** You'll need them to access your deployed API.

---

#### **Step 4: Test Deployment**

```bash
# Replace <USERNAME> with your Modal username

# Test health endpoint
curl https://<USERNAME>--multi-model-env-backend-health.modal.run

# Test GeoNLI evaluation
curl -X POST https://<USERNAME>--multi-model-env-backend-backend.modal.run/geoNLI/eval \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

---

#### **Step 5: Monitor Logs**

```bash
# View deployment logs
modal app logs multi-model-env-backend

# Follow logs in real-time
modal app logs multi-model-env-backend --follow

# View specific function logs
modal app logs multi-model-env-backend --function backend
```

---

### **Modal Deployment Architecture**

```
Modal App: multi-model-env-backend
├── 3 Docker Images:
│   ├── caption_image (captioning.zip + Python 3.11)
│   ├── vqa_image (vqa.zip + Python 3.11)
│   └── grounding_image (grounding.zip + CUDA 12.1 + Python 3.10)
│
├── Functions:
│   ├── run_caption() - Caption generation
│   ├── run_vqa() - Visual Q&A
│   └── run_grounding() - Object detection (A10G GPU)
│
└── Web Endpoints:
    ├── /router (POST) - Individual service calls
    ├── /backend (ALL) - Complete FastAPI app
    └── /health (GET) - Health check
```

**URL Pattern:**
```
https://<username>--<app-name>-<function-name>.modal.run[/path]
```

---

### **Update Deployment**

```bash
# After making changes, redeploy
modal deploy modal_app.py

# Modal will automatically:
# - Build new images
# - Update functions
# - Deploy with zero downtime
```

---

### **Manage Deployments**

```bash
# List all Modal apps
modal app list

# Show app details
modal app show multi-model-env-backend

# Stop app (free up resources)
modal app stop multi-model-env-backend

# Delete app
modal app delete multi-model-env-backend
```

---

## 🧪 Testing

### **Manual Testing**

#### **Test Health Endpoint**

```bash
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "cuda_available": true,
  "gpu_count": 1,
  "gpu_name": "NVIDIA GeForce RTX 3090"
}
```

#### **Test Authentication**

```bash
# Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "fullName": "Test User",
    "password": "testpass123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Check auth (using saved cookies)
curl http://localhost:8000/api/auth/check \
  -b cookies.txt
```

#### **Test GeoNLI Evaluation**

Create `test_request.json`:
```json
{
  "input_image": {
    "image_id": "test.png",
    "image_url": "https://bit.ly/4ouV45l",
    "metadata": {
      "width": 512,
      "height": 512,
      "spatial_resolution_m": 1.57
    }
  },
  "queries": {
    "caption_query": {
      "instruction": "Generate a detailed caption"
    }
  }
}
```

Run test:
```bash
curl -X POST http://localhost:8000/geoNLI/eval \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

---

### **Automated Testing**

Create `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health check passed")

def test_signup():
    """Test user signup"""
    data = {
        "email": "test@example.com",
        "fullName": "Test User",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/signup", json=data)
    assert response.status_code == 201
    print("✅ Signup test passed")

def test_geonli_eval():
    """Test GeoNLI evaluation"""
    data = {
        "input_image": {
            "image_id": "test.png",
            "image_url": "https://bit.ly/4ouV45l",
            "metadata": {
                "width": 512,
                "height": 512,
                "spatial_resolution_m": 1.57
            }
        },
        "queries": {
            "caption_query": {
                "instruction": "Generate a caption"
            }
        }
    }
    response = requests.post(f"{BASE_URL}/geoNLI/eval", json=data)
    assert response.status_code == 200
    result = response.json()
    assert "queries" in result
    assert "caption_query" in result["queries"]
    print("✅ GeoNLI evaluation test passed")

if __name__ == "__main__":
    print("🧪 Running API tests...")
    
    try:
        test_health()
        test_signup()
        test_geonli_eval()
        
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
```

Run tests:
```bash
python test_api.py
```

---

### **Load Testing**

```bash
# Install Apache Bench
sudo apt-get install apache2-utils  # Linux
brew install httpd                   # macOS

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 -T 'application/json' \
  -p test_request.json \
  http://localhost:8000/geoNLI/eval

# Output shows:
# - Requests per second
# - Time per request
# - Transfer rate
# - Success/failure rate
```

---

## 🐛 Troubleshooting

### **Issue 1: MongoDB Connection Failed**

**Symptoms:**
```
pymongo.errors.ServerSelectionTimeoutError: connection refused
```

**Solutions:**

1. **Check MongoDB URL:**
```bash
echo $MONGODB_URL
# Should show your connection string
```

2. **Test MongoDB connection:**
```bash
mongosh "$MONGODB_URL"
```

3. **Whitelist IP in MongoDB Atlas:**
   - Go to: Network Access → Add IP Address
   - Add `0.0.0.0/0` (allow from anywhere)

4. **Check MongoDB service (if local):**
```bash
sudo systemctl status mongodb
sudo systemctl start mongodb
```

---

### **Issue 2: CUDA Out of Memory**

**Symptoms:**
```
RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB
```

**Solutions:**

1. **Check GPU memory:**
```bash
nvidia-smi
```

2. **Force CPU mode:**
```bash
export CUDA_VISIBLE_DEVICES=""
python src/server.py
```

3. **Reduce batch sizes** in `.env`:
```bash
MAX_CAPTION_TOKENS=256
MAX_VQA_TOKENS=64
```

4. **Use mixed precision:**
```python
# In service files, change dtype
torch_dtype=torch.float16  # Instead of float32
```

---

### **Issue 3: Model Files Not Found**

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'captioning_env/checkpoints/caption_model'
```

**Solutions:**

1. **Verify zip extraction:**
```bash
ls -la captioning_env/ vqa_env/ grounding_env/
```

2. **Check .env paths:**
```bash
grep MODEL_PATH .env
```

3. **Re-extract zip files:**
```bash
rm -rf captioning_env/ vqa_env/ grounding_env/
unzip captioning.zip -d captioning_env/
unzip vqa.zip -d vqa_env/
unzip grounding.zip -d grounding_env/
```

4. **Update model paths in `.env`** to match extracted structure.

---

### **Issue 4: Port Already in Use**

**Symptoms:**
```
OSError: [Errno 98] Address already in use
```

**Solutions:**

1. **Find process using port 8000:**
```bash
lsof -i :8000
# OR
netstat -tulpn | grep 8000
```

2. **Kill the process:**
```bash
kill -9 <PID>
```

3. **Use different port:**
```bash
uvicorn src.server:app --port 8001
```

---

### **Issue 5: Import Errors**

**Symptoms:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solutions:**

1. **Activate virtual environment:**
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. **Reinstall dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify installation:**
```bash
pip list | grep fastapi
pip list | grep uvicorn
```

4. **Check Python version:**
```bash
python --version
# Should be 3.10 or 3.11
```

---

### **Issue 6: CORS Errors**

**Symptoms:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solutions:**

1. **Update `FRONTEND_URL` in `.env`:**
```bash
FRONTEND_URL=http://localhost:5173
```

2. **Add frontend URL in `src/server.py`:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://your-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. **Restart server** after changes.

---

### **Issue 7: Slow Response Times**

**Symptoms:**
- Requests take >30 seconds
- Timeouts occur frequently

**Solutions:**

1. **Use GPU acceleration:**
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
```

2. **Reduce model sizes** (use base models without LoRA):
```bash
CAPTION_MODEL_PATH=
VQA_MODEL_PATH=
GROUNDING_MODEL_PATH=
```

3. **Implement caching:**
```python
# Add Redis caching for frequent requests
```

4. **Scale horizontally** with multiple workers:
```bash
gunicorn src.server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## 📁 Project Structure

```
multi-model-env-backend/
│
├── captioning.zip              # Caption model environment (from Google Drive)
├── vqa.zip                     # VQA model environment (from Google Drive)
├── grounding.zip               # Grounding model environment (from Google Drive)
│
├── modal_app.py                # Modal deployment configuration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
│
├── src/
│   ├── __init__.py
│   ├── server.py               # FastAPI application entry point
│   │
│   ├── routes/                 # API route definitions
│   │   ├── __init__.py
│   │   ├── authroute.py       # Authentication endpoints
│   │   ├── sessionroute.py    # Session management
│   │   ├── projectroute.py    # Project management
│   │   ├── messageroute.py    # Message/chat endpoints
│   │   ├── imageroute.py      # Image upload endpoints
│   │   └── geonliroute.py     # GeoNLI evaluation endpoints
│   │
│   ├── controllers/            # Business logic
│   │   ├── __init__.py
│   │   ├── authcontroller.py
│   │   ├── sessioncontroller.py
│   │   ├── projectcontroller.py
│   │   ├── messagecontroller.py
│   │   ├── imagecontroller.py
│   │   └── geonlicontroller.py  # Main GeoNLI orchestration
│   │
│   ├── services/               # AI model services
│   │   ├── __init__.py
│   │   ├── florence2_caption_service.py   # Caption generation
│   │   ├── florence2_vqa_service.py       # Visual Q&A
│   │   └── grounding_service.py           # Object detection
│   │
│   ├── models/                 # Pydantic models (request/response)
│   │   ├── __init__.py
│   │   └── geonlimodel.py     # GeoNLI evaluation models
│   │
│   ├── modals/                 # Database models
│   │   ├── __init__.py
│   │   ├── usermodel.py
│   │   ├── sessionmodel.py
│   │   ├── projectmodel.py
│   │   ├── messagemodel.py
│   │   └── imagemodel.py
│   │
│   ├── lib/                    # Core utilities
│   │   ├── __init__.py
│   │   ├── db.py              # MongoDB connection
│   │   └── utils.py           # JWT utilities
│   │
│   ├── middleware/             # FastAPI middleware
│   │   ├── __init__.py
│   │   └── authmiddleware.py  # Authentication middleware
│   │
│   └── utils/                  # Helper functions
│       ├── __init__.py
│       └── image_utils.py     # Image processing utilities
│
├── uploads/                    # Uploaded images (created at runtime)
│
└── venv/                       # Python virtual environment (create this)
```

---

## 📊 Performance Benchmarks

### **Local Development (RTX 3090)**

| Operation | Time | GPU Memory | CPU Usage |
|-----------|------|------------|-----------|
| Caption Generation | ~2s | 4GB | 20% |
| VQA (single question) | ~1s | 4GB | 15% |
| Grounding Detection | ~5s | 12GB | 30% |
| Full GeoNLI Eval | ~8s | 14GB | 40% |

### **Modal Deployment (A10G GPU)**

| Operation | Cold Start | Warm Time | GPU Memory |
|-----------|------------|-----------|------------|
| Caption | ~30s | ~1s | 6GB |
| VQA | ~30s | ~0.5s | 6GB |
| Grounding | ~45s | ~3s | 16GB |
| Full Eval | ~60s | ~5s | 20GB |

**Notes:**
- Cold start = First request after deployment
- Warm time = Subsequent requests (model already loaded)
- Memory usage varies with input image size

---

## 🔐 Security Best Practices

### **1. Environment Variables**

❌ **Never commit `.env` files**
```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

✅ **Use strong JWT secrets**
```bash
# Generate secure secret
openssl rand -hex 32
```

### **2. MongoDB Security**

✅ **Enable authentication**
```bash
# Create admin user in MongoDB
use admin
db.createUser({
  user: "admin",
  pwd: "strongpassword",
  roles: ["userAdminAnyDatabase"]
})
```

✅ **Restrict IP access** in MongoDB Atlas:
- Whitelist specific IPs instead of 0.0.0.0/0 in production

### **3. API Security**

✅ **Use HTTPS in production**:
```bash
# Deploy behind nginx/Caddy with SSL
```

✅ **Rate limiting**:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.get("/api/endpoint")
@limiter.limit("5/minute")
async def endpoint():
    pass
```

### **4. File Upload Security**

✅ **Validate file types**:
```python
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
```

✅ **Limit file sizes**:
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

### **5. Dependency Management**

✅ **Keep dependencies updated**:
```bash
pip install --upgrade pip
pip list --outdated
pip install --upgrade <package>
```

---

## 📈 Scaling Considerations

### **Horizontal Scaling**

```bash
# Use multiple workers with Gunicorn
gunicorn src.server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### **Caching**

```python
# Add Redis caching for frequent requests
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import aioredis

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="geonli")

@app.get("/api/endpoint")
@cache(expire=60)  # Cache for 60 seconds
async def endpoint():
    pass
```

### **Database Optimization**

```python
# Add indexes in db.py
async def init_database():
    db = get_database()
    
    # User indexes
    await db[USERS_COLLECTION].create_index("email", unique=True)
    await db[USERS_COLLECTION].create_index("createdAt")
    
    # Session indexes
    await db[SESSIONS_COLLECTION].create_index([
        ("userId", 1), 
        ("updatedAt", -1)
    ])
    
    # Message indexes
    await db[MESSAGES_COLLECTION].create_index([
        ("sessionId", 1), 
        ("createdAt", 1)
    ])
```

### **Load Balancing**

```nginx
# nginx.conf
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name api.geonli.com;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **MongoDB Documentation**: https://docs.mongodb.com
- **Modal Documentation**: https://modal.com/docs
- **Florence-2 Model**: https://huggingface.co/microsoft/Florence-2-large
- **YOLO Documentation**: https://docs.ultralytics.com
- **PyTorch Documentation**: https://pytorch.org/docs

---


## ✅ Quick Start Checklist

Use this checklist to ensure everything is set up correctly:

- [ ] Python 3.10 or 3.11 installed
- [ ] Downloaded all 3 zip files from Google Drive
  - [ ] captioning.zip (~2-3GB)
  - [ ] vqa.zip (~2-3GB)
  - [ ] grounding.zip (~15-20GB)
- [ ] Created virtual environment: `python3.11 -m venv venv`
- [ ] Activated virtual environment
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Created `.env` file with all required variables
- [ ] Set up MongoDB (Atlas or local)
- [ ] Generated JWT secret: `openssl rand -hex 32`
- [ ] Extracted zip files (for local dev)
- [ ] Started server: `python src/server.py`
- [ ] Tested health endpoint: `curl http://localhost:8000/health`
- [ ] Tested API docs: http://localhost:8000/docs
- [ ] Tested GeoNLI evaluation: POST to `/geoNLI/eval`
- [ ] (Optional) Deployed to Modal: `modal deploy modal_app.py`

---

## 🎉 You're All Set!

Your GeoNLI backend is now ready to use! Here's what you can do next:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Test the endpoints**: Use the interactive Swagger UI
3. **Connect your frontend**: Update CORS settings and connect
4. **Deploy to production**: Follow the Modal deployment guide
5. **Monitor performance**: Check logs and add monitoring

---

 