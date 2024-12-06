import subprocess

def dev():
    subprocess.call(["fastapi", "dev", "tus_datos_prueba"])

def alembic_migrate():
    subprocess.call(["alembic", "upgrade", "head"])

def alembic_autogen():
    subprocess.call(["alembic", "revision", "--autogenerate"])