from flask import Flask, request, render_template_string, jsonify
import requests
import json

app = Flask(__name__)


def get_profile(token: str) -> str:
    """Fetch user profile by token and return email."""
    headers = {'Accept': 'application/json', 'Authorization': f'Bearer {token}'}
    url = 'https://api.test.profcomff.com/auth/me?info=auth_methods'
    response = requests.get(url, headers=headers)

    # Check the status code of the response
    if response.status_code == 200:
        # Attempt to extract the email address
        email = response.json().get('email', 'No email found')
        return email
    else:
        # Handle possible errors or different responses
        return 'Error retrieving profile information.'


def ru_eng(text: str) -> str:
    text = 'Translate to eng: ' + text
    API_URL = "https://api-inference.huggingface.co/models/utrobinmv/t5_translate_en_ru_zh_large_1024"
    headers = {"Authorization": "Bearer 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"}
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    response_data = response.json()
    translated_text = response_data[0]['translation_text']
    if 'Translate to eng:' in translated_text:
        translated_text = translated_text.replace('Translate to eng:', '')
    return translated_text


def eng_ru(text: str) -> str:
    API_URL = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-ru"
    headers = {"Authorization": "Bearer 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"}
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    return response.json()[0]['translation_text']


def _per(text: str) -> str:
    eng_data = ru_eng(text)
    ru_data = eng_ru(eng_data)
    return ru_data


def _data(text: str) -> list:
    words = text.split()
    max_length = 20
    return [' '.join(words[i:i + max_length]) for i in range(0, len(words), max_length)]


def frase(text: str) -> str:
    parts = _data(text)
    paraphrased_texts = [_per(part) for part in parts]
    final_output = " ".join(paraphrased_texts)
    return final_output


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        text = request.form['text']
        result = frase(text)
        return render_template_string(HTML_TEMPLATE, original_text=text, translated_text=result)
    return render_template_string(HTML_TEMPLATE, original_text='', translated_text='')


@app.route('/get-email')
def get_email():
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Token is required"}), 400
    email = get_profile(token)
    return jsonify({"email": email})


HTML_TEMPLATE = '''




<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Translation and Paraphrasing Tool</title>
    <style>
        body, html {
            height: 100%;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Helvetica', sans-serif;
            background-color: darkgray;
        }
        .phone {
            width: 80vw;

            height: 70vh; /* Typical height of a mobile phone */
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            border-radius: 20px;
            padding: 20px 20px;
        }
        form {
            width: 100%;

            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }
        textarea {
            flex-grow: 1;

            margin-bottom: 10px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 10px;
            resize: none;
        }
        button {
            padding: 10px 20px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #0056b3;
        }
        h1, h2 {
            width: 100%;
            text-align: center;
        }
        p {
            width: 100%;
            background: #f8f8f8;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: auto;
            margin-top: 5px;
        }
    </style>
</head>
<body>
<div class="phone">
    <h1>Сервис: "Другими словами"</h1>
    <form method="post">
        <textarea name="text" placeholder="Введите текст.. Наш сервис позволит вам перефразировать ваш текст, найти новые идеи.
И конечно же, объяснить всё «Другими словами»"></textarea>
        <button type="submit">Отправить</button>
    </form>

    <h2>Результат:</h2>
    <p>{{ translated_text }}</p>
</div>
</body>
</html>


'''

if __name__ == '__main__':
    app.run(debug=True)
