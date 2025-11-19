import requests
import uuid
from datetime import timedelta
from flask import Flask, request, render_template, redirect, url_for, session, make_response
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = "uma_chave_muito_segura"

# Segurança da sessão
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)


# -------------------- CONEXÃO BD --------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="petinho2006",
        database="weatherapp"
    )


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

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            return render_template("register.html", error="Usuário já existe.")

        user_id = str(uuid.uuid4())

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        cursor.execute(
            "INSERT INTO users (id, nome, email, senha) VALUES (%s, %s, %s, %s)",
            (user_id, name, email, hashed)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("login_page"))

    return render_template("register.html")


# -------------------- LOGIN --------------------
@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = request.form.get("remember")

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
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
        response.set_cookie("last_user", email, max_age=30*24*60*60)  # 30 dias
        return response

    last_user = request.cookies.get("last_user")
    return render_template("login.html", last_user=last_user)


# -------------------- DASHBOARD --------------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login_page"))

    weather_data = None
    city = None

    if request.method == "POST":
        city = request.form.get("city", "").strip()

        if city:
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
                    f"&daily=sunrise,sunset"
                    f"&hourly=relative_humidity_2m"
                    f"&timezone=auto"
                )

                weather_response = requests.get(weather_url)

                if weather_response.status_code == 200:
                    j = weather_response.json()

                    weather_data = {
                        "city": geo_data["name"],
                        "temperature": j["current_weather"]["temperature"],
                        "windspeed": j["current_weather"]["windspeed"],
                        "winddirection": j["current_weather"]["winddirection"],
                        "weathercode": j["current_weather"]["weathercode"],
                        "humidity": j["hourly"]["relative_humidity_2m"][0],
                        "sunrise": j["daily"]["sunrise"][0].split("T")[1],
                        "sunset": j["daily"]["sunset"][0].split("T")[1],
                    }
                else:
                    weather_data = {"error": "Não foi possível obter o clima."}
            else:
                weather_data = {"error": "Cidade não encontrada."}

    return render_template("dashboard.html", weather=weather_data, city=city)


# -------------------- LOGOUT --------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("name", None)

    response = make_response(redirect(url_for("login_page")))
    response.set_cookie("session_ended", "true", max_age=60)
    return response


# -------------------- RUN --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
