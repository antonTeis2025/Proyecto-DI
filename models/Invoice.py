import enum
from typing import List
from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


# NOTA: Asegúrate de que los nombres de tabla aquí coincidan con
# los __tablename__ en tus archivos customer.py y product.py

class InvoiceStatus(enum.Enum):
    ACTIVE = "Activo"
    INACTIVE = "Inactivo"


# 3. LA FACTURA
class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column("idFac", Integer, primary_key=True)

    # ### CORRECCIÓN 1: CLIENTE ###
    # Cambia "Customer.dni" por "nombre_tabla.nombre_columna".
    # Asumo que tu tabla se llama "clientes". Si se llama "customers", cámbialo.
    customer_dni: Mapped[str] = mapped_column("dni_nie", ForeignKey("customers.dni_nie"), nullable=False)

    date: Mapped[str] = mapped_column(String)

    # Relaciones
    # Aquí SÍ usamos el nombre de la Clase ("Customer")
    customer: Mapped["Customer"] = relationship("Customer")
    details: Mapped[List["InvoiceDetail"]] = relationship("InvoiceDetail", back_populates="invoice")

    subtotal: float = 0.0
    iva: float = 0.0
    total: float = 0.0

    def calculate_totals(self):
        self.subtotal = sum(d.subtotal for d in self.details) if self.details else 0.0
        self.iva = self.subtotal * 0.21
        self.total = self.subtotal + self.iva

    def __repr__(self):
        return f"<Invoice(id={self.id}, date='{self.date}', total={self.total})>"


# 2. TABLA INTERMEDIA (Association Object)
class InvoiceDetail(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column("idv", Integer, primary_key=True)

    # ### CORRECCIÓN 2: FACTURA ###
    # Apuntamos a la tabla "invoices" columna "idFac"
    invoice_id: Mapped[int] = mapped_column("idFac", ForeignKey("invoices.idFac"), nullable=False)

    # ### CORRECCIÓN 3: PRODUCTO ###
    # Cambia "Product.id" por "nombre_tabla_productos.id".
    # Asumo que tu tabla se llama "productos".
    product_id: Mapped[int] = mapped_column("idProduct", ForeignKey("products.code"), nullable=False)

    product_name: Mapped[str] = mapped_column("productName", String)
    product_price: Mapped[str] = mapped_column("productPrice", String)
    quantity: Mapped[int] = mapped_column("amount", Integer)

    # Nota: he renombrado esto porque en Invoice usabas d.subtotal,
    # pero aquí se llamaba total_line. Para que coincida con calculate_totals:
    subtotal: Mapped[float] = mapped_column("totalPrice", Float)

    # Relaciones
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="details")
    product: Mapped["Product"] = relationship("Product")

    def __repr__(self):
        return f"<Sale(id={self.id}, item='{self.product_name}')>"