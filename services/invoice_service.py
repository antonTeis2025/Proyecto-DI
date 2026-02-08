from typing import List, Dict, Optional
from datetime import date, datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import get_session
from models.Invoice import Invoice, InvoiceDetail, InvoiceStatus
from models.Product import Product


class InvoiceService:

    @staticmethod
    def create(customer_dni: str, items) -> Invoice:
        """
        Crea factura y descuenta stock atómicamente.
        items structure: [{'product_id': 1, 'quantity': 2}, ...]
        """
        # if not items:
        #    raise ValueError("La factura debe tener al menos un producto.")

        with get_session() as session:
            # 1. Cabecera
            invoice = Invoice(
                customer_dni=customer_dni,
                date=datetime.now().strftime("%d/%m/%Y-%H:%M")
            )
            session.add(invoice)

            # if items is not None:
            #    # 2. Detalles y Stock
            #    for item in items:
            #        p_id = item['product_id']
            #        qty = item['quantity']

            #        product = session.get(Product, p_id)

            #        if not product:
                        # No hace falta rollback explícito si lanzas excepción,
                        # el Context Manager de Python (__exit__) debería encargarse,
                        # pero si quieres ser explícito, hazlo antes del raise.
            #            session.rollback()
            #            raise ValueError(f"Producto ID {p_id} no existe")

            #        if product.stock < qty:
                        # --- CORRECCIÓN AQUÍ ---
                        # 1. Capturamos los datos en variables locales
            #            p_name = product.name
            #            p_stock = product.stock

                        # 2. Hacemos Rollback (Limpiamos la sesión)
            #            session.rollback()

                        # 3. Lanzamos el error usando las variables locales, NO el objeto SQLAlchemy
            #            raise ValueError(f"Stock insuficiente para '{p_name}'. Stock actual: {p_stock}")

            #        product.stock -= qty

                    # Crear detalle (Snapshot de precio)
            #        detail = InvoiceDetail(
            #            product_id=p_id,
            #            quantity=qty,
            #            unit_price=product.unit_price,
            #            invoice=invoice
            #        )
            #        session.add(detail)

            # 3. Guardar y Calcular
            session.flush()  # Envía SQL a la BD para generar IDs, pero no commitea
            # invoice.calculate_totals()  # Método de tu modelo que suma subtotal/iva

            session.commit()

            # 4. Eager load para devolver el objeto completo
            # Re-cargamos la factura con sus relaciones para que la UI pueda pintarla
            # sin dar error de "Detached Instance"
            stmt = (
                select(Invoice)
                .where(Invoice.id == invoice.id)
            )
            return session.scalar(stmt)

    @staticmethod
    def get_all() -> List[Invoice]:
        """Obtiene facturas cargando el nombre del cliente (Join optimizado)."""
        with get_session() as session:
            stmt = (
                select(Invoice)
                .options(selectinload(Invoice.customer))  # Carga datos del cliente en una sola query
                .order_by(Invoice.date.desc())
            )
            return list(session.scalars(stmt).all())

    @staticmethod
    def get_by_id(invoice_id: int) -> Optional[Invoice]:
        """Carga factura COMPLETA: Cliente y Detalles (Productos)."""
        with get_session() as session:
            stmt = (
                select(Invoice)
                .options(
                    selectinload(Invoice.customer),
                    selectinload(Invoice.details).selectinload(InvoiceDetail.product)
                )
                .where(Invoice.id == invoice_id)
            )
            return session.scalar(stmt)

    @staticmethod
    def cancel_invoice(invoice_id: int):
        """
        Anula una factura: cambia estado y DEVUELVE el stock.
        """
        with get_session() as session:
            # Cargamos con detalles para saber qué devolver
            stmt = (
                select(Invoice)
                .options(selectinload(Invoice.details))
                .where(Invoice.id == invoice_id)
            )
            invoice = session.scalar(stmt)

            if not invoice:
                raise ValueError("Factura no encontrada")

            if invoice.status == InvoiceStatus.INACTIVE:  # Asumiendo enum INACTIVE
                raise ValueError("La factura ya está anulada")

            # Devolver Stock
            for detail in invoice.details:
                product = session.get(Product, detail.product_id)
                if product:
                    product.stock += int(detail.quantity)  # Asumiendo entero

            invoice.status = InvoiceStatus.INACTIVE
            session.commit()

    @staticmethod
    def add_product(id_factura: int, producto: InvoiceDetail) -> Invoice:
        # 1. Abrimos la sesión PRIMERO
        with get_session() as session:
            # 2. Buscamos la factura DENTRO de esta sesión activa
            # Usamos session.get para asegurar que el objeto esté atado a esta transacción
            factura = session.get(Invoice, id_factura)

            if not factura:
                raise ValueError("Factura no encontrada")

            # 3. Ahora sí podemos modificar la relación
            factura.details.append(producto)

            # 4. Guardamos
            session.commit()
            session.refresh(factura)

            return factura


    @staticmethod
    def delete_invoice(invoice_id: int):
        """
        Elimina físicamente una factura y todos sus detalles asociados.
        """
        with get_session() as session:
            # 1. Buscamos la factura
            # No necesitamos cargar relaciones (selectinload) porque las borraremos por ID
            stmt = select(Invoice).where(Invoice.id == invoice_id)
            invoice = session.scalar(stmt)

            if not invoice:
                raise ValueError(f"No se pudo eliminar: La factura con ID {invoice_id} no existe.")

            try:
                # 2. Borrar los detalles asociados primero (por integridad referencial)
                # SQLAlchemy permite borrar mediante la relación si está cargada,
                # pero una ejecución de delete directa es más eficiente:
                from sqlalchemy import delete
                stmt_details = delete(InvoiceDetail).where(InvoiceDetail.invoice_id == invoice_id)
                session.execute(stmt_details)

                # 3. Borrar la cabecera de la factura
                session.delete(invoice)

                # 4. Confirmar cambios
                session.commit()
                print(f"Factura {invoice_id} y sus detalles eliminados correctamente.")

            except Exception as e:
                session.rollback()
                raise Exception(f"Error al eliminar la factura: {str(e)}")