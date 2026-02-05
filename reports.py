import datetime
from PyQt6.QtGui import QFont
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import os

from conexion import *
from globals import subtotal
from services.customer_service import CustomerService
from services.invoice_service import InvoiceService


class Reports:
    rootPath = ".\\reports"

    @classmethod
    def create_canvas(cls, title_suffix):
        """Crea un canvas nuevo para cada reporte con su propio nombre."""
        date = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        name = f"{date}_{title_suffix}.pdf"
        cls.pdf_path = os.path.join(cls.rootPath, name)
        cls.c = canvas.Canvas(cls.pdf_path)
        return cls.c

    @classmethod
    def topreport(cls, titulo):
        """Dibuja la cabecera con el título dinámico."""
        try:
            path_logo = os.path.join(os.path.dirname(__file__), "img", "logo.png")
            logo = Image.open(path_logo)

            if isinstance(logo, Image.Image):
                cls.c.setFont("Helvetica-Bold", 10)
                cls.c.drawString(55, 785, "EMPRESA TEIS")

                # Título que viene por parámetro
                cls.c.setFont("Helvetica-Bold", 14)
                cls.c.drawCentredString(300, 675, titulo)

                cls.c.line(35, 665, 550, 665)

                cls.c.drawImage(path_logo, 480, 745, width=40, height=40)

                cls.c.setFont("Helvetica", 9)
                cls.c.drawString(55, 755, "CIF: A55641214B")
                cls.c.drawString(55, 745, "28080 Vigo")
                cls.c.drawString(55, 735, "C/ A Picota, 12423")
                cls.c.drawString(55, 725, "Tel: 912345678")
                cls.c.drawString(55, 715, "Email: info@empresateis.com")

                cls.c.line(50, 705, 50, 800)
                cls.c.line(50, 705, 180, 705)
                cls.c.line(180, 705, 180, 800)
                cls.c.line(180, 800, 50, 800)

        except Exception as e:
            print("Error en topreport:", e)

    @classmethod
    def footer(cls):
        try:
            cls.c.line(50, 50, 525, 50)
            day = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            cls.c.setFont("Helvetica", 7)
            cls.c.drawString(465, 40, day)
        except Exception as e:
            print("Error en footer:", e)

    # ============================================================
    # REPORT CUSTOMERS
    # ============================================================
    @classmethod
    def reportCustomers(cls):
        try:
            cls.create_canvas("reportCustomers")

            # records = Conexion.listCustomers(False)
            customers = CustomerService.get_all(active_only = False)
            items = ["DNI_NIE", "SURNAME", "NAME", "MOBILE", "CITY", "INVOICE TYPE", "STATE"]

            cls.topreport("Report Customers")

            cls.c.setFont("Helvetica-Bold", 10)
            cls.c.drawString(55, 650, items[0])
            cls.c.drawString(120, 650, items[1])
            cls.c.drawString(220, 650, items[2])
            cls.c.drawString(270, 650, items[3])
            cls.c.drawString(320, 650, items[4])
            cls.c.drawString(400, 650, items[5])
            cls.c.drawString(480, 650, items[6])
            cls.c.line(50, 695, 525, 695)
            cls.footer()

            x = 55
            y = 630

            for customer in customers:
                if y <= 90:
                    cls.c.showPage()
                    cls.topreport("Report Customers")
                    cls.footer()

                    cls.c.setFont("Helvetica-Bold", 10)
                    cls.c.drawString(55, 650, items[0])
                    cls.c.drawString(120, 650, items[1])
                    cls.c.drawString(220, 650, items[2])
                    cls.c.drawString(270, 650, items[3])
                    cls.c.drawString(320, 650, items[4])
                    cls.c.drawString(400, 650, items[5])
                    cls.c.drawString(480, 650, items[6])
                    cls.c.line(50, 695, 525, 695)
                    y = 630

                cls.c.setFont("Helvetica", 7)
                dni = '****' + str(customer.dni)[4:7] + '**' # dni
                #print("DEBUG: reportCustomers --------------------------------")
                #print(record) ['Z7111425Z', '14/11/2022', 'Vega Molina', 'Isabel', 'isabel.vega@example.com', '611648114', 'Calle Sol 26', 'Zaragoza', 'Zaragoza', 'electronic', 'True']
                #print("-------------------------------------------------------")
                cls.c.drawString(x, y, dni)
                cls.c.drawString(x + 65, y, str(customer.surname)) # apell
                cls.c.drawString(x + 165, y, str(customer.name)) # nombre
                cls.c.drawString(x + 215, y, str(customer.mobile)) # tlf
                cls.c.drawString(x + 265, y, str(customer.city_name))  # cuidad
                cls.c.drawString(x + 345, y, str(customer.invoice_type).capitalize()) # t factura
                cls.c.drawString(x + 425, y, "Activo" if str(customer.invoice_type) == "True" else "Baja") # historical

                y -= 15

            cls.c.save()
            os.startfile(cls.pdf_path)

        except Exception as e:
            print("Error en reportCustomers:", e)

    # ============================================================
    # REPORT PRODUCTS
    # ============================================================
    @classmethod
    def reportProducts(cls):
        try:
            cls.create_canvas("reportProducts")

            records = Conexion.listProducts()
            items = ["CODE", "NAME", "STOCK", "FAMILY", "UNIT PRICE"]

            cls.topreport("Report Products")

            cls.c.setFont("Helvetica-Bold", 10)
            cls.c.drawString(55, 650, items[0])
            cls.c.drawString(120, 650, items[1])
            cls.c.drawString(270, 650, items[2])
            cls.c.drawString(350, 650, items[3])
            cls.c.drawString(425, 650, items[4])
            cls.c.line(50, 695, 525, 695)
            cls.footer()

            x = 55
            y = 630

            for record in records:
                if y <= 90:
                    cls.c.showPage()
                    cls.topreport("Report Products")
                    cls.footer()

                    cls.c.setFont("Helvetica-Bold", 10)
                    cls.c.drawString(55, 650, items[0])
                    cls.c.drawString(120, 650, items[1])
                    cls.c.drawString(270, 650, items[2])
                    cls.c.drawString(350, 650, items[3])
                    cls.c.drawString(425, 650, items[4])
                    cls.c.line(50, 695, 525, 695)
                    y = 630

                cls.c.setFont("Helvetica", 7)
                cls.c.drawString(x, y, str(record[0]))
                cls.c.drawString(x + 65, y, record[1])
                cls.c.drawString(x + 215, y, str(record[2]))
                cls.c.drawString(x + 295, y, record[3])
                cls.c.drawString(x + 370, y, str(record[4]))
                y -= 15

            cls.c.save()
            os.startfile(cls.pdf_path)

        except Exception as e:
            print("Error en reportProducts:", e)

    # ============================================================
    # REPORT INVOICES
    # ============================================================
    @classmethod
    def reportInvoices(cls):
        print("-------------------------------------------------------- ejecutando: reportInvoices")
        try:
            cls.create_canvas("reportInvoices")

            dni = globals.ui.txtDniCustomerFac.text().strip()
            titulo = "Factura Simple" if dni == "00000000T" else "Factura"

            cls.topreport(titulo + " Nº " + globals.ui.lblNumFac.text())

            if dni != "00000000T":
                cliente = CustomerService.get_by_dni(dni)
                # print("---------------------- reportInvoices  (cliente) ----------------------")
                # print(record) ['32516522L', '20/01/2022', 'Domínguez Soto', 'Lucía', 'lucía.domínguez@example.com', '647009029', 'Calle Luna 33', 'Cádiz', 'Cádiz', 'electronic', 'True']
                # print("-----------------------------------------------------------------------")
                cls.c.setFont("Helvetica-Bold", 10)
                cls.c.drawString(220, 785, "Customer")

                cls.c.setFont("Helvetica", 9)

                cls.c.drawString(220, 755, "DNI: " + cliente.dni)
                cls.c.drawString(220, 745, "Apellidos: " + cliente.surname)
                cls.c.drawString(220, 735, "Nombre: " + cliente.name)
                cls.c.drawString(220, 725, "Dirección: " + cliente.address)
                cls.c.drawString(220, 715, "Localidad: " + cliente.city_name + " Provincia: " + cliente.province_name)

                cls.c.line(215, 705, 215, 800)
                cls.c.line(215, 705, 360, 705)
                cls.c.line(360, 705, 360, 800)
                cls.c.line(360, 800, 215, 800)


            items = ["CODE", "NAME", "UNIT PRICE", "AMOUNT", "TOTAL PRICE"]

            cls.c.setFont("Helvetica-Bold", 10)
            cls.c.drawString(55, 650, items[0])
            cls.c.drawString(120, 650, items[1])
            cls.c.drawString(270, 650, items[2])
            cls.c.drawString(360, 650, items[3])
            cls.c.drawString(430, 650, items[4])
            cls.c.line(50, 695, 525, 695)


            # records = Conexion.loadSalesByFac(int(globals.ui.lblNumFac.text()))

            factura = InvoiceService.get_by_id(int(globals.ui.lblNumFac.text()))

            x = 55
            y = 630

            for detail in factura.details:
                # print("---------------------- reportInvoices (productos) ----------------------")
                # print(record)       ['14', '5', '11', 'Mobile', '185.36', '1', '185.36']
                # print("------------------------------------------------------------------------")
                if y <= 100:
                    cls.c.showPage()
                    cls.topreport("Report Products")
                    cls.footer()

                    cls.c.setFont("Helvetica-Bold", 10)
                    cls.c.drawString(55, 650, items[0])
                    cls.c.drawString(120, 650, items[1])
                    cls.c.drawString(270, 650, items[2])
                    cls.c.drawString(360, 650, items[3])
                    cls.c.drawString(430, 650, items[4])
                    cls.c.line(50, 695, 525, 695)
                    y = 630

                cls.c.setFont("Helvetica", 7)
                cls.c.drawString(x, y, str(detail.product_id))
                cls.c.drawString(x + 65, y, detail.product_name)
                cls.c.drawString(x + 215, y, str(detail.product_price) + "€")
                cls.c.drawString(x + 305, y, str(detail.quantity))
                cls.c.drawString(x + 375, y, str(detail.subtotal) + "€")
                y -= 15

            subtotal = sum([float(detail.subtotal) for detail in factura.details])
            iva = subtotal * 0.21
            total = subtotal + iva
            cls.c.setFont("Helvetica-Bold", 10)
            cls.c.drawString(425, 95, "SUBTOTAL: " + f"{subtotal:.2f} €")
            cls.c.drawString(425, 80, "IVA: " + f"{iva:.2f} €")
            cls.c.drawString(425, 65, "TOTAL: " + f"{total:.2f} €")
            cls.footer()
            cls.c.save()
            os.startfile(cls.pdf_path)
        except Exception as e:
            print("Error en reportInvoices:", e)

            
            


