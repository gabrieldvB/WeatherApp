import requests
import uuid
import json
import jwt
import smtplib
import sqlite3
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, render_template, redirect, url_for, session, make_response, jsonify
import bcrypt

app = Flask(__name__)
app.secret_key = "ALTERE_ESTA_CHAVE_EM_PRODUCAO_123456"
app.config['JWT_SECRET_KEY'] = "ALTERE_ESTA_CHAVE_JWT_EM_PRODUCAO_123456"

# Segurança da sessão
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Configuração de email (ajuste com suas credenciais)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = ''  # Adicione seu email aqui
app.config['MAIL_PASSWORD'] = ''  # Adicione sua senha de app aqui
app.config['MAIL_USE_TLS'] = True

DATABASE = 'weatherapp.db'


# -------------------- CONEXÃO BD --------------------
def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializa o banco de dados SQLite"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            theme TEXT DEFAULT 'dark',
            language TEXT DEFAULT 'pt',
            email_verified INTEGER DEFAULT 0,
            email_verification_token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de histórico de buscas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            city_name TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_searches ON search_history(user_id, searched_at)')
    
    # Tabela de cidades favoritas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorite_cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            city_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, city_name)
        )
    ''')
    
    # Tabela de tokens de recuperação de senha
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            token TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()


# -------------------- FUNÇÕES AUXILIARES --------------------
def load_translations(lang='pt'):
    try:
        with open(f'translations/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        with open('translations/pt.json', 'r', encoding='utf-8') as f:
            return json.load(f)


def get_user_language():
    if 'user' in session:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT language FROM users WHERE id = ?", (session['user'],))
        user = cursor.fetchone()
        conn.close()
        return user['language'] if user and user['language'] else 'pt'
    return 'pt'


def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_USERNAME']
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False


def save_search_history(user_id, city_name, lat, lon):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO search_history (user_id, city_name, latitude, longitude) VALUES (?, ?, ?, ?)",
            (user_id, city_name, lat, lon)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar histórico: {e}")


def get_weather_icon(code):
    icons = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
        45: "🌫️", 48: "🌫️",
        51: "🌦️", 53: "🌧️", 55: "🌧️",
        61: "🌧️", 63: "🌧️", 65: "🌧️",
        71: "🌨️", 73: "🌨️", 75: "🌨️",
        77: "🌨️", 80: "🌦️", 81: "🌧️", 82: "⛈️",
        85: "🌨️", 86: "🌨️",
        95: "⛈️", 96: "⛈️", 99: "⛈️"
    }
    return icons.get(code, "🌤️")


# -------------------- HOME REDIRECT --------------------
@app.route("/")
def home():
    return redirect(url_for("login_page"))


# -------------------- REGISTRO --------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not all([name, email, password]):
            return render_template("register.html", error="Preencha todos os campos.")

        if '@' not in email or '.' not in email:
            return render_template("register.html", error="Email inválido.")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return render_template("register.html", error="Usuário já existe.")

        user_id = str(uuid.uuid4())
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        verification_token = str(uuid.uuid4())

        cursor.execute(
            "INSERT INTO users (id, nome, email, senha, email_verification_token) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, email, hashed, verification_token)
        )

        conn.commit()
        conn.close()

        # Enviar email de verificação
        verification_link = url_for('verify_email', token=verification_token, _external=True)
        email_body = f"""
        <h2>Bem-vindo ao Weather App!</h2>
        <p>Olá {name},</p>
        <p>Clique no link abaixo para verificar seu email:</p>
        <a href="{verification_link}">Verificar Email</a>
        """
        send_email(email, "Verifique seu email - Weather App", email_body)

        return redirect(url_for("login_page", success="Cadastro realizado! Verifique seu email."))

    return render_template("register.html")


# -------------------- LOGIN --------------------
@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = request.form.get("remember")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        conn.close()

        if not user:
            return render_template("login.html", error="Email ou senha incorretos.")

        if not bcrypt.checkpw(password.encode("utf-8"), user["senha"].encode("utf-8")):
            return render_template("login.html", error="Email ou senha incorretos.")

        session["user"] = user["id"]
        session["name"] = user["nome"]

        if remember:
            session.permanent = True

        response = make_response(redirect(url_for("dashboard")))
        response.set_cookie("last_user", email, max_age=30*24*60*60)
        return response

    last_user = request.cookies.get("last_user")
    return render_template("login.html", last_user=last_user)


# -------------------- DASHBOARD --------------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login_page"))

    weather_data = None
    forecast_data = None
    city = None
    lat = None
    lon = None

    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM favorite_cities WHERE user_id = ? ORDER BY added_at DESC",
        (session['user'],)
    )
    favorites = cursor.fetchall()
    
    cursor.execute(
        "SELECT DISTINCT city_name, latitude, longitude FROM search_history WHERE user_id = ? ORDER BY searched_at DESC LIMIT 10",
        (session['user'],)
    )
    history = cursor.fetchall()
    
    cursor.execute("SELECT theme FROM users WHERE id = ?", (session['user'],))
    user_data = cursor.fetchone()
    theme = user_data['theme'] if user_data and user_data['theme'] else 'dark'
    
    conn.close()

    if request.method == "POST":
        city = request.form.get("city", "").strip()

        if city:
            lang = get_user_language()
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language={lang}&format=json"
            geo_response = requests.get(geo_url)

            if geo_response.status_code == 200 and "results" in geo_response.json():
                geo_data = geo_response.json()["results"][0]
                lat = geo_data["latitude"]
                lon = geo_data["longitude"]
                city = geo_data["name"]

                save_search_history(session['user'], city, lat, lon)

                weather_url = (
                    f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={lat}&longitude={lon}"
                    f"&current_weather=true"
                    f"&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,weathercode,precipitation_probability_max"
                    f"&hourly=relative_humidity_2m,temperature_2m"
                    f"&timezone=auto"
                )

                weather_response = requests.get(weather_url)

                if weather_response.status_code == 200:
                    j = weather_response.json()

                    weather_data = {
                        "city": city,
                        "latitude": lat,
                        "longitude": lon,
                        "temperature": j["current_weather"]["temperature"],
                        "windspeed": j["current_weather"]["windspeed"],
                        "winddirection": j["current_weather"]["winddirection"],
                        "weathercode": j["current_weather"]["weathercode"],
                        "weather_icon": get_weather_icon(j["current_weather"]["weathercode"]),
                        "humidity": j["hourly"]["relative_humidity_2m"][0],
                        "sunrise": j["daily"]["sunrise"][0].split("T")[1],
                        "sunset": j["daily"]["sunset"][0].split("T")[1],
                    }
                    
                    forecast_data = []
                    for i in range(7):
                        forecast_data.append({
                            "date": j["daily"]["time"][i],
                            "max_temp": j["daily"]["temperature_2m_max"][i],
                            "min_temp": j["daily"]["temperature_2m_min"][i],
                            "icon": get_weather_icon(j["daily"]["weathercode"][i]),
                            "precipitation": j["daily"]["precipitation_probability_max"][i]
                        })
                    
                    weather_data["hourly_temps"] = j["hourly"]["temperature_2m"][:24]
                    weather_data["hourly_times"] = [t.split("T")[1] for t in j["hourly"]["time"][:24]]
                    
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT * FROM favorite_cities WHERE user_id = ? AND city_name = ?",
                        (session['user'], city)
                    )
                    weather_data["is_favorite"] = cursor.fetchone() is not None
                    conn.close()
                else:
                    weather_data = {"error": "Não foi possível obter o clima."}
            else:
                weather_data = {"error": "Cidade não encontrada."}

    return render_template(
        "dashboard.html",
        weather=weather_data,
        forecast=forecast_data,
        city=city,
        favorites=favorites,
        history=history,
        theme=theme
    )


# -------------------- LOGOUT --------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("name", None)

    response = make_response(redirect(url_for("login_page")))
    response.set_cookie("session_ended", "true", max_age=60)
    return response


# -------------------- VERIFICAÇÃO DE EMAIL --------------------
@app.route("/verify-email/<token>")
def verify_email(token):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM users WHERE email_verification_token = ?",
        (token,)
    )
    user = cursor.fetchone()
    
    if user:
        cursor.execute(
            "UPDATE users SET email_verified = 1, email_verification_token = NULL WHERE id = ?",
            (user['id'],)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("login_page", success="Email verificado com sucesso!"))
    
    conn.close()
    return redirect(url_for("login_page", error="Token inválido."))


# -------------------- RECUPERAÇÃO DE SENHA --------------------
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if user:
            token = jwt.encode({
                'user_id': user['id'],
                'exp': datetime.utcnow() + timedelta(hours=1)
            }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
            
            cursor.execute(
                "INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)",
                (user['id'], token, datetime.utcnow() + timedelta(hours=1))
            )
            conn.commit()
            
            reset_link = url_for('reset_password', token=token, _external=True)
            email_body = f"""
            <h2>Recuperação de Senha - Weather App</h2>
            <p>Olá {user['nome']},</p>
            <p>Clique no link abaixo para redefinir sua senha:</p>
            <a href="{reset_link}">Redefinir Senha</a>
            <p>Este link expira em 1 hora.</p>
            """
            send_email(email, "Recuperação de Senha", email_body)
        
        conn.close()
        return render_template("forgot_password.html", success="Se o email existir, você receberá instruções.")
    
    return render_template("forgot_password.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        
        if request.method == "POST":
            new_password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            
            if new_password != confirm_password:
                return render_template("reset_password.html", token=token, error="As senhas não coincidem.")
            
            hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET senha = ? WHERE id = ?", (hashed, user_id))
            cursor.execute("UPDATE password_reset_tokens SET used = 1 WHERE token = ?", (token,))
            conn.commit()
            conn.close()
            
            return redirect(url_for("login_page", success="Senha alterada com sucesso!"))
        
        return render_template("reset_password.html", token=token)
    
    except jwt.ExpiredSignatureError:
        return redirect(url_for("forgot_password", error="Token expirado."))
    except:
        return redirect(url_for("forgot_password", error="Token inválido."))


# -------------------- API ENDPOINTS --------------------
@app.route("/api/favorite", methods=["POST"])
def toggle_favorite():
    if "user" not in session:
        return jsonify({"success": False, "message": "Não autenticado"}), 401
    
    data = request.get_json()
    city_name = data.get("city_name")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM favorite_cities WHERE user_id = ? AND city_name = ?",
        (session['user'], city_name)
    )
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute(
            "DELETE FROM favorite_cities WHERE id = ?",
            (existing['id'],)
        )
        conn.commit()
        message = "Removido dos favoritos"
        is_favorite = False
    else:
        cursor.execute(
            "INSERT INTO favorite_cities (user_id, city_name, latitude, longitude) VALUES (?, ?, ?, ?)",
            (session['user'], city_name, latitude, longitude)
        )
        conn.commit()
        message = "Adicionado aos favoritos"
        is_favorite = True
    
    conn.close()
    
    return jsonify({"success": True, "message": message, "is_favorite": is_favorite})


@app.route("/api/clear-history", methods=["DELETE"])
def clear_history():
    if "user" not in session:
        return jsonify({"success": False}), 401
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM search_history WHERE user_id = ?", (session['user'],))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})


@app.route("/api/update-theme", methods=["POST"])
def update_theme():
    if "user" not in session:
        return jsonify({"success": False}), 401
    
    data = request.get_json()
    theme = data.get("theme", "dark")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET theme = ? WHERE id = ?", (theme, session['user']))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})


@app.route("/api/update-language", methods=["POST"])
def update_language():
    if "user" not in session:
        return jsonify({"success": False}), 401
    
    data = request.get_json()
    language = data.get("language", "pt")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language = ? WHERE id = ?", (language, session['user']))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})


@app.route("/api/weather/<city>")
def api_weather(city):
    """API REST própria para consulta de clima"""
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=pt&format=json"
    geo_response = requests.get(geo_url)
    
    if geo_response.status_code == 200 and "results" in geo_response.json():
        geo_data = geo_response.json()["results"][0]
        lat = geo_data["latitude"]
        lon = geo_data["longitude"]
        
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current_weather=true"
            f"&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,weathercode"
            f"&hourly=relative_humidity_2m"
            f"&timezone=auto"
        )
        
        weather_response = requests.get(weather_url)
        
        if weather_response.status_code == 200:
            return jsonify(weather_response.json())
    
    return jsonify({"error": "Cidade não encontrada"}), 404


# -------------------- RUN --------------------
if __name__ == "__main__":
    init_db()
    print("✓ Banco de dados SQLite inicializado")
    app.run(host="0.0.0.0", port=8080, debug=True)
