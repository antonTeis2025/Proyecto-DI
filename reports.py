import datetime
from PyQt6.QtGui import QFont
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import os

from conexion import *
from globals import subtotal


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

            records = Conexion.listCustomers(False)
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

            for record in records:
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
                dni = '****' + record[0][4:7] + '**'
                cls.c.drawString(x, y, dni)
                cls.c.drawString(x + 65, y, record[2])
                cls.c.drawString(x + 165, y, record[3])
                cls.c.drawString(x + 215, y, record[5])
                cls.c.drawString(x + 265, y, record[8])
                cls.c.drawString(x + 345, y, record[9].capitalize())
                cls.c.drawString(x + 425, y, "Activo" if record[10] == "True" else "Baja")

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
        try:
            cls.create_canvas("reportInvoices")

            dni = globals.ui.txtDniCustomerFac.text().strip()
            titulo = "Factura Simple" if dni == "00000000T" else "Factura"

            cls.topreport(titulo + " Nº " + globals.ui.lblNumFac.text())

            if dni != "00000000T":
                record = Conexion.dataOneCustomer(dni)

                cls.c.setFont("Helvetica-Bold", 10)
                cls.c.drawString(220, 785, "Customer")

                cls.c.setFont("Helvetica", 9)

                cls.c.drawString(220, 755, "DNI: " + record[0])
                cls.c.drawString(220, 745, "Apellidos: " + record[2])
                cls.c.drawString(220, 735, "Nombre: " + record[3])
                cls.c.drawString(220, 725, "Dirección: " + record[6])
                cls.c.drawString(220, 715, "Localidad: " + record[8] + " Provincia: " + record[7])

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


            records = Conexion.loadSalesByFac(int(globals.ui.lblNumFac.text()))
            print(records)
            x = 55
            y = 630

            for record in records:
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
                cls.c.drawString(x, y, str(record[2]))
                cls.c.drawString(x + 65, y, record[3])
                cls.c.drawString(x + 215, y, str(record[4]) + "€")
                cls.c.drawString(x + 305, y, str(record[5]))
                cls.c.drawString(x + 375, y, str(record[6]) + "€")
                y -= 15
            subtotal = sum([float(record[6]) for record in records])
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

            
            


