from dotenv import load_dotenv
from os import environ as env

load_dotenv()

ADMIN_DOMAIN = env.get("ADMIN_DOMAIN", "eventos.com")

IS_DEBUG = env.get("DEBUG", "false") in ["true", "yes"]

SECRET = env.get("SECRET", "secret")

POSTGRES_DB = env.get("POSTGRES_DB", "postgres")
POSTGRES_USER = env.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = env.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = env.get("POSTGRES_HOST", "localhost:5432")

POSTGRES_URI = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

ELASTIC_HOSTS = env.get("ELASTIC_HOSTS", "http://localhost:9200").split(";")

MAIL_HOST = env.get("MAIL_HOST", "localhost:1025")
MAIL_USER = env.get("MAIL_USER")
MAIL_PASSWORD = env.get("MAIL_PASSWORD")
MAIL_FROM = env.get("MAIL_FROM", "Prueba Tus Datos <prueba@localhost>")
MAIL_TLS = env.get("MAIL_TLS", "false") in ["true", "yes"]