import threading
import webbrowser
from flask import Flask, render_template_string, request

app = Flask(__name__)

def refactor_code(original_code):
    if "def compute_squares" in original_code:
        optimized_func = """
def compute_squares(numbers):
    # Refactored with list comprehension for better performance
    return [x * x for x in numbers]
"""
        start = original_code.find("def compute_squares")
        end = original_code.find("def ", start + 1)
        if end == -1:
            end = len(original_code)
        refactored_code = original_code[:start] + optimized_func + original_code[end:]
        return refactored_code.strip()
    return original_code

@app.route('/', methods=['GET', 'POST'])
def index():
    original = ""
    refactored = ""
    if request.method == 'POST':
        file = request.files.get('codefile')
        if file:
            original = file.read().decode('utf-8', errors='ignore')
            refactored = refactor_code(original)

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Code Refactoring & Optimization Demo</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap');

    body {
        font-family: 'Roboto Mono', monospace;
        background: #1e1e2f;
        color: #cdd6f4;
        margin: 0;
        padding: 0 20px;
    }
    header {
        text-align: center;
        padding: 30px 10px 10px;
        color: #89b4fa;
    }
    form {
        background: #313244;
        max-width: 700px;
        margin: 20px auto;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(100, 100, 150, 0.5);
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    input[type="file"] {
        padding: 10px;
        background: #45475a;
        border: none;
        border-radius: 8px;
        color: #cdd6f4;
        width: 100%;
        max-width: 400px;
        margin-bottom: 20px;
        cursor: pointer;
        transition: background 0.3s ease;
    }
    input[type="file"]:hover {
        background: #585b70;
    }
    button {
        background: #89b4fa;
        color: #1e1e2f;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 12px 25px;
        cursor: pointer;
        font-size: 16px;
        transition: background 0.3s ease;
        width: 180px;
    }
    button:hover {
        background: #62a0f8;
    }
    .code-container {
        max-width: 900px;
        margin: 30px auto;
        background: #313244;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(100, 100, 150, 0.5);
        overflow-x: auto;
    }
    label {
        font-size: 18px;
        margin-bottom: 8px;
        color: #f5c2e7;
        display: block;
        font-weight: 600;
    }
    pre {
        background: #181825;
        padding: 15px;
        border-radius: 10px;
        white-space: pre-wrap;
        word-break: break-word;
        font-size: 14px;
        line-height: 1.5;
        color: #f2cdcd;
    }
    @media (max-width: 600px) {
        button {
            width: 100%;
        }
        input[type="file"] {
            max-width: 100%;
        }
    }
</style>
</head>
<body>
<header>
    <h1>Code Refactoring & Performance Optimization Demo</h1>
    <p>Upload a Python file with <code>compute_squares</code> function to see refactoring results.</p>
</header>
<form method="post" enctype="multipart/form-data">
    <input type="file" name="codefile" accept=".py" required />
    <button type="submit">Upload & Refactor</button>
</form>

{% if original %}
<div class="code-container">
    <label>Original Code:</label>
    <pre>{{ original }}</pre>
</div>
<div class="code-container">
    <label>Refactored & Optimized Code:</label>
    <pre>{{ refactored }}</pre>
</div>
{% endif %}

</body>
</html>
""", original=original, refactored=refactored)


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(debug=True)
