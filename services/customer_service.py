from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from database import get_session
from models.Customer import Customer


class CustomerService:


    @staticmethod
    def create(dni: str, name: str, surname: str, **kwargs) -> Customer:
        """Crea un cliente nuevo validando duplicados."""
        with get_session() as session:
            # Validación previa
            stmt = select(Customer).where(Customer.dni == dni)
            if session.scalar(stmt):
                raise ValueError(f"Ya existe un cliente con DNI {dni}")

            customer = Customer(dni=dni, name=name, surname=surname, **kwargs)
            session.add(customer)
            try:
                session.commit()
                session.refresh(customer)
                return customer
            except IntegrityError as e:
                session.rollback()
                raise ValueError(f"Error de integridad al crear cliente: {e}")

    @staticmethod
    def get_all(active_only: bool = True) -> List[Customer]:
        """Obtiene listado. Por defecto solo los activos."""
        with get_session() as session:
            stmt = select(Customer)
            if active_only:
                # Asumiendo que agregaste un campo is_active o similar,
                # si no, borra el .where o filtra por lógica de negocio
                if hasattr(Customer, 'historical'):
                    stmt = stmt.where(Customer.historical == "True")

            # .all() devuelve una lista, scalars() extrae los objetos del Row
            return list(session.scalars(stmt).all())


    @staticmethod
    def get_by_mobile(mobile: str) -> Optional[Customer]:
        with get_session() as session:
            stmt = select(Customer).where(Customer.mobile == mobile)
            return session.scalar(stmt)

    @staticmethod
    def get_by_dni(dni: str) -> Optional[Customer]:
        with get_session() as session:
            stmt = select(Customer).where(Customer.dni == dni)
            return session.scalar(stmt)

    @staticmethod
    def update(dni: str, **kwargs) -> Customer:
        """
        Actualiza campos dinámicos.
        Uso: CustomerService.update(1, email="new@mail.com", address="Calle Falsa 123")
        """
        with get_session() as session:
            customer = session.get(Customer, dni)
            if not customer:
                raise ValueError(f"Cliente con DNI {dni} no encontrado")

            for key, value in kwargs.items():
                if hasattr(customer, key):
                    setattr(customer, key, value)

            session.commit()
            session.refresh(customer)
            return customer

    @staticmethod
    def delete(dni: str, hard_delete: bool = False) -> bool:
        """
        Por defecto hace Soft Delete (recomendado).
        Si hard_delete=True, intenta borrar físico (puede fallar por FK).
        """
        with get_session() as session:
            customer = session.get(Customer, dni)
            if not customer:
                return False

            if hard_delete:
                try:
                    session.delete(customer)
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    raise ValueError("No se puede eliminar el cliente porque tiene facturas asociadas.")
            else:
                # Soft Delete (si tienes el campo, si no, implementa el hard delete)
                if hasattr(customer, 'historical'):
                    customer.historical = False
                    session.commit()
                else:
                    raise NotImplementedError("El modelo Customer no tiene 'historical' para borrado lógico.")

            return True