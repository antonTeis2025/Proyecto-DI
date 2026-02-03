import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 1. Definimos el nombre de la base de datos
# Usamos os.path para asegurar que funcione bien en Windows/Linux

# DATABASE_NAME = "data/test.sqlite"
DATABASE_NAME = "data/bbdd.sqlite"

# 2. Configuración del Motor (Engine)
# 'echo=True' hará que veas en la consola todas las sentencias SQL que se ejecutan.
# Es ÚTILISIMO para aprender y depurar. Cuando termines el proyecto, lo pones en False.
engine = create_engine(f"sqlite:///{DATABASE_NAME}", echo=True)

# 3. La Fábrica de Sesiones (SessionMaker)
# No usamos la conexión directa, usamos "Sesiones".
# Imagina que una sesión es una "transacción" o un "espacio de trabajo" temporal.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# 4. Clase Base Declarativa
# Todas tus entidades (Customer, Product, etc.) heredarán de esta clase.
class Base(DeclarativeBase):
    pass

# 5. Función para inicializar la Base de Datos
def create_tables():
    """
    Esta función detecta todas las clases que hereden de 'Base'
    y crea las tablas correspondientes en SQLite si no existen.
    """
    print("Detectando modelos y creando tablas...")

    # IMPORTANTE: Debemos importar los modelos AQUÍ dentro para que
    # SQLAlchemy sepa que existen antes de crear las tablas.
    # Si no los importas, no se crean.
    try:
        import models.Customer
        import models.Invoice
        import models.Product
        import models.locations


        # Crea todo lo que esté pendiente
        Base.metadata.create_all(bind=engine)
        print("¡Tablas creadas con éxito!")

    except ImportError as e:
        print(f"Error al importar modelos: {e}")
        print(
            "Asegúrate de que tus archivos de modelos (customer.py, etc.) están en una carpeta 'models' con un __init__.py")


# 6. Utilidad para obtener una sesión (Patrón Context Manager)
# Esto te servirá para usar 'with' en tu código y no olvidar cerrar conexiones.
from contextlib import contextmanager


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()  # Guarda cambios si todo va bien
    except Exception:
        session.rollback()  # Deshace cambios si hubo error
        raise
    finally:
        session.close()  # Cierra la conexión siempre