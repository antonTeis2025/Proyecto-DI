import enum

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy import Enum as SAEnum

from database import Base


class ProductFamily(enum.Enum):
    FOODS = "Foods"
    FURNITURE = "Furniture"
    ELECTRONICS = "Electronics"
    CLOTHES = "Clothes"

class Product(Base):
    __tablename__ = "products"

    # La PK en tu DB es 'code', no 'id'
    id: Mapped[int] = mapped_column("code", Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    stock: Mapped[str] = mapped_column(String, default="0")  # Tu DB dice que stock es TEXT
    family: Mapped[str] = mapped_column(
        String)  # Tu DB dice TEXT, cuidado con el Enum aquí si los datos viejos no coinciden

    # Tu DB tiene 'unitPrice' (camelCase)
    unit_price: Mapped[str] = mapped_column("unitPrice", String)  # Tu DB dice TEXT, debería ser Float/Real

    def __repr__(self):
        return f"<Product(code={self.id}, name='{self.name}')>"

    # ---------------------------------------------------------
    # VALIDACIONES DE NEGOCIO (Domain Logic)
    # ---------------------------------------------------------
    @validates('unit_price')
    def validate_price(self, key, price):
        """Asegura que el precio nunca sea negativo"""
        if price < 0:
            raise ValueError(f"El precio no puede ser negativo: {price}")
        return price

    @validates('stock')
    def validate_stock(self, key, stock_value):
        """Asegura que el stock sea un entero positivo"""
        if stock_value < 0:
             # Opcional: podrías permitir stock negativo si admites "backorders"
             raise ValueError("El stock no puede ser negativo")
        return stock_value

