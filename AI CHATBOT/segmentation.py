from flask import Flask, request, jsonify, render_template
import datetime
import re
import json
from sympy import symbols, Eq, solve, simplify, diff, integrate, limit, sympify
import wikipedia
import pytesseract
from PIL import Image
import pyttsx3
import io
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PyPDF2 import PdfReader
import docx
import torchvision.transforms as T
from torchvision import models

app = Flask(__name__)

# --- Load Code Snippets from JSON ---
with open('programs.json') as f:
    code_snippets = json.load(f)

# --- Memory for Wikipedia context ---
last_wiki_topic = {"topic": None, "offset": 0}

# --- Image Captioning Setup ---
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# --- Object Detection Model Setup (YOLO or FasterRCNN) ---
# Load a pre-trained Faster R-CNN model for object detection
detection_model = models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
detection_model.eval()

def get_image_caption(image: Image.Image) -> str:
    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption

# --- Basic Math Expression Evaluation ---
def evaluate_math_expression(expression):
    try:
        expression = expression.lower()
        expression = expression.replace("plus", "+").replace("minus", "-")
        expression = expression.replace("x", "*").replace("into", "*")
        expression = expression.replace("divided by", "/").replace("mod", "%")
        if re.match(r"^[\d\s\+\-\*/%\.\(\)]+$", expression):
            result = eval(expression)
            return f"The answer is: {result}"
        return None
    except Exception:
        return None

# --- Advanced Math Solver ---
def advanced_math_solver(expression):
    try:
        x = symbols('x')
        expression = expression.lower().replace("^", "**")

        if "solve" in expression:
            eq = expression.replace("solve", "").strip()
            lhs, rhs = eq.split("=")
            equation = Eq(sympify(lhs), sympify(rhs))
            result = solve(equation, x)
            return f"Solution: {result}"
        elif "differentiate" in expression or "derivative" in expression:
            expr = expression.replace("differentiate", "").replace("derivative", "").strip()
            return f"Derivative: {diff(sympify(expr))}"
        elif "integrate" in expression:
            expr = expression.replace("integrate", "").strip()
            return f"Integral: {integrate(sympify(expr))}"
        elif "simplify" in expression:
            expr = expression.replace("simplify", "").strip()
            return f"Simplified: {simplify(sympify(expr))}"
        elif "limit" in expression:
            expr = expression.replace("limit", "").strip()
            return f"Limit as x approaches ∞: {limit(sympify(expr), x, float('inf'))}"
        return None
    except Exception:
        return "Sorry, I couldn't solve that. Try checking your expression."

# --- Disease Info Handler ---
def get_disease_info(message):
    disease_data = {
        "cold": {
            "name": "Common Cold",
            "symptoms": "Runny nose, sore throat, cough, congestion, slight body aches.",
            "cause": "Caused by a viral infection (usually rhinovirus).",
            "treatment": "Rest, hydration, and over-the-counter cold medications.",
            "severity": "Mild"
        },
        "fever": {
            "name": "Fever",
            "symptoms": "High body temperature, chills, sweating, headache, body aches.",
            "cause": "Usually due to an infection (bacterial or viral).",
            "treatment": "Stay hydrated, take paracetamol or ibuprofen, and rest.",
            "severity": "Mild to Moderate"
        },
        "covid": {
            "name": "COVID-19",
            "symptoms": "Fever, cough, fatigue, shortness of breath, loss of taste or smell.",
            "cause": "Caused by SARS-CoV-2 virus, spreads through droplets.",
            "treatment": "Isolation, monitoring symptoms, and seeking medical help if needed.",
            "severity": "Varies from Mild to Severe"
        },
        "malaria": {
            "name": "Malaria",
            "symptoms": "Fever, chills, vomiting, headache, muscle pain.",
            "cause": "Spread by Anopheles mosquitoes carrying Plasmodium parasite.",
            "treatment": "Antimalarial medications prescribed by doctors.",
            "severity": "Moderate to Severe"
        },
        "diabetes": {
            "name": "Diabetes",
            "symptoms": "Increased thirst, frequent urination, fatigue, blurred vision.",
            "cause": "High blood sugar due to insulin issues (Type 1 or 2).",
            "treatment": "Managed with medication, insulin, diet control, and exercise.",
            "severity": "Chronic"
        },
        "hypertension": {
            "name": "Hypertension",
            "symptoms": "Often silent, may include headache, shortness of breath, or nosebleeds.",
            "cause": "High pressure in the arteries. Risk factor for heart disease.",
            "treatment": "Lifestyle changes and antihypertensive drugs.",
            "severity": "Chronic"
        },
        "headache": {
            "name": "Headache",
            "symptoms": "Pain in head, scalp, or neck. Can be dull or sharp.",
            "cause": "Stress, dehydration, sinus issues, eye strain, or more serious causes.",
            "treatment": "Rest, hydration, and over-the-counter pain relievers.",
            "severity": "Mild to Moderate"
        }
    }

    for keyword, info in disease_data.items():
        if keyword in message:
            return (
                f"🩺 *{info['name']}*\n"
                f"- **Symptoms**: {info['symptoms']}\n"
                f"- **Cause**: {info['cause']}\n"
                f"- **Treatment**: {info['treatment']}\n"
                f"- **Severity**: {info['severity']}"
            )
    return None

# --- Object Detection ---
def detect_objects(image: Image.Image):
    transform = T.Compose([T.ToTensor()])
    img_tensor = transform(image).unsqueeze(0)
    
    with torch.no_grad():
        predictions = detection_model(img_tensor)

    labels = predictions[0]['labels']
    scores = predictions[0]['scores']
    boxes = predictions[0]['boxes']

    detected_objects = []
    object_count = 0
    for label, score in zip(labels, scores):
        if score > 0.5:  # confidence threshold
            object_count += 1
            detected_objects.append(f"Object: {label.item()}, Confidence: {score.item():.2f}")

    return object_count, detected_objects

# --- File Reading Functions ---
def read_pdf_file(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def read_docx_file(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def read_txt_file(file):
    return file.read().decode("utf-8")

# --- Image Recognition and Captioning ---
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file') or request.files.get('image')
    if file:
        filename = file.filename.lower()
        try:
            # Handling image captioning
            if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp')): 
                img = Image.open(io.BytesIO(file.read()))
                caption = get_image_caption(img)

                # Weapon detection logic - Check for weapon-related keywords in caption
                weapons = ["gun", "knife", "pistol", "bomb", "rifle"]
                detected_weapons = [weapon for weapon in weapons if weapon in caption.lower()]

                if detected_weapons:
                    # Add a warning to the caption if a weapon is detected
                    warning_message = f"⚠️ Warning: Possible weapon detected ({', '.join(detected_weapons)})."
                    caption = warning_message + "\n" + caption

                # Object segmentation and counting
                object_count, detected_objects = detect_objects(img)
                caption += f"\nDetected objects: {object_count}. Objects: {', '.join(detected_objects)}"

                return jsonify({"caption": caption})

            # Handling text files (PDF, DOCX, TXT)
            elif filename.endswith('.pdf'):
                content = read_pdf_file(file)
                return jsonify({"type": "text", "result": content})
            elif filename.endswith('.docx'):
                content = read_docx_file(file)
                return jsonify({"type": "text", "result": content})
            elif filename.endswith('.txt'):
                content = read_txt_file(file)
                return jsonify({"type": "text", "result": content})
            else:
                return jsonify({"status": "error", "message": "Unsupported file type"})
        
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    
    return jsonify({"status": "no file uploaded"})

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    reply = assistant_logic(user_message)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
