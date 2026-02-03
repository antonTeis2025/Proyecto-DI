from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from database import get_session
from models.Product import Product, ProductFamily


class ProductService:

    @staticmethod
    def create(name: str, price: float, family: ProductFamily, stock: int = 0) -> Product:
        if price < 0:
            raise ValueError("El precio no puede ser negativo")

        with get_session() as session:
            product = Product(name=name, unit_price=price, family=family, stock=stock)
            session.add(product)
            session.commit()
            session.refresh(product)
            return product

    @staticmethod
    def get_all() -> List[Product]:
        with get_session() as session:
            stmt = select(Product).order_by(Product.name)
            return list(session.scalars(stmt).all())

    @staticmethod
    def get_by_id(product_id: int) -> Optional[Product]:
        with get_session() as session:
            return session.get(Product, product_id)

    @staticmethod
    def update(product_id: int, **kwargs) -> Product:
        with get_session() as session:
            product = session.get(Product, product_id)
            if not product:
                raise ValueError("Producto no encontrado")

            # Validaciones específicas antes de asignar
            if 'unit_price' in kwargs and kwargs['unit_price'] < 0:
                raise ValueError("Precio negativo no permitido")
            if 'stock' in kwargs and kwargs['stock'] < 0:
                raise ValueError("Stock negativo no permitido")

            for key, value in kwargs.items():
                if hasattr(product, key):
                    setattr(product, key, value)

            session.commit()
            session.refresh(product)
            return product

    @staticmethod
    def delete(product_id: int) -> bool:
        with get_session() as session:
            product = session.get(Product, product_id)
            if not product:
                return False

            try:
                session.delete(product)
                session.commit()
                return True
            except IntegrityError:
                session.rollback()
                raise ValueError("No se puede borrar el producto: aparece en facturas existentes.")