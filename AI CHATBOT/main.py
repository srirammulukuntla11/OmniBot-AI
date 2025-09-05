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
import random

app = Flask(__name__)

# --- Load Code Snippets from JSON ---
with open('programs.json') as f:
    code_snippets = json.load(f)

# --- Memory for Wikipedia context ---
last_wiki_topic = {"topic": None, "offset": 0}

# --- Image Captioning Setup ---
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def get_image_caption(image: Image.Image) -> str:
    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption

# --- Story Generation --- 
def generate_story(key_points):
    # Predefined templates or story arcs
    story_templates = [
        "Once upon a time, there was a {character} who was {adjective}. One day, they discovered {discovery}. This discovery led them on a journey to {destination}, where they encountered {obstacle}. With determination and courage, they overcame the obstacle and {resolution}.",
        "In a distant land, a {character} set out on an adventure to {goal}. Along the way, they faced many challenges, including {challenge}. But through wisdom and bravery, they succeeded in {achievement}. Their journey became a legend, known far and wide as the {story_name}.",
        "A {adjective} {character} found themselves caught in an unexpected situation. While trying to {action}, they stumbled upon {discovery}. This started a chain of events that led to {unexpected_turn}. In the end, they learned {lesson}, and their life was changed forever."
    ]

    # Example dynamic parts based on input key points
    story_data = {
        "character": "knight" if "knight" in key_points else "hero",
        "adjective": "brave" if "brave" in key_points else "kind",
        "discovery": "a hidden treasure" if "treasure" in key_points else "a powerful artifact",
        "destination": "a distant castle" if "castle" in key_points else "an enchanted forest",
        "obstacle": "a dangerous dragon" if "dragon" in key_points else "an evil sorcerer",
        "resolution": "became a legend" if "legend" in key_points else "defeated the dark forces",
        "goal": "defeat the evil forces" if "evil" in key_points else "find a rare artifact",
        "challenge": "treacherous terrain" if "terrain" in key_points else "a fierce monster",
        "achievement": "saving the kingdom" if "kingdom" in key_points else "finding the treasure",
        "story_name": "The Brave Knight's Quest" if "knight" in key_points else "The Hero's Journey",
        "action": "fight the sorcerer" if "fight" in key_points else "seek the hidden treasure",
        "unexpected_turn": "they realized the treasure was cursed" if "cursed" in key_points else "they were betrayed by an ally",
        "lesson": "the true meaning of courage" if "courage" in key_points else "the importance of friendship"
    }

    # Randomly choose a template and fill it with dynamic data
    story_template = random.choice(story_templates)
    story = story_template.format(**story_data)

    return story

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

# --- Program Snippet Handler ---
def get_program_snippet(message):
    for key in code_snippets:
        if key.lower() in message.lower():
            return f"Here is the {key} program:\n```python\n{code_snippets[key]}\n```"
    return None

# --- Wikipedia Info ---
def get_wikipedia_info(query, more=False):
    try:
        if not more:
            last_wiki_topic["topic"] = query
            last_wiki_topic["offset"] = 0
        else:
            query = last_wiki_topic["topic"]
            last_wiki_topic["offset"] += 2

        if not query:
            return "Please ask about a topic first."

        summary = wikipedia.summary(query, sentences=last_wiki_topic["offset"] + 2)
        paragraphs = summary.split(". ")
        start = last_wiki_topic["offset"]
        end = start + 2
        more_info = ". ".join(paragraphs[start:end])
        return more_info if more_info else "No more information available."
    except Exception:
        return "Sorry, I couldn't find information on that topic."

# --- Assistant Logic ---
def assistant_logic(send):
    data_btn = send.lower()

    if "what is your name" in data_btn:
        return "My name is Virtual Assistant"
    elif any(greet in data_btn for greet in ["hello", "hye", "hay", "hi"]):
        return "Hey sir, how can I help you!"
    elif "how are you" in data_btn:
        return "I am doing great these days, sir."
    elif "thanku" in data_btn or "thank" in data_btn:
        return "It's my pleasure, sir, to stay with you."
    elif "good morning" in data_btn:
        return "Good morning sir, I think you might need some help."
    elif "time now" in data_btn:
        now = datetime.datetime.now()
        return now.strftime("Current time is %I:%M %p")
    elif "current affairs" in data_btn:
        return (
            "📰 Here are some current affairs (April 7, 2025):\n"
            "- India and Japan sign defense cooperation pact.\n"
            "- ISRO announces launch of Chandrayaan-4 in December.\n"
            "- Stock markets see record high this week.\n"
            "- NASA confirms water traces on Europa.\n"
            "- T20 World Cup preparations begin across nations."
        )
    elif "open youtube" in data_btn:
        return "OPEN_YOUTUBE"
    elif "open google" in data_btn:
        return "OPEN_GOOGLE"
    elif "open facebook" in data_btn:
        return "OPEN_FACEBOOK"
    elif "open sbtet" in data_btn:
        return "OPEN_SBTET"
    elif "open music" in data_btn:
        return "OPEN_MUSIC"
    elif "shutdown" in data_btn or "quit" in data_btn:
        return "Ok sir. Shutting down."

    if data_btn.startswith(("about ", "who is ", "what is ")):
        topic = data_btn.replace("about", "").replace("who is", "").replace("what is", "").strip()
        return get_wikipedia_info(topic, more=False)
    elif "more about him" in data_btn or "more about her" in data_btn:
        return get_wikipedia_info("", more=True)

    program_result = get_program_snippet(data_btn)
    if program_result:
        return program_result

    basic_result = evaluate_math_expression(data_btn)
    if basic_result:
        return basic_result

    advanced_result = advanced_math_solver(data_btn)
    if advanced_result:
        return advanced_result

    disease_result = get_disease_info(data_btn)
    if disease_result:
        return disease_result

    # Check if the user wants a story and call the story generator
    if "tell me a story" in data_btn:
        key_points = {"character": "young prince", "setting": "magical forest", "conflict": "an evil dragon", "resolution": "outsmarting the dragon using clever tricks"}
        story = generate_story(key_points)
        return story

    return "Sorry, I didn’t understand that. Try asking about diseases, math problems, or say 'open YouTube' or upload a file or image."

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
