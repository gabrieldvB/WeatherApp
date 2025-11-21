"""
Serviços de lógica de negócio
"""
import uuid
import smtplib
import bcrypt
import jwt
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config


class AuthService:
    """Serviço de autenticação"""
    
    @staticmethod
    def hash_password(password):
        """Gera hash da senha"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password, hashed):
        """Verifica senha contra hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_token():
        """Gera token único"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_jwt_token(user_id, expiration_hours=1):
        """Gera token JWT"""
        return jwt.encode({
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=expiration_hours)
        }, Config.JWT_SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def decode_jwt_token(token):
        """Decodifica token JWT"""
        try:
            return jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


class EmailService:
    """Serviço de envio de emails"""
    
    @staticmethod
    def send_email(to_email, subject, body):
        """Envia email"""
        if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
            print(f"Email não configurado. Destinatário: {to_email}, Assunto: {subject}")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = Config.MAIL_USERNAME
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
            server.starttls()
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
            return False
    
    @staticmethod
    def send_verification_email(to_email, name, verification_link):
        """Envia email de verificação"""
        body = f"""
        <h2>Bem-vindo ao Weather App!</h2>
        <p>Olá {name},</p>
        <p>Clique no link abaixo para verificar seu email:</p>
        <a href="{verification_link}">Verificar Email</a>
        """
        return EmailService.send_email(to_email, "Verifique seu email - Weather App", body)
    
    @staticmethod
    def send_password_reset_email(to_email, name, reset_link):
        """Envia email de recuperação de senha"""
        body = f"""
        <h2>Recuperação de Senha - Weather App</h2>
        <p>Olá {name},</p>
        <p>Clique no link abaixo para redefinir sua senha:</p>
        <a href="{reset_link}">Redefinir Senha</a>
        <p>Este link expira em 1 hora.</p>
        """
        return EmailService.send_email(to_email, "Recuperação de Senha", body)


class WeatherService:
    """Serviço de consulta de clima"""
    
    @staticmethod
    def get_coordinates(city_name, language='pt'):
        """Obtém coordenadas de uma cidade"""
        try:
            url = f"{Config.GEOCODING_API_URL}?name={city_name}&count=1&language={language}&format=json"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200 and "results" in response.json():
                data = response.json()["results"][0]
                return {
                    'name': data['name'],
                    'latitude': data['latitude'],
                    'longitude': data['longitude']
                }
            return None
        except Exception as e:
            print(f"Erro ao obter coordenadas: {e}")
            return None
    
    @staticmethod
    def get_weather_data(latitude, longitude):
        """Obtém dados climáticos"""
        try:
            url = (
                f"{Config.WEATHER_API_URL}?"
                f"latitude={latitude}&longitude={longitude}"
                f"&current_weather=true"
                f"&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,weathercode,precipitation_probability_max"
                f"&hourly=relative_humidity_2m,temperature_2m"
                f"&timezone=auto"
            )
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Erro ao obter clima: {e}")
            return None
    
    @staticmethod
    def format_weather_data(raw_data, city_name, latitude, longitude):
        """Formata dados climáticos para exibição"""
        current = raw_data['current_weather']
        daily = raw_data['daily']
        hourly = raw_data['hourly']
        
        return {
            'city': city_name,
            'latitude': latitude,
            'longitude': longitude,
            'temperature': current['temperature'],
            'windspeed': current['windspeed'],
            'winddirection': current['winddirection'],
            'weathercode': current['weathercode'],
            'weather_icon': WeatherService.get_weather_icon(current['weathercode']),
            'humidity': hourly['relative_humidity_2m'][0],
            'sunrise': daily['sunrise'][0].split('T')[1],
            'sunset': daily['sunset'][0].split('T')[1],
            'hourly_temps': hourly['temperature_2m'][:24],
            'hourly_times': [t.split('T')[1] for t in hourly['time'][:24]],
        }
    
    @staticmethod
    def format_forecast_data(raw_data):
        """Formata previsão de 7 dias"""
        daily = raw_data['daily']
        forecast = []
        
        for i in range(7):
            forecast.append({
                'date': daily['time'][i],
                'max_temp': daily['temperature_2m_max'][i],
                'min_temp': daily['temperature_2m_min'][i],
                'icon': WeatherService.get_weather_icon(daily['weathercode'][i]),
                'precipitation': daily['precipitation_probability_max'][i]
            })
        
        return forecast
    
    @staticmethod
    def get_weather_icon(code):
        """Retorna ícone para código climático"""
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


class ValidationService:
    """Serviço de validação"""
    
    @staticmethod
    def validate_email(email):
        """Valida formato de email"""
        return '@' in email and '.' in email
    
    @staticmethod
    def validate_password(password, min_length=6):
        """Valida senha"""
        return len(password) >= min_length
    
    @staticmethod
    def validate_name(name, min_length=3):
        """Valida nome"""
        return len(name.strip()) >= min_length
