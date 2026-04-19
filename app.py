from flask import Flask, render_template, request, jsonify, redirect, url_request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yusuf_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///builder.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Veritabanı Modelleri
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    project_data = db.Column(db.Text, nullable=True) # Kullanıcının sitesi burada saklanacak

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Rotalar ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_pw = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        login_user(user)
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Hatalı giriş"}), 401

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

# Otomatik Kayıt Rotası
@app.route('/save_project', methods=['POST'])
@login_required
def save_project():
    data = request.get_json()
    current_user.project_data = json.dumps(data)
    db.session.commit()
    return jsonify({"status": "success"})

# Kayıtlı Veriyi Yükleme Rotası
@app.route('/load_project')
@login_required
def load_project():
    if current_user.project_data:
        return jsonify(json.loads(current_user.project_data))
    return jsonify({})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)