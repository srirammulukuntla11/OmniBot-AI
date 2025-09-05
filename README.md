🤖 OmniBot AI – Your All-in-One Virtual Assistant

OmniBot AI is an **AI-powered Virtual Assistant** built using **Flask**.  
It can chat, solve math problems, fetch information from Wikipedia, generate stories, provide disease information, detect objects in images, and even process uploaded files.  

🚀 Features
🤖 Chatbot Capabilities
- Small talk & greetings
- Current time & affairs
- Wikipedia integration (`who is`, `what is`, `about`, and follow-ups)
- Story generation
- Predefined **Python program snippets** (from `programs.json`)

📊 Math Solver
- Basic arithmetic (`+ - * / %`)
- Advanced math using **SymPy**:
  - Solve equations
  - Differentiation
  - Integration
  - Simplification
  - Limits

🩺 Health Assistant
- Information on common diseases:
  - Cold, Fever, COVID-19, Malaria, Diabetes, Hypertension, Headache

🖼️ Image Processing
- **Image Captioning** using [BLIP](https://huggingface.co/Salesforce/blip-image-captioning-base)
- **Object Detection** (Faster R-CNN)
- **Image Segmentation** (DeepLabV3)
- **Weapon Detection** from captions (gun, knife, rifle, etc.)
- Returns both captions and segmented results

📂 File Handling
- Upload and read:
  - **PDF** (via PyPDF2)
  - **DOCX** (via python-docx)
  - **TXT** files

🔊 Voice Integration
- Speech synthesis with `pyttsx3`
- Can be extended for mute/unmute and male/female voice selection

📂 Project Structure

├── segmentation.py   # Flask app with object detection + file handling

├── hi.py             # Flask app with segmentation + story + extended logic

├── programs.json     # Predefined Python program snippets

├── templates/

 └── index.html    # Chat UI (if implemented)

⚡ Installation
1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-chatbot.git
cd ai-chatbot
````

2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows
```

3. Install Dependencies

```bash
pip install -r requirements.txt
```

*(Create `requirements.txt` with all used libraries: Flask, sympy, wikipedia, pytesseract, pillow, pyttsx3, torch, transformers, torchvision, PyPDF2, python-docx, matplotlib, numpy)*

4. Run the App

```bash
python hi.py
```

or

```bash
python segmentation.py
```

The app runs at: **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

🎯 Example Queries
* "What is your name?"
* "Solve x^2 + 2x - 3 = 0"
* "Differentiate x^3 + 2x"
* "About Albert Einstein"
* "Tell me a story"
* "Bubble sort program"
* Upload an image/PDF/DOCX/TXT
  
📌 Future Enhancements
* Add authentication system
* Store chat history (memory)
* Integrate real-time news APIs
* Improve UI/UX with better design
* Cloud deployment (Heroku, Render, or AWS)

📜 License
This project is licensed under the **MIT License** – feel free to use and modify.

🙌 Acknowledgements
* [Flask](https://flask.palletsprojects.com/)
* [PyTorch](https://pytorch.org/)
* [Hugging Face Transformers](https://huggingface.co/)
* [SymPy](https://www.sympy.org/)
* [Wikipedia API](https://pypi.org/project/wikipedia/)



👉 Do you want me to also generate a **`requirements.txt`** file automatically from your imports? That way, your project will be ready-to-run on GitHub.
```
