from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yusuf_pro_studio_9988'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = None  # JSON tabanlı login için yönlendirme yapma

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    site_data = db.Column(db.Text, nullable=True)  # JSON string

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"message": "Oturum açmanız gerekiyor"}), 401

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/user', methods=['GET'])
@login_required
def get_user():
    return jsonify({"username": current_user.username})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Bu kullanıcı adı zaten alınmış!"}), 400
    user = User(
        username=data['username'],
        password=generate_password_hash(data['password'])
    )
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return jsonify({"success": True, "username": user.username})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        login_user(user)
        return jsonify({"success": True, "username": user.username})
    return jsonify({"message": "Kullanıcı adı veya şifre hatalı!"}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True})

@app.route('/api/auto-save', methods=['POST'])
@login_required
def auto_save():
    data = request.get_json()
    current_user.site_data = json.dumps(data)
    db.session.commit()
    return jsonify({"status": "saved"})

# ... (önceki kod aynen) ...
@app.route('/api/load-site', methods=['GET'])
@login_required
def load_site():
    if current_user.site_data:
        return jsonify(json.loads(current_user.site_data))
    else:
        default_data = {
            "components": "<div style='padding:50px;text-align:center;background:#f3f4f6;'><h1>Yeni Tasarım</h1><p>Sürükle-bırak ile başlayın</p></div>",
            "styles": "",
            "assets": []
        }
        return jsonify(default_data)
# ...

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)