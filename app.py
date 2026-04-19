from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    html_content = data.get('html')
    css_content = data.get('css')
    
    # İlerleyen aşamalarda PyGithub kütüphanesi kullanarak 
    # bu çıktıları doğrudan kullanıcının GitHub sayfasına (GitHub Pages) pushlayabilirsin.
    
    # Şimdilik sunucuya geçici bir HTML dosyası olarak kaydediyoruz.
    with open('generated_site.html', 'w', encoding='utf-8') as f:
        f.write(f"<!DOCTYPE html>\n<html>\n<head>\n<style>{css_content}</style>\n</head>\n<body>\n{html_content}\n</body>\n</html>")
        
    return jsonify({"status": "success", "message": "Tasarım başarıyla alındı ve sunucuya kaydedildi!"})

if __name__ == '__main__':
    # Ortam değişkeninden portu al (Canlı sunucu için gerekli)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)