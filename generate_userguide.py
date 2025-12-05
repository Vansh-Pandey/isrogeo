#!/usr/bin/env python3
"""
GeoNLI User Guide PDF Generator
Creates a comprehensive user guide with deployment and usage instructions
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from datetime import datetime

def create_user_guide():
    """Create the GeoNLI User Guide PDF"""
    
    # Create document
    doc = SimpleDocTemplate(
        "/mnt/user-data/outputs/User_Guide.pdf",
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=28,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#3b82f6'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#60a5fa'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=10
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=9,
        fontName='Courier',
        textColor=colors.HexColor('#1e293b'),
        backColor=colors.HexColor('#f1f5f9'),
        leftIndent=20,
        rightIndent=20,
        spaceAfter=10,
        spaceBefore=5
    )
    
    note_style = ParagraphStyle(
        'Note',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#0f766e'),
        backColor=colors.HexColor('#ccfbf1'),
        leftIndent=20,
        rightIndent=20,
        spaceAfter=10,
        spaceBefore=5,
        borderPadding=10
    )
    
    warning_style = ParagraphStyle(
        'Warning',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#9a3412'),
        backColor=colors.HexColor('#fed7aa'),
        leftIndent=20,
        rightIndent=20,
        spaceAfter=10,
        spaceBefore=5,
        borderPadding=10
    )
    
    # Build document content
    story = []
    
    # ===================================================================
    # COVER PAGE
    # ===================================================================
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("GeoNLI", title_style))
    story.append(Paragraph("AI-Powered Satellite Image Analysis Platform", subtitle_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("User Guide", heading1_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Version info box
    version_data = [
        ['Version', '1.0.0'],
        ['Release Date', datetime.now().strftime('%B %Y')],
        ['Platform', 'Web Application'],
        ['Backend', 'FastAPI + Python'],
        ['Frontend', 'React 19'],
    ]
    version_table = Table(version_data, colWidths=[2*inch, 3*inch])
    version_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#334155')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(version_table)
    
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph(
        "© 2025 GeoNLI Project. All rights reserved.",
        subtitle_style
    ))
    
    story.append(PageBreak())
    
    # ===================================================================
    # TABLE OF CONTENTS
    # ===================================================================
    story.append(Paragraph("Table of Contents", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    toc_items = [
        ("1. Introduction", "3"),
        ("   1.1 What is GeoNLI?", "3"),
        ("   1.2 Key Features", "3"),
        ("   1.3 System Requirements", "4"),
        ("2. Quick Start Guide", "5"),
        ("   2.1 Account Creation", "5"),
        ("   2.2 First Login", "5"),
        ("   2.3 Your First Analysis", "6"),
        ("3. Backend Deployment", "7"),
        ("   3.1 Prerequisites", "7"),
        ("   3.2 Local Deployment", "8"),
        ("   3.3 Cloud Deployment (Modal)", "11"),
        ("4. Frontend Setup", "13"),
        ("   4.1 Installation", "13"),
        ("   4.2 Configuration", "14"),
        ("   4.3 Running Development Server", "14"),
        ("5. Using the Application", "15"),
        ("   5.1 Dashboard Overview", "15"),
        ("   5.2 Uploading Images", "16"),
        ("   5.3 AI Chat Interface", "17"),
        ("   5.4 Session Management", "18"),
        ("   5.5 Advanced Features", "19"),
        ("6. API Reference", "21"),
        ("   6.1 GeoNLI Evaluation Endpoint", "21"),
        ("   6.2 Authentication", "22"),
        ("   6.3 Session Management", "23"),
        ("7. Troubleshooting", "24"),
        ("   7.1 Common Issues", "24"),
        ("   7.2 Backend Problems", "25"),
        ("   7.3 Frontend Problems", "26"),
        ("8. Best Practices", "27"),
        ("9. Support & Resources", "28"),
    ]
    
    for item, page in toc_items:
        toc_line = f"{item}" + "." * (60 - len(item) - len(page)) + f" {page}"
        story.append(Paragraph(toc_line, body_style))
    
    story.append(PageBreak())
    
    # ===================================================================
    # SECTION 1: INTRODUCTION
    # ===================================================================
    story.append(Paragraph("1. Introduction", heading1_style))
    
    story.append(Paragraph("1.1 What is GeoNLI?", heading2_style))
    story.append(Paragraph(
        "GeoNLI is an advanced AI-powered platform for analyzing satellite imagery through natural "
        "language interactions. It combines state-of-the-art computer vision models with an intuitive "
        "chat interface to provide detailed image analysis, object detection, and visual question answering.",
        body_style
    ))
    
    story.append(Paragraph(
        "The platform leverages three specialized AI services:",
        body_style
    ))
    
    # Services table
    services_data = [
        ['Service', 'Model', 'Purpose'],
        ['Caption', 'Florence-2', 'Generate detailed scene descriptions'],
        ['VQA', 'Florence-2', 'Answer questions about images'],
        ['Grounding', 'GeoGround + YOLO', 'Detect objects with precise bounding boxes'],
    ]
    services_table = Table(services_data, colWidths=[1.5*inch, 1.8*inch, 3*inch])
    services_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(services_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("1.2 Key Features", heading2_style))
    
    features = [
        "<b>Intelligent Image Analysis:</b> Upload satellite images and receive detailed AI-generated captions",
        "<b>Natural Language Queries:</b> Ask questions about your images in plain English",
        "<b>Object Detection:</b> Automatically identify and locate objects with oriented bounding boxes",
        "<b>Session Management:</b> Organize your analyses into sessions for easy reference",
        "<b>Export Capabilities:</b> Download analysis results and chat conversations",
        "<b>Multi-user Support:</b> Secure authentication with personal workspaces",
        "<b>Responsive Interface:</b> Works seamlessly on desktop and tablet devices",
        "<b>Real-time Processing:</b> Get instant AI responses as you interact",
    ]
    
    for feature in features:
        story.append(Paragraph(f"• {feature}", body_style))
    
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("1.3 System Requirements", heading2_style))
    
    story.append(Paragraph("<b>For Users (Web Interface):</b>", body_style))
    story.append(Paragraph("• Modern web browser (Chrome, Firefox, Safari, or Edge)", body_style))
    story.append(Paragraph("• Stable internet connection (minimum 5 Mbps)", body_style))
    story.append(Paragraph("• Screen resolution: 1280x720 or higher", body_style))
    
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("<b>For Deployment (Backend):</b>", body_style))
    story.append(Paragraph("• Python 3.10 or 3.11", body_style))
    story.append(Paragraph("• 16GB RAM minimum (32GB recommended)", body_style))
    story.append(Paragraph("• 50GB storage (100GB recommended)", body_style))
    story.append(Paragraph("• NVIDIA GPU with 16GB+ VRAM (optional but recommended)", body_style))
    story.append(Paragraph("• MongoDB 4.4+ (local or Atlas)", body_style))
    
    story.append(PageBreak())
    
    # ===================================================================
    # SECTION 2: QUICK START GUIDE
    # ===================================================================
    story.append(Paragraph("2. Quick Start Guide", heading1_style))
    
    story.append(Paragraph(
        "This section will help you get started with using GeoNLI in just a few minutes. "
        "If you're setting up the application for the first time, please refer to Sections 3 and 4 "
        "for deployment instructions.",
        body_style
    ))
    
    story.append(Paragraph("2.1 Account Creation", heading2_style))
    
    story.append(Paragraph("<b>Step 1:</b> Navigate to the GeoNLI application URL", body_style))
    story.append(Paragraph("<font face='Courier' size='9'>https://your-geonli-instance.com</font>", code_style))
    
    story.append(Paragraph("<b>Step 2:</b> Click on the 'Sign Up' tab", body_style))
    
    story.append(Paragraph("<b>Step 3:</b> Fill in your registration details:", body_style))
    story.append(Paragraph("• Full Name: Your complete name", body_style))
    story.append(Paragraph("• Email: A valid email address", body_style))
    story.append(Paragraph("• Password: Minimum 6 characters", body_style))
    
    story.append(Paragraph("<b>Step 4:</b> Click 'Create Account'", body_style))
    
    story.append(Paragraph(
        "<b>Note:</b> Upon successful registration, you'll be automatically logged in.",
        note_style
    ))
    
    story.append(Paragraph("2.2 First Login", heading2_style))
    
    story.append(Paragraph(
        "After creating your account or for subsequent visits:",
        body_style
    ))
    
    story.append(Paragraph("<b>Step 1:</b> Go to the login page", body_style))
    
    story.append(Paragraph("<b>Step 2:</b> Enter your credentials:", body_style))
    story.append(Paragraph("• Email: Your registered email", body_style))
    story.append(Paragraph("• Password: Your account password", body_style))
    
    story.append(Paragraph("<b>Step 3:</b> Click 'Sign In'", body_style))
    
    story.append(Paragraph(
        "You'll be redirected to the main dashboard with three panels:",
        body_style
    ))
    story.append(Paragraph("• <b>Left Panel:</b> Session list and management", body_style))
    story.append(Paragraph("• <b>Center Panel:</b> Image workspace", body_style))
    story.append(Paragraph("• <b>Right Panel:</b> AI chat console", body_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("2.3 Your First Analysis", heading2_style))
    
    story.append(Paragraph("<b>Step 1: Upload an Image</b>", heading3_style))
    story.append(Paragraph(
        "In the center panel (Image Workspace):",
        body_style
    ))
    story.append(Paragraph("1. Click the upload area or drag and drop an image", body_style))
    story.append(Paragraph("2. Select a satellite image (JPEG or PNG format)", body_style))
    story.append(Paragraph("3. Wait for the upload to complete", body_style))
    
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("<b>Step 2: Ask Questions</b>", heading3_style))
    story.append(Paragraph(
        "In the right panel (Chat Console), type your first question:",
        body_style
    ))
    story.append(Paragraph(
        '<font face="Courier" size="9">What can you see in this satellite image?</font>',
        code_style
    ))
    
    story.append(Paragraph("Press Enter or click the send button.", body_style))
    
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("<b>Step 3: View Results</b>", heading3_style))
    story.append(Paragraph(
        "The AI will analyze your image and respond with:",
        body_style
    ))
    story.append(Paragraph("• A detailed caption describing the scene", body_style))
    story.append(Paragraph("• Answers to your specific questions", body_style))
    story.append(Paragraph("• Object detection results if requested", body_style))
    
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("<b>Step 4: Continue the Conversation</b>", heading3_style))
    story.append(Paragraph(
        "You can ask follow-up questions such as:",
        body_style
    ))
    story.append(Paragraph('• "How many buildings are visible?"', body_style))
    story.append(Paragraph('• "What color are the roofs?"', body_style))
    story.append(Paragraph('• "Can you locate all the vehicles?"', body_style))
    
    story.append(Paragraph(
        "<b>Tip:</b> Each session maintains conversation history, allowing the AI to understand context.",
        note_style
    ))
    
    story.append(PageBreak())
    
    # ===================================================================
    # SECTION 3: BACKEND DEPLOYMENT
    # ===================================================================
    story.append(Paragraph("3. Backend Deployment", heading1_style))
    
    story.append(Paragraph(
        "This section provides detailed instructions for deploying the GeoNLI backend, which powers "
        "all AI analysis capabilities. You can deploy locally for development or to Modal for production.",
        body_style
    ))
    
    story.append(Paragraph("3.1 Prerequisites", heading2_style))
    
    story.append(Paragraph("<b>Software Requirements:</b>", heading3_style))
    
    prereq_data = [
        ['Software', 'Version', 'Purpose'],
        ['Python', '3.10 or 3.11', 'Backend runtime'],
        ['MongoDB', '4.4+', 'Database storage'],
        ['Git', 'Latest', 'Version control'],
        ['CUDA', '12.1+ (optional)', 'GPU acceleration'],
    ]
    prereq_table = Table(prereq_data, colWidths=[1.5*inch, 1.5*inch, 3.3*inch])
    prereq_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    story.append(prereq_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>Model Files:</b>", heading3_style))
    story.append(Paragraph(
        "You'll need three pre-packaged model environment files:",
        body_style
    ))
    story.append(Paragraph("• <b>captioning.zip</b> (~2-3GB) - Florence-2 caption model", body_style))
    story.append(Paragraph("• <b>vqa.zip</b> (~2-3GB) - Florence-2 VQA model", body_style))
    story.append(Paragraph("• <b>grounding.zip</b> (~15-20GB) - GeoGround + YOLO models", body_style))
    
    story.append(Paragraph(
        "<b>Warning:</b> Ensure you have sufficient storage space (~20GB minimum) before downloading.",
        warning_style
    ))
    
    story.append(PageBreak())
    
    story.append(Paragraph("3.2 Local Deployment", heading2_style))
    
    story.append(Paragraph("<b>Step 1: Extract the Deployment Package</b>", heading3_style))
    story.append(Paragraph(
        "Extract the provided <font face='Courier'>multi-model-env-backend.zip</font> file:",
        body_style
    ))
    story.append(Paragraph(
        '<font face="Courier" size="9">unzip multi-model-env-backend.zip<br/>'
        'cd multi-model-env-backend</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Step 2: Download Model Files</b>", heading3_style))
    story.append(Paragraph(
        "If model files are not included in the package, download them from the provided Google Drive links "
        "and place them in the <font face='Courier'>multi-model-env-backend/</font> directory.",
        body_style
    ))
    
    story.append(Paragraph(
        
        code_style
    ))
    
    story.append(Paragraph("<b>Step 3: Create Virtual Environment</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="9">python3.11 -m venv venv<br/>'
        'source venv/bin/activate  # On Linux/Mac<br/>'
        '# OR<br/>'
        'venv\\Scripts\\activate     # On Windows</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Step 4: Install Dependencies</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="9">pip install --upgrade pip<br/>'
        'pip install -r requirements.txt</font>',
        code_style
    ))
    
    story.append(Paragraph(
        "This will install all required Python packages including FastAPI, PyTorch, and model dependencies.",
        body_style
    ))
    
    story.append(PageBreak())
    
    story.append(Paragraph("<b>Step 5: Extract Model Environments</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="9">unzip captioning.zip -d captioning_env/<br/>'
        'unzip vqa.zip -d vqa_env/<br/>'
        'unzip grounding.zip -d grounding_env/</font>',
        code_style
    ))
    
    story.append(Paragraph(
        "<b>Note:</b> This step may take several minutes due to large file sizes.",
        note_style
    ))
    
    story.append(Paragraph("<b>Step 6: Configure MongoDB</b>", heading3_style))
    story.append(Paragraph(
        "Option A: Use MongoDB Atlas (Recommended)",
        body_style
    ))
    story.append(Paragraph("1. Go to https://www.mongodb.com/cloud/atlas", body_style))
    story.append(Paragraph("2. Create a free account and cluster", body_style))
    story.append(Paragraph("3. Create a database user with password", body_style))
    story.append(Paragraph("4. Whitelist IP address: Add 0.0.0.0/0 for development", body_style))
    story.append(Paragraph("5. Get connection string from 'Connect' button", body_style))
    
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph(
        "Option B: Install MongoDB Locally",
        body_style
    ))
    story.append(Paragraph(
        '<font face="Courier" size="9"># Ubuntu/Debian<br/>'
        'sudo apt-get install mongodb-community<br/><br/>'
        '# macOS<br/>'
        'brew install mongodb-community<br/><br/>'
        '# Start service<br/>'
        'sudo systemctl start mongodb</font>',
        code_style
    ))
    
    story.append(PageBreak())
    
    story.append(Paragraph("<b>Step 7: Create Configuration File</b>", heading3_style))
    story.append(Paragraph(
        "Create a <font face='Courier'>.env</font> file in the project root with the following content:",
        body_style
    ))
    
    story.append(Paragraph(
        '<font face="Courier" size="8"># Database<br/>'
        'MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/<br/>'
        'DATABASE_NAME=geonli_db<br/><br/>'
        '# Authentication<br/>'
        'JWT_SECRET=your-generated-secret-key<br/>'
        'JWT_ALGORITHM=HS256<br/>'
        'ACCESS_TOKEN_EXPIRE_DAYS=7<br/><br/>'
        '# Server<br/>'
        'HOST=0.0.0.0<br/>'
        'PORT=8000<br/>'
        'NODE_ENV=development<br/>'
        'FRONTEND_URL=http://localhost:5173<br/><br/>'
        '# Model Paths<br/>'
        'CAPTION_MODEL_PATH=./checkpoints/caption_model<br/>'
        'VQA_MODEL_PATH=./checkpoints/vqa_model<br/>'
        'GROUNDING_MODEL_PATH=./models/geoground</font>',
        code_style
    ))
    
    story.append(Paragraph(
        "<b>Important:</b> Generate a secure JWT secret using: <font face='Courier'>openssl rand -hex 32</font>",
        warning_style
    ))
    
    story.append(Paragraph("<b>Step 8: Start the Backend Server</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="9">python src/server.py</font>',
        code_style
    ))
    
    story.append(Paragraph(
        "The server will start on http://localhost:8000. You should see:",
        body_style
    ))
    story.append(Paragraph(
        '<font face="Courier" size="9">🚀 Starting GeoNLI Backend...<br/>'
        '📍 Environment: Local<br/>'
        '✅ Database initialized<br/>'
        'INFO: Uvicorn running on http://0.0.0.0:8000</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Step 9: Verify Installation</b>", heading3_style))
    story.append(Paragraph(
        "Test the health endpoint:",
        body_style
    ))
    story.append(Paragraph(
        '<font face="Courier" size="9">curl http://localhost:8000/health</font>',
        code_style
    ))
    
    story.append(Paragraph(
        "Visit the API documentation at: http://localhost:8000/docs",
        body_style
    ))
    
    story.append(PageBreak())
    
    story.append(Paragraph("3.3 Cloud Deployment (Modal)", heading2_style))
    
    story.append(Paragraph(
        "Modal provides serverless GPU infrastructure ideal for AI workloads. "
        "This deployment option offers automatic scaling and pay-per-use pricing.",
        body_style
    ))
    
    story.append(Paragraph("<b>Step 1: Install Modal CLI</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="9">pip install modal</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Step 2: Authenticate with Modal</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="9">modal token new</font>',
        code_style
    ))
    story.append(Paragraph("Follow the prompts to log in to your Modal account.", body_style))
    
    story.append(Paragraph("<b>Step 3: Configure Modal Secrets</b>", heading3_style))
    story.append(Paragraph(
        "Store your environment variables securely in Modal:",
        body_style
    ))
    story.append(Paragraph(
        '<font face="Courier" size="8">modal secret create geonli-secrets \\<br/>'
        '  MONGODB_URL="mongodb+srv://username:password@cluster.mongodb.net/" \\<br/>'
        '  DATABASE_NAME="geonli_db" \\<br/>'
        '  JWT_SECRET="your-jwt-secret" \\<br/>'
        '  FRONTEND_URL="https://your-frontend-domain.com"</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Step 4: Prepare Deployment Files</b>", heading3_style))
    story.append(Paragraph(
        "Ensure these files are in your project root:",
        body_style
    ))
    story.append(Paragraph("• modal_app.py (deployment configuration)", body_style))
    story.append(Paragraph("• captioning.zip", body_style))
    story.append(Paragraph("• vqa.zip", body_style))
    story.append(Paragraph("• grounding.zip", body_style))
    story.append(Paragraph("• src/ directory (backend source code)", body_style))
    
    story.append(Paragraph(
        "<b>Note:</b> For Modal deployment, keep zip files compressed - Modal extracts them automatically.",
        note_style
    ))
    
    story.append(PageBreak())
    
    story.append(Paragraph("<b>Step 5: Deploy to Modal</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="9">modal deploy modal_app.py</font>',
        code_style
    ))
    
    story.append(Paragraph(
        "Modal will build Docker images, upload your files, and deploy the application. "
        "You'll receive URLs for your deployed endpoints:",
        body_style
    ))
    
    story.append(Paragraph(
        '<font face="Courier" size="8">✓ App deployed! 🎉<br/><br/>'
        'Web endpoints:<br/>'
        '├─ backend: https://username--multi-model-env-backend-backend.modal.run<br/>'
        '├─ health: https://username--multi-model-env-backend-health.modal.run<br/>'
        '└─ router: https://username--multi-model-env-backend-router.modal.run</font>',
        code_style
    ))
    
    story.append(Paragraph(
        "<b>Important:</b> Save these URLs - you'll need the backend URL for frontend configuration.",
        warning_style
    ))
    
    story.append(Paragraph("<b>Step 6: Test Deployment</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="9">curl https://&lt;username&gt;--multi-model-env-backend-health.modal.run</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Step 7: Monitor Logs</b>", heading3_style))
    story.append(Paragraph(
        "View real-time logs:",
        body_style
    ))
    story.append(Paragraph(
        '<font face="Courier" size="9">modal app logs multi-model-env-backend --follow</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Deployment Tips:</b>", heading3_style))
    story.append(Paragraph("• First deployment takes 5-10 minutes as Modal builds images", body_style))
    story.append(Paragraph("• Subsequent deploys are faster (2-3 minutes)", body_style))
    story.append(Paragraph("• Cold starts take 30-60 seconds, warm requests are instant", body_style))
    story.append(Paragraph("• Modal automatically scales based on demand", body_style))
    
    story.append(PageBreak())
    
    # ===================================================================
    # SECTION 4: FRONTEND SETUP
    # ===================================================================
    story.append(Paragraph("4. Frontend Setup", heading1_style))
    
    story.append(Paragraph(
        "The GeoNLI frontend is a React 19 application that provides the user interface. "
        "This section guides you through setting up and running the frontend.",
        body_style
    ))
    
    story.append(Paragraph("4.1 Installation", heading2_style))
    
    story.append(Paragraph("<b>Step 1: Extract Frontend Package</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="9">unzip frontend.zip<br/>'
        'cd frontend</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Step 2: Verify Node.js Installation</b>", heading3_style))
    story.append(Paragraph(
        "Ensure you have Node.js v20.19.0 or v22.12.0+:",
        body_style
    ))
    story.append(Paragraph(
        '<font face="Courier" size="9">node --version<br/>'
        'npm --version</font>',
        code_style
    ))
    
    story.append(Paragraph(
        "If Node.js is not installed, download from: https://nodejs.org/",
        body_style
    ))
    
    story.append(Paragraph("<b>Step 3: Install Dependencies</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="9">npm install</font>',
        code_style
    ))
    
    story.append(Paragraph(
        "This installs all required packages including React, Vite, Tailwind CSS, and Zustand.",
        body_style
    ))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("4.2 Configuration", heading2_style))
    
    story.append(Paragraph("<b>Create Environment File</b>", heading3_style))
    story.append(Paragraph(
        "Create a <font face='Courier'>.env</font> file in the frontend directory:",
        body_style
    ))
    
    story.append(Paragraph(
        '<font face="Courier" size="9"># For local backend<br/>'
        'VITE_IPV4_URL=http://localhost:8000<br/><br/>'
        '# For Modal backend<br/>'
        'VITE_BACKEND_URL=https://username--multi-model-env-backend-backend.modal.run<br/><br/>'
        '# Optional: Custom port<br/>'
        'VITE_PORT=5173</font>',
        code_style
    ))
    
    story.append(Paragraph(
        "<b>Important:</b> Replace the Modal URL with your actual deployment URL from Section 3.3.",
        warning_style
    ))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("4.3 Running Development Server", heading2_style))
    
    story.append(Paragraph("<b>Start the Development Server</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="9">npm run dev</font>',
        code_style
    ))
    
    story.append(Paragraph(
        "The application will start on http://localhost:5173. You should see:",
        body_style
    ))
    story.append(Paragraph(
        '<font face="Courier" size="9">VITE v7.2.4  ready in 500 ms<br/><br/>'
        '➜  Local:   http://localhost:5173/<br/>'
        '➜  Network: http://192.168.1.100:5173/</font>',
        code_style
    ))
    
    story.append(Paragraph(
        "Open your web browser and navigate to http://localhost:5173 to access the application.",
        body_style
    ))
    
    story.append(Paragraph("<b>Production Build</b>", heading3_style))
    story.append(Paragraph(
        "To create a production build:",
        body_style
    ))
    story.append(Paragraph(
        '<font face="Courier" size="9">npm run build</font>',
        code_style
    ))
    
    story.append(Paragraph(
        "The optimized build will be created in the <font face='Courier'>dist/</font> directory. "
        "You can deploy this to any static hosting service (Vercel, Netlify, etc.).",
        body_style
    ))
    
    story.append(PageBreak())
    
    # ===================================================================
    # SECTION 5: USING THE APPLICATION
    # ===================================================================
    story.append(Paragraph("5. Using the Application", heading1_style))
    
    story.append(Paragraph("5.1 Dashboard Overview", heading2_style))
    
    story.append(Paragraph(
        "The GeoNLI dashboard consists of three main panels:",
        body_style
    ))
    
    dashboard_data = [
        ['Panel', 'Location', 'Purpose'],
        ['Session List', 'Left', 'View and manage analysis sessions'],
        ['Image Workspace', 'Center', 'Upload and view satellite images'],
        ['Chat Console', 'Right', 'Interact with AI for image analysis'],
    ]
    dashboard_table = Table(dashboard_data, colWidths=[1.8*inch, 1.3*inch, 3.2*inch])
    dashboard_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    story.append(dashboard_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>Header Bar Features:</b>", heading3_style))
    story.append(Paragraph("• <b>Theme Toggle:</b> Switch between dark and light modes", body_style))
    story.append(Paragraph("• <b>Share Button:</b> Share the current session", body_style))
    story.append(Paragraph("• <b>Profile Menu:</b> Access account settings and logout", body_style))
    
    story.append(Paragraph("<b>Panel Resizing:</b>", heading3_style))
    story.append(Paragraph(
        "You can resize the left and right panels by dragging the divider between panels. "
        "This allows you to customize your workspace based on your needs.",
        body_style
    ))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("5.2 Uploading Images", heading2_style))
    
    story.append(Paragraph("<b>Supported Formats:</b>", heading3_style))
    story.append(Paragraph("• JPEG (.jpg, .jpeg)", body_style))
    story.append(Paragraph("• PNG (.png)", body_style))
    
    story.append(Paragraph("<b>Upload Methods:</b>", heading3_style))
    
    story.append(Paragraph("<b>Method 1: Drag and Drop</b>", body_style))
    story.append(Paragraph("1. Locate your satellite image file", body_style))
    story.append(Paragraph("2. Drag the file to the Image Workspace (center panel)", body_style))
    story.append(Paragraph("3. Drop the file when the upload area is highlighted", body_style))
    
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("<b>Method 2: Click to Upload</b>", body_style))
    story.append(Paragraph("1. Click the upload area in the Image Workspace", body_style))
    story.append(Paragraph("2. Browse and select your image file", body_style))
    story.append(Paragraph("3. Click 'Open' to confirm", body_style))
    
    story.append(Paragraph("<b>After Upload:</b>", heading3_style))
    story.append(Paragraph("• The image will display in the center panel", body_style))
    story.append(Paragraph("• Zoom controls appear in the top-right corner", body_style))
    story.append(Paragraph("• A download button allows you to save the image", body_style))
    
    story.append(Paragraph(
        "<b>Tip:</b> You can zoom in/out using the +/- buttons or reset to 100% zoom.",
        note_style
    ))
    
    story.append(PageBreak())
    
    story.append(Paragraph("5.3 AI Chat Interface", heading2_style))
    
    story.append(Paragraph(
        "The AI chat console on the right allows you to interact with the AI about your uploaded images.",
        body_style
    ))
    
    story.append(Paragraph("<b>Asking Questions:</b>", heading3_style))
    
    story.append(Paragraph("<b>Step 1:</b> Type your question in the input field at the bottom", body_style))
    story.append(Paragraph("<b>Step 2:</b> Press Enter or click the send button", body_style))
    story.append(Paragraph("<b>Step 3:</b> Wait for the AI to analyze and respond", body_style))
    
    story.append(Paragraph("<b>Example Questions:</b>", heading3_style))
    
    example_questions = [
        "What objects can you identify in this image?",
        "Describe the overall scene in detail",
        "How many buildings are visible?",
        "What is the predominant land use type?",
        "Can you locate all the vehicles?",
        "What color are the roofs of the buildings?",
        "Are there any water bodies present?",
        "Estimate the size of the largest structure",
    ]
    
    for question in example_questions:
        story.append(Paragraph(f'• "{question}"', body_style))
    
    story.append(Paragraph("<b>Message Actions:</b>", heading3_style))
    story.append(Paragraph("• <b>Copy:</b> Click the copy icon to copy a message to clipboard", body_style))
    story.append(Paragraph("• <b>Export:</b> Click 'Export Chat' to download the conversation as a text file", body_style))
    
    story.append(Paragraph(
        "<b>Note:</b> The AI maintains context within a session, so you can ask follow-up questions.",
        note_style
    ))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("5.4 Session Management", heading2_style))
    
    story.append(Paragraph(
        "Sessions help you organize your analyses. Each session maintains its own chat history and uploaded images.",
        body_style
    ))
    
    story.append(Paragraph("<b>Creating a New Session:</b>", heading3_style))
    story.append(Paragraph("1. Click the '+ New Chat' button in the left panel", body_style))
    story.append(Paragraph("2. A new session is created with a default name", body_style))
    story.append(Paragraph("3. The session becomes active immediately", body_style))
    
    story.append(Paragraph("<b>Renaming a Session:</b>", heading3_style))
    story.append(Paragraph("1. Hover over a session in the list", body_style))
    story.append(Paragraph("2. Click the three-dot menu icon", body_style))
    story.append(Paragraph("3. Select 'Rename'", body_style))
    story.append(Paragraph("4. Enter the new name and confirm", body_style))
    
    story.append(Paragraph("<b>Archiving a Session:</b>", heading3_style))
    story.append(Paragraph("1. Open the session menu (three dots)", body_style))
    story.append(Paragraph("2. Select 'Archive'", body_style))
    story.append(Paragraph("3. Archived sessions are hidden from the main list", body_style))
    story.append(Paragraph("4. Toggle 'Show Archived' to view archived sessions", body_style))
    
    story.append(Paragraph("<b>Deleting a Session:</b>", heading3_style))
    story.append(Paragraph("1. Open the session menu", body_style))
    story.append(Paragraph("2. Select 'Delete'", body_style))
    story.append(Paragraph("3. Confirm the deletion", body_style))
    
    story.append(Paragraph(
        "<b>Warning:</b> Deleting a session permanently removes all associated messages and images.",
        warning_style
    ))
    
    story.append(Paragraph("<b>Searching Sessions:</b>", heading3_style))
    story.append(Paragraph("1. Click the search icon in the left panel", body_style))
    story.append(Paragraph("2. Type keywords to filter sessions by name", body_style))
    story.append(Paragraph("3. Click the X icon to clear the search", body_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("5.5 Advanced Features", heading2_style))
    
    story.append(Paragraph("<b>Object Detection (Grounding):</b>", heading3_style))
    story.append(Paragraph(
        "To get precise object locations with bounding boxes:",
        body_style
    ))
    story.append(Paragraph('1. Upload an image', body_style))
    story.append(Paragraph('2. Ask: "Can you locate all [objects] in this image?"', body_style))
    story.append(Paragraph('3. Example: "Can you locate all storage tanks?"', body_style))
    story.append(Paragraph('4. The AI will provide coordinates for each detected object', body_style))
    
    story.append(Paragraph("<b>Detailed Captions:</b>", heading3_style))
    story.append(Paragraph(
        'Ask: "Generate a detailed caption for this image"',
        body_style
    ))
    story.append(Paragraph(
        "The AI will provide a comprehensive description including:",
        body_style
    ))
    story.append(Paragraph("• Scene composition", body_style))
    story.append(Paragraph("• Major features and structures", body_style))
    story.append(Paragraph("• Colors and textures", body_style))
    story.append(Paragraph("• Spatial relationships", body_style))
    
    story.append(Paragraph("<b>Visual Question Answering (VQA):</b>", heading3_style))
    story.append(Paragraph(
        "Ask specific questions about image attributes:",
        body_style
    ))
    story.append(Paragraph("• Binary: 'Is there a runway in this image?'", body_style))
    story.append(Paragraph("• Numeric: 'How many cars are in the parking lot?'", body_style))
    story.append(Paragraph("• Semantic: 'What is the primary color of the buildings?'", body_style))
    
    story.append(Paragraph("<b>Exporting Results:</b>", heading3_style))
    
    story.append(Paragraph("<b>Export Chat:</b>", body_style))
    story.append(Paragraph("1. Click the 'Export Chat' button at the bottom of the chat panel", body_style))
    story.append(Paragraph("2. A .txt file will be downloaded with the complete conversation", body_style))
    story.append(Paragraph("3. The filename includes the session name and timestamp", body_style))
    
    story.append(Paragraph("<b>Download Image:</b>", body_style))
    story.append(Paragraph("1. Click the download icon in the Image Workspace", body_style))
    story.append(Paragraph("2. The current image will be saved to your downloads folder", body_style))
    
    story.append(Paragraph("<b>Profile Settings:</b>", heading3_style))
    story.append(Paragraph("Access your profile by clicking your avatar in the top-right:", body_style))
    story.append(Paragraph("• Update your name and profile picture", body_style))
    story.append(Paragraph("• Change your password", body_style))
    story.append(Paragraph("• View account statistics (sessions, images analyzed)", body_style))
    story.append(Paragraph("• Manage preferences (theme, notifications)", body_style))
    
    story.append(Paragraph("<b>Keyboard Shortcuts:</b>", heading3_style))
    
    shortcuts_data = [
        ['Action', 'Shortcut'],
        ['Send message', 'Enter'],
        ['New line in message', 'Shift + Enter'],
        ['Focus search', 'Ctrl + F'],
        ['New session', 'Ctrl + N'],
    ]
    shortcuts_table = Table(shortcuts_data, colWidths=[3*inch, 2.5*inch])
    shortcuts_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    story.append(shortcuts_table)
    
    story.append(PageBreak())
    
    # ===================================================================
    # SECTION 6: API REFERENCE
    # ===================================================================
    story.append(Paragraph("6. API Reference", heading1_style))
    
    story.append(Paragraph(
        "This section provides technical details for developers integrating with the GeoNLI API.",
        body_style
    ))
    
    story.append(Paragraph("6.1 GeoNLI Evaluation Endpoint", heading2_style))
    
    story.append(Paragraph("<b>Endpoint:</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="9">POST /geoNLI/eval</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Description:</b>", heading3_style))
    story.append(Paragraph(
        "Performs comprehensive satellite image analysis including caption generation, "
        "object detection, and visual question answering.",
        body_style
    ))
    
    story.append(Paragraph("<b>Request Format:</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="7">{<br/>'
        '  "input_image": {<br/>'
        '    "image_id": "sample1.png",<br/>'
        '    "image_url": "https://example.com/image.png",<br/>'
        '    "metadata": {<br/>'
        '      "width": 512,<br/>'
        '      "height": 512,<br/>'
        '      "spatial_resolution_m": 1.57<br/>'
        '    }<br/>'
        '  },<br/>'
        '  "queries": {<br/>'
        '    "caption_query": {<br/>'
        '      "instruction": "Generate a detailed caption"<br/>'
        '    },<br/>'
        '    "grounding_query": {<br/>'
        '      "instruction": "Locate all storage tanks"<br/>'
        '    },<br/>'
        '    "attribute_query": {<br/>'
        '      "binary": {"instruction": "Are there any digits visible?"},<br/>'
        '      "numeric": {"instruction": "How many storage tanks?"},<br/>'
        '      "semantic": {"instruction": "What color are the tanks?"}<br/>'
        '    }<br/>'
        '  }<br/>'
        '}</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Response Format:</b>", heading3_style))
    story.append(Paragraph(
        "Returns the same structure with 'response' fields populated for each query.",
        body_style
    ))
    
    story.append(Paragraph(
        '<font face="Courier" size="7">{<br/>'
        '  "input_image": { ... },<br/>'
        '  "queries": {<br/>'
        '    "caption_query": {<br/>'
        '      "instruction": "...",<br/>'
        '      "response": "The satellite image shows..."<br/>'
        '    },<br/>'
        '    "grounding_query": {<br/>'
        '      "instruction": "...",<br/>'
        '      "response": [<br/>'
        '        {"object-id": "1", "obbox": [x1,y1,x2,y2,x3,y3,x4,y4]}<br/>'
        '      ]<br/>'
        '    },<br/>'
        '    "attribute_query": {<br/>'
        '      "binary": {"instruction": "...", "response": "Yes"},<br/>'
        '      "numeric": {"instruction": "...", "response": 8.0},<br/>'
        '      "semantic": {"instruction": "...", "response": "White"}<br/>'
        '    }<br/>'
        '  }<br/>'
        '}</font>',
        code_style
    ))
    
    story.append(Paragraph(
        "<b>Note:</b> All queries are optional. You can include any combination based on your needs.",
        note_style
    ))
    
    story.append(PageBreak())
    
    story.append(Paragraph("6.2 Authentication", heading2_style))
    
    story.append(Paragraph("<b>Sign Up:</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="8">POST /api/auth/signup<br/><br/>'
        'Request Body:<br/>'
        '{"email": "user@example.com", "fullName": "John Doe", "password": "pass123"}<br/><br/>'
        'Response: User object with JWT cookie set</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Login:</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="8">POST /api/auth/login<br/><br/>'
        'Request Body:<br/>'
        '{"email": "user@example.com", "password": "pass123"}<br/><br/>'
        'Response: User object with JWT cookie set</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Check Auth:</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="8">GET /api/auth/check<br/><br/>'
        'Headers: Cookie: jwt=&lt;token&gt;<br/><br/>'
        'Response: Current user object</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Logout:</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="8">POST /api/auth/logout<br/><br/>'
        'Headers: Cookie: jwt=&lt;token&gt;<br/><br/>'
        'Response: Success message, JWT cookie cleared</font>',
        code_style
    ))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("6.3 Session Management", heading2_style))
    
    story.append(Paragraph("<b>Create Session:</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="8">POST /api/sessions<br/><br/>'
        'Request Body:<br/>'
        '{"name": "My Analysis", "archived": false, "projectId": null}</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Get All Sessions:</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="8">GET /api/sessions<br/><br/>'
        'Response: Array of session objects</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Update Session:</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="8">PUT /api/sessions/{session_id}<br/><br/>'
        'Request Body:<br/>'
        '{"name": "Updated Name", "archived": true}</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Delete Session:</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="8">DELETE /api/sessions/{session_id}</font>',
        code_style
    ))
    
    story.append(Paragraph(
        "<b>Note:</b> All session endpoints require authentication (JWT cookie).",
        note_style
    ))
    
    story.append(PageBreak())
    
    # ===================================================================
    # SECTION 7: TROUBLESHOOTING
    # ===================================================================
    story.append(Paragraph("7. Troubleshooting", heading1_style))
    
    story.append(Paragraph("7.1 Common Issues", heading2_style))
    
    story.append(Paragraph("<b>Issue: Cannot access the application</b>", heading3_style))
    story.append(Paragraph("<b>Solution:</b>", body_style))
    story.append(Paragraph("• Verify both backend and frontend servers are running", body_style))
    story.append(Paragraph("• Check firewall settings allow connections on ports 5173 and 8000", body_style))
    story.append(Paragraph("• Ensure correct URLs in .env files", body_style))
    story.append(Paragraph("• Try clearing browser cache and cookies", body_style))
    
    story.append(Paragraph("<b>Issue: Login fails with 'Invalid credentials'</b>", heading3_style))
    story.append(Paragraph("<b>Solution:</b>", body_style))
    story.append(Paragraph("• Double-check email and password", body_style))
    story.append(Paragraph("• Passwords are case-sensitive", body_style))
    story.append(Paragraph("• Try resetting your password (if implemented)", body_style))
    story.append(Paragraph("• Verify backend database connection is working", body_style))
    
    story.append(Paragraph("<b>Issue: Images won't upload</b>", heading3_style))
    story.append(Paragraph("<b>Solution:</b>", body_style))
    story.append(Paragraph("• Check file format (only JPEG and PNG supported)", body_style))
    story.append(Paragraph("• Verify file size is under limit (usually 10MB)", body_style))
    story.append(Paragraph("• Ensure you have an active session", body_style))
    story.append(Paragraph("• Check browser console for error messages", body_style))
    story.append(Paragraph("• Verify backend /api/images/upload endpoint is working", body_style))
    
    story.append(Paragraph("<b>Issue: AI responses are slow or timeout</b>", heading3_style))
    story.append(Paragraph("<b>Solution:</b>", body_style))
    story.append(Paragraph("• First request after deployment may take 30-60s (cold start)", body_style))
    story.append(Paragraph("• Subsequent requests should be faster", body_style))
    story.append(Paragraph("• For local deployment, ensure GPU is being utilized", body_style))
    story.append(Paragraph("• Check backend logs for errors", body_style))
    story.append(Paragraph("• Try with a smaller image", body_style))
    
    story.append(Paragraph("<b>Issue: Dark/Light theme not saving</b>", heading3_style))
    story.append(Paragraph("<b>Solution:</b>", body_style))
    story.append(Paragraph("• Check if browser allows localStorage", body_style))
    story.append(Paragraph("• Clear browser cache and try again", body_style))
    story.append(Paragraph("• Ensure cookies are not blocked", body_style))
    story.append(Paragraph("• Try in a different browser", body_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("7.2 Backend Problems", heading2_style))
    
    story.append(Paragraph("<b>MongoDB Connection Error</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="8">Error: ServerSelectionTimeoutError: connection refused</font>',
        code_style
    ))
    story.append(Paragraph("<b>Solutions:</b>", body_style))
    story.append(Paragraph("• Verify MONGODB_URL in .env is correct", body_style))
    story.append(Paragraph("• Check MongoDB Atlas IP whitelist includes your IP", body_style))
    story.append(Paragraph("• For local MongoDB, ensure service is running:", body_style))
    story.append(Paragraph(
        '  <font face="Courier" size="8">sudo systemctl status mongodb</font>',
        code_style
    ))
    story.append(Paragraph("• Test connection with mongosh", body_style))
    
    story.append(Paragraph("<b>CUDA Out of Memory</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="8">RuntimeError: CUDA out of memory</font>',
        code_style
    ))
    story.append(Paragraph("<b>Solutions:</b>", body_style))
    story.append(Paragraph("• Check GPU memory usage: nvidia-smi", body_style))
    story.append(Paragraph("• Close other GPU-intensive applications", body_style))
    story.append(Paragraph("• Reduce batch sizes in .env configuration", body_style))
    story.append(Paragraph("• Switch to CPU mode (slower but works):", body_style))
    story.append(Paragraph(
        '  <font face="Courier" size="8">export CUDA_VISIBLE_DEVICES=""</font>',
        code_style
    ))
    
    story.append(Paragraph("<b>Model Files Not Found</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="8">FileNotFoundError: No such file or directory</font>',
        code_style
    ))
    story.append(Paragraph("<b>Solutions:</b>", body_style))
    story.append(Paragraph("• Verify all three zip files were extracted", body_style))
    story.append(Paragraph("• Check model paths in .env match directory structure", body_style))
    story.append(Paragraph("• Re-extract zip files if needed", body_style))
    story.append(Paragraph("• Ensure sufficient disk space for extraction", body_style))
    
    story.append(Paragraph("<b>Port Already in Use</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="8">OSError: Address already in use</font>',
        code_style
    ))
    story.append(Paragraph("<b>Solutions:</b>", body_style))
    story.append(Paragraph("• Find process using port 8000:", body_style))
    story.append(Paragraph(
        '  <font face="Courier" size="8">lsof -i :8000</font>',
        code_style
    ))
    story.append(Paragraph("• Kill the process:", body_style))
    story.append(Paragraph(
        '  <font face="Courier" size="8">kill -9 &lt;PID&gt;</font>',
        code_style
    ))
    story.append(Paragraph("• Or use a different port in .env", body_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("7.3 Frontend Problems", heading2_style))
    
    story.append(Paragraph("<b>Blank Screen After Login</b>", heading3_style))
    story.append(Paragraph("<b>Solutions:</b>", body_style))
    story.append(Paragraph("• Open browser console (F12) and check for errors", body_style))
    story.append(Paragraph("• Verify VITE_BACKEND_URL in .env is correct", body_style))
    story.append(Paragraph("• Clear browser cache (Ctrl+Shift+Delete)", body_style))
    story.append(Paragraph("• Clear localStorage: Open console and run:", body_style))
    story.append(Paragraph(
        '  <font face="Courier" size="8">localStorage.clear()</font>',
        code_style
    ))
    story.append(Paragraph("• Verify backend is accessible from frontend", body_style))
    
    story.append(Paragraph("<b>CORS Errors</b>", heading3_style))
    story.append(Paragraph(
        '<font face="Courier" size="8">Access to XMLHttpRequest blocked by CORS policy</font>',
        code_style
    ))
    story.append(Paragraph("<b>Solutions:</b>", body_style))
    story.append(Paragraph("• Add frontend URL to CORS allowed origins in backend server.py", body_style))
    story.append(Paragraph("• Ensure FRONTEND_URL in backend .env matches actual frontend URL", body_style))
    story.append(Paragraph("• Restart backend after configuration changes", body_style))
    story.append(Paragraph("• For Modal deployment, update CORS settings in deployed app", body_style))
    
    story.append(Paragraph("<b>Build Failures</b>", heading3_style))
    story.append(Paragraph("<b>Solutions:</b>", body_style))
    story.append(Paragraph("• Delete node_modules and package-lock.json", body_style))
    story.append(Paragraph("• Run npm install again", body_style))
    story.append(Paragraph("• Verify Node.js version is compatible (v20+)", body_style))
    story.append(Paragraph("• Check for syntax errors in code", body_style))
    story.append(Paragraph("• Clear Vite cache:", body_style))
    story.append(Paragraph(
        '  <font face="Courier" size="8">rm -rf dist node_modules/.vite</font>',
        code_style
    ))
    
    story.append(PageBreak())
    
    # ===================================================================
    # SECTION 8: BEST PRACTICES
    # ===================================================================
    story.append(Paragraph("8. Best Practices", heading1_style))
    
    story.append(Paragraph("<b>Image Quality:</b>", heading3_style))
    story.append(Paragraph("• Use high-resolution satellite images for best results", body_style))
    story.append(Paragraph("• Ensure images are clear and not heavily compressed", body_style))
    story.append(Paragraph("• Optimal resolution: 512x512 pixels or higher", body_style))
    story.append(Paragraph("• Avoid images with excessive noise or artifacts", body_style))
    
    story.append(Paragraph("<b>Asking Questions:</b>", heading3_style))
    story.append(Paragraph("• Be specific in your questions", body_style))
    story.append(Paragraph("• Use clear, descriptive language", body_style))
    story.append(Paragraph("• Ask one question at a time for best accuracy", body_style))
    story.append(Paragraph("• Provide context when asking follow-up questions", body_style))
    story.append(Paragraph("• Use object-specific terminology (e.g., 'storage tanks' vs 'round things')", body_style))
    
    story.append(Paragraph("<b>Session Organization:</b>", heading3_style))
    story.append(Paragraph("• Create separate sessions for different analysis tasks", body_style))
    story.append(Paragraph("• Use descriptive session names (e.g., 'Urban Area Analysis - January 2025')", body_style))
    story.append(Paragraph("• Archive completed sessions to keep workspace clean", body_style))
    story.append(Paragraph("• Export important conversations before deleting sessions", body_style))
    story.append(Paragraph("• Regularly clean up unused sessions", body_style))
    
    story.append(Paragraph("<b>Performance Optimization:</b>", heading3_style))
    story.append(Paragraph("• Close unused browser tabs to free memory", body_style))
    story.append(Paragraph("• Use the latest browser version for best performance", body_style))
    story.append(Paragraph("• On slow connections, wait for complete upload before querying", body_style))
    story.append(Paragraph("• For batch processing, use the API directly instead of UI", body_style))
    
    story.append(Paragraph("<b>Security:</b>", heading3_style))
    story.append(Paragraph("• Use strong, unique passwords", body_style))
    story.append(Paragraph("• Log out when using shared computers", body_style))
    story.append(Paragraph("• Don't share your account credentials", body_style))
    story.append(Paragraph("• For production deployments, use HTTPS", body_style))
    story.append(Paragraph("• Regularly update passwords", body_style))
    
    story.append(Paragraph("<b>Data Management:</b>", heading3_style))
    story.append(Paragraph("• Export important analysis results regularly", body_style))
    story.append(Paragraph("• Keep backup copies of original images", body_style))
    story.append(Paragraph("• Document your analysis methodology in session names/notes", body_style))
    story.append(Paragraph("• Consider data retention policies for sensitive imagery", body_style))
    
    story.append(PageBreak())
    
    # ===================================================================
    # SECTION 9: SUPPORT & RESOURCES
    # ===================================================================
    story.append(Paragraph("9. Support & Resources", heading1_style))
    
    story.append(Paragraph("<b>Documentation:</b>", heading3_style))
    story.append(Paragraph("• Backend README: Comprehensive backend setup guide", body_style))
    story.append(Paragraph("• Frontend README: Complete frontend documentation", body_style))
    story.append(Paragraph("• API Documentation: Interactive API docs at /docs endpoint", body_style))
    story.append(Paragraph("• Modal Deployment Guide: Cloud deployment instructions", body_style))
    
    story.append(Paragraph("<b>Interactive API Documentation:</b>", heading3_style))
    story.append(Paragraph(
        "When the backend is running, access interactive API documentation:",
        body_style
    ))
    story.append(Paragraph("• Swagger UI: http://localhost:8000/docs", body_style))
    story.append(Paragraph("• ReDoc: http://localhost:8000/redoc", body_style))
    
    story.append(Paragraph("<b>Example Files:</b>", heading3_style))
    story.append(Paragraph("• example_requests.json - Sample API requests", body_style))
    story.append(Paragraph("• integration_example.py - Python integration code", body_style))
    story.append(Paragraph("• modal_client.py - Modal API client", body_style))
    story.append(Paragraph("• test_modal.sh - Testing script", body_style))
    
    story.append(Paragraph("<b>Technology Stack:</b>", heading3_style))
    
    tech_data = [
        ['Component', 'Technology', 'Version'],
        ['Backend', 'FastAPI + Python', '0.121.3 / 3.11'],
        ['Frontend', 'React + Vite', '19.0.0 / 7.2.4'],
        ['Database', 'MongoDB', '4.4+'],
        ['AI Models', 'Florence-2, GeoGround, YOLO', '-'],
        ['State Management', 'Zustand', '5.0.3'],
        ['Styling', 'Tailwind CSS', '4.1.4'],
        ['Cloud', 'Modal (optional)', '-'],
    ]
    tech_table = Table(tech_data, colWidths=[1.5*inch, 2.5*inch, 1.3*inch])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>External Resources:</b>", heading3_style))
    story.append(Paragraph("• FastAPI: https://fastapi.tiangolo.com", body_style))
    story.append(Paragraph("• React: https://react.dev", body_style))
    story.append(Paragraph("• MongoDB Atlas: https://www.mongodb.com/cloud/atlas", body_style))
    story.append(Paragraph("• Modal: https://modal.com/docs", body_style))
    story.append(Paragraph("• Florence-2: https://huggingface.co/microsoft/Florence-2-large", body_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("<b>Need Help?</b>", heading3_style))
    story.append(Paragraph(
        "If you encounter issues not covered in this guide:",
        body_style
    ))
    story.append(Paragraph("1. Check the Troubleshooting section (Section 7)", body_style))
    story.append(Paragraph("2. Review backend/frontend README files", body_style))
    story.append(Paragraph("3. Check browser console for error messages", body_style))
    story.append(Paragraph("4. Review backend logs for detailed error information", body_style))
    story.append(Paragraph("5. Consult the interactive API documentation", body_style))
    
    story.append(PageBreak())
    
    # ===================================================================
    # APPENDIX: QUICK REFERENCE
    # ===================================================================
    story.append(Paragraph("Appendix: Quick Reference", heading1_style))
    
    story.append(Paragraph("<b>Common Commands:</b>", heading3_style))
    
    commands_data = [
        ['Task', 'Command'],
        ['Start Backend (Local)', 'python src/server.py'],
        ['Start Frontend (Dev)', 'npm run dev'],
        ['Build Frontend', 'npm run build'],
        ['Deploy to Modal', 'modal deploy modal_app.py'],
        ['View Modal Logs', 'modal app logs multi-model-env-backend --follow'],
        ['Test Health', 'curl http://localhost:8000/health'],
        ['Generate JWT Secret', 'openssl rand -hex 32'],
    ]
    commands_table = Table(commands_data, colWidths=[2.3*inch, 3.5*inch])
    commands_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    story.append(commands_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>Default Ports:</b>", heading3_style))
    story.append(Paragraph("• Backend: 8000", body_style))
    story.append(Paragraph("• Frontend: 5173", body_style))
    story.append(Paragraph("• MongoDB (local): 27017", body_style))
    
    story.append(Paragraph("<b>Important File Locations:</b>", heading3_style))
    story.append(Paragraph("• Backend .env: multi-model-env-backend/.env", body_style))
    story.append(Paragraph("• Frontend .env: frontend/.env", body_style))
    story.append(Paragraph("• Backend logs: Terminal output or logs/", body_style))
    story.append(Paragraph("• Uploaded images: multi-model-env-backend/uploads/", body_style))
    
    story.append(Paragraph("<b>Deployment Checklist:</b>", heading3_style))
    
    checklist_items = [
        "Python 3.10/3.11 installed",
        "Node.js v20+ installed",
        "MongoDB configured (Atlas or local)",
        "All three model zip files downloaded",
        "Backend .env file created and configured",
        "Frontend .env file created and configured",
        "JWT secret generated",
        "Backend dependencies installed (pip install -r requirements.txt)",
        "Frontend dependencies installed (npm install)",
        "Model environments extracted (for local) or zipped (for Modal)",
        "Backend server started and health check passes",
        "Frontend server started and accessible",
        "Login/Signup working correctly",
        "Image upload working",
        "AI responses working",
    ]
    
    for item in checklist_items:
        story.append(Paragraph(f"☐ {item}", body_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Final page
    story.append(Paragraph("End of User Guide", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "Thank you for using GeoNLI! We hope this guide helps you get the most out of the platform.",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "For the latest updates and additional resources, please refer to the project documentation.",
        body_style
    ))
    
    # Build PDF
    doc.build(story)
    print("✅ User Guide PDF created successfully!")
    print("📄 Location: /mnt/user-data/outputs/User_Guide.pdf")

if __name__ == "__main__":
    create_user_guide()