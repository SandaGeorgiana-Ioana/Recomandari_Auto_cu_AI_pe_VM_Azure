from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from reportlab.pdfgen import canvas


client = openai.OpenAI(api_key="")

app = Flask(__name__)
CORS(app)


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    prompt = generate_prompt(data)
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        recomandari = response.choices[0].message.content
        pdf_path = generate_pdf(data, recomandari)
        return jsonify({"recommendations": recomandari, "pdf_url": pdf_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_prompt(data):
    prompt = f"""
Recomandă 3 mașini în funcție de:
- Buget: {data['buget']} €
- Pasageri: {data['adulti']} adulți, {data['copii']} copii
- Mărci preferate: {", ".join(data['marci']) if data['marci'] else "—"}
- Caroserie: {data['tip']} | Combustibil: {data['combustibil']} | Transmisie: {data['cutie']}
- Consum țintă: {data['consum']} L/100km
- Siguranță minimă: {data['siguranta']}%
- Interior: {data['interior']} | Culoare: {data['culoare']}
- Dotări dorite: {", ".join(data['dotari']) if data['dotari'] else "—"}
- Senzori activi: {", ".join(data.get('senzoriActivi', [])) if data.get('senzoriActivi') else "—"}
- Senzori pasivi: {", ".join(data.get('senzoriPasivi', [])) if data.get('senzoriPasivi') else "—"}
- Producători senzori: {", ".join(data.get('producatoriSenzori', [])) if data.get('producatoriSenzori') else "—"}
- Priorități: {data['prioritati']}

Răspunde cu 3 opțiuni în format:
1. Model – descriere
De ce se potrivește: ...
- Siguranță/ADAS: ...
- Consum estimat: ...
- Puncte forte: • ... • ... • ...
-Puncte slabe:
"""
    return prompt


def generate_pdf(data, recomandari):
    path = "recomandari_ai.pdf"
    c = canvas.Canvas(path)
    y = 800

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Preferințe utilizator:")
    y -= 20
    c.setFont("Helvetica", 11)

    c.drawString(50, y, f"Buget: {data['buget']} €, Adulti: {data['adulti']}, Copii: {data['copii']}")
    y -= 15
    c.drawString(50, y, f"Mărci: {', '.join(data['marci'])}")
    y -= 15
    c.drawString(50, y, f"Tip: {data['tip']}, Combustibil: {data['combustibil']}, Transmisie: {data['cutie']}")
    y -= 15
    c.drawString(50, y, f"Consum: {data['consum']} L/100km, Siguranță: {data['siguranta']}%")
    y -= 15
    c.drawString(50, y, f"Interior: {data['interior']}, Culoare: {data['culoare']}")
    y -= 15
    c.drawString(50, y, f"Dotări: {', '.join(data['dotari'])}")
    y -= 15
    c.drawString(50, y, f"Priorități: {data['prioritati']}")
    y -= 30

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Recomandări AI:")
    y -= 20
    c.setFont("Helvetica", 11)

    for line in recomandari.splitlines():
        c.drawString(50, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            y = 800

    c.save()
    return path


if __name__ == "__main__":
    app.run(debug=True)
