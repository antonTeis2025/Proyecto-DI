from typing import Optional

from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
import enum
from database import Base
from sqlalchemy import Enum as SAEnum

# num para el invoice type
class InvoiceType(enum.Enum):
    # IZQUIERDA (Clave): Como lo usarás en tu código Python
    # DERECHA (Valor): Lo que se guardará textualmente en la Base de Datos

    E_INVOICE = "e-invoice"  # En la BD se guardará "e-invoice"
    PAPER_BILLING = "paperbilling"  # En la BD se guardará "paperbilling"

class Customer(Base):
    __tablename__ = 'customers'

    # 1. La PK en tu base de datos NO es 'id', es 'dni_nie' (Text).
    dni: Mapped[str] = mapped_column("dni_nie", String(20), primary_key=True)

    # 2. Mapeo de columnas con nombres distintos
    # Python: add_data  <--> BBDD: adddata
    add_data: Mapped[Optional[str]] = mapped_column("adddata", String(100), nullable=True)

    # Python: email     <--> BBDD: mail
    email: Mapped[Optional[str]] = mapped_column("mail", String(150), nullable=True)

    # Campos que coinciden
    surname: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    mobile: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # 3. EL PROBLEMA DEL MUNICIPIO
    # Tu tabla 'customers' NO TIENE 'municipality_id'. Tiene 'city' y 'province' como TEXTO.
    # Mapeamos directamente a esas columnas de texto para no perder los datos.
    city_name: Mapped[Optional[str]] = mapped_column("city", String(100), nullable=True)
    province_name: Mapped[Optional[str]] = mapped_column("province", String(100), nullable=True)

    # Mapeo de tipos
    invoice_type: Mapped[Optional[str]] = mapped_column("invoicetype", String(50), nullable=True)

    # En tu DB se llama 'historical', asumo que es lo que usas para activo/inactivo
    # Lo trato como string porque en SQLite sale como TEXT
    historical: Mapped[Optional[str]] = mapped_column("historical", String, default="True")
    # Validacion del DNI en el propio
    @validates('dni')
    def validate_dni(self, key, dni_value):
        """
        Esta función se ejecuta AUTOMÁTICAMENTE antes de asignar el valor al DNI.
        Aquí movemos tu lógica del archivo customers.py
        """
        if not dni_value:
            raise ValueError("El DNI no puede estar vacío")

        dni = dni_value.upper().strip()

        # Lógica de validación DNI española estándar
        tabla = "TRWAGMYFPDXBNJZSQVHLCKE"
        numeros = "1234567890"

        if len(dni) != 9:
            raise ValueError(f"Longitud de DNI incorrecta: {dni}")

        # Tratamiento para NIEs (X, Y, Z)
        check_dni = dni
        if dni[0] == 'X':
            check_dni = '0' + dni[1:]
        elif dni[0] == 'Y':
            check_dni = '1' + dni[1:]
        elif dni[0] == 'Z':
            check_dni = '2' + dni[1:]

        number_part = check_dni[:-1]
        letter_part = check_dni[-1]

        if not number_part.isdigit():
            raise ValueError("El DNI contiene caracteres inválidos")

        if tabla[int(number_part) % 23] != letter_part:
            raise ValueError(f"La letra del DNI es incorrecta. Debería ser {tabla[int(number_part) % 23]}")

        return dni  # Retorna el valor limpio y validado

    def __repr__(self):
        return f"<Customer(dni='{self.dni}', name='{self.name} {self.surname}')>"





