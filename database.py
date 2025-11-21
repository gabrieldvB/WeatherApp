"""
Módulo de gerenciamento do banco de dados
"""
import sqlite3
from contextlib import contextmanager
from config import Config


@contextmanager
def get_db_connection():
    """Context manager para conexões com o banco de dados"""
    conn = sqlite3.connect(Config.DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """Inicializa as tabelas do banco de dados"""
    with get_db_connection() as conn:
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
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_searches 
            ON search_history(user_id, searched_at)
        ''')
        
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


class UserRepository:
    """Repositório para operações com usuários"""
    
    @staticmethod
    def find_by_email(email):
        """Busca usuário por email"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            return cursor.fetchone()
    
    @staticmethod
    def find_by_id(user_id):
        """Busca usuário por ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return cursor.fetchone()
    
    @staticmethod
    def create(user_id, nome, email, senha_hash, verification_token):
        """Cria novo usuário"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO users 
                   (id, nome, email, senha, email_verification_token) 
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, nome, email, senha_hash, verification_token)
            )
    
    @staticmethod
    def update_password(user_id, new_password_hash):
        """Atualiza senha do usuário"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET senha = ? WHERE id = ?",
                (new_password_hash, user_id)
            )
    
    @staticmethod
    def verify_email(user_id):
        """Marca email como verificado"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET email_verified = 1, email_verification_token = NULL WHERE id = ?",
                (user_id,)
            )
    
    @staticmethod
    def update_theme(user_id, theme):
        """Atualiza tema do usuário"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET theme = ? WHERE id = ?",
                (theme, user_id)
            )
    
    @staticmethod
    def update_language(user_id, language):
        """Atualiza idioma do usuário"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET language = ? WHERE id = ?",
                (language, user_id)
            )


class SearchHistoryRepository:
    """Repositório para histórico de buscas"""
    
    @staticmethod
    def add(user_id, city_name, latitude, longitude):
        """Adiciona busca ao histórico"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO search_history 
                   (user_id, city_name, latitude, longitude) 
                   VALUES (?, ?, ?, ?)""",
                (user_id, city_name, latitude, longitude)
            )
    
    @staticmethod
    def get_recent(user_id, limit=10):
        """Retorna buscas recentes do usuário"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT DISTINCT city_name, latitude, longitude 
                   FROM search_history 
                   WHERE user_id = ? 
                   ORDER BY searched_at DESC 
                   LIMIT ?""",
                (user_id, limit)
            )
            return cursor.fetchall()
    
    @staticmethod
    def clear(user_id):
        """Limpa histórico do usuário"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM search_history WHERE user_id = ?",
                (user_id,)
            )


class FavoriteCitiesRepository:
    """Repositório para cidades favoritas"""
    
    @staticmethod
    def get_all(user_id):
        """Retorna todas as cidades favoritas do usuário"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM favorite_cities 
                   WHERE user_id = ? 
                   ORDER BY added_at DESC""",
                (user_id,)
            )
            return cursor.fetchall()
    
    @staticmethod
    def find(user_id, city_name):
        """Verifica se cidade está nos favoritos"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM favorite_cities 
                   WHERE user_id = ? AND city_name = ?""",
                (user_id, city_name)
            )
            return cursor.fetchone()
    
    @staticmethod
    def add(user_id, city_name, latitude, longitude):
        """Adiciona cidade aos favoritos"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO favorite_cities 
                   (user_id, city_name, latitude, longitude) 
                   VALUES (?, ?, ?, ?)""",
                (user_id, city_name, latitude, longitude)
            )
    
    @staticmethod
    def remove(favorite_id):
        """Remove cidade dos favoritos"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM favorite_cities WHERE id = ?",
                (favorite_id,)
            )


class PasswordResetRepository:
    """Repositório para tokens de reset de senha"""
    
    @staticmethod
    def create(user_id, token, expires_at):
        """Cria token de reset de senha"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO password_reset_tokens 
                   (user_id, token, expires_at) 
                   VALUES (?, ?, ?)""",
                (user_id, token, expires_at)
            )
    
    @staticmethod
    def mark_as_used(token):
        """Marca token como usado"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE password_reset_tokens SET used = 1 WHERE token = ?",
                (token,)
            )
