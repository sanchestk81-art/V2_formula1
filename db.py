import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Variáveis individuais para conexão
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "formula1")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
DB_SSLMODE = os.getenv("DB_SSLMODE")

# Suporte a strings de conexão direta em nuvem (Neon, Supabase, Vercel Postgres, Railway)
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")


def get_db_connection(use_dict_cursor=True):
    """
    Cria e retorna uma conexão direta com o banco de dados PostgreSQL.
    Não utiliza ORM. O cursor padrão é RealDictCursor, permitindo
    acessar as colunas como dicionário (ex: linha['nome']).
    
    Suporta:
    1. DATABASE_URL ou POSTGRES_URL (recomendado para Vercel / Neon / Supabase)
    2. Variáveis individuais: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    """
    cursor_factory = RealDictCursor if use_dict_cursor else None

    try:
        if DATABASE_URL:
            url = DATABASE_URL.strip()
            # Ajuste de prefixo postgres:// -> postgresql:// para psycopg2
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)

            # Para bancos em nuvem (Neon, Supabase, RDS), se não houver sslmode, adiciona require
            if "sslmode=" not in url and "localhost" not in url and "127.0.0.1" not in url:
                separador = "&" if "?" in url else "?"
                url = f"{url}{separador}sslmode=require"

            conn = psycopg2.connect(url, cursor_factory=cursor_factory)
        else:
            # Conexão por parâmetros individuais
            params = {
                "host": DB_HOST,
                "port": DB_PORT,
                "dbname": DB_NAME,
                "user": DB_USER,
                "password": DB_PASSWORD,
                "cursor_factory": cursor_factory
            }

            # Se estiver na nuvem (não for localhost), exige SSL por padrão para Supabase/Neon/RDS
            if DB_SSLMODE:
                params["sslmode"] = DB_SSLMODE
            elif DB_HOST not in ("localhost", "127.0.0.1"):
                params["sslmode"] = "require"

            conn = psycopg2.connect(**params)

        return conn

    except psycopg2.Error as erro:
        is_serverless = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
        print(f"\n[ERRO DE CONEXÃO COM O BANCO DE DADOS POSTGRESQL]: {erro}")
        if is_serverless and (DB_HOST in ("localhost", "127.0.0.1") and not DATABASE_URL):
            print("⚠️ ATENÇÃO: A aplicação está rodando no Vercel e tentando conectar ao 'localhost'.")
            print("Configure a variável DATABASE_URL (ou DB_HOST, DB_PASSWORD, etc.) no painel do Vercel com os dados do seu banco PostgreSQL em nuvem (ex: Supabase ou Neon).\n")
        raise erro
