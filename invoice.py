import datetime
from itertools import product

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QAbstractItemView
from sqlalchemy.engine import row

import conexion
import globals
from conexion import Conexion
from models import InvoiceDetail, Invoice
from reports import Reports
from services.customer_service import CustomerService
from services.invoice_service import InvoiceService
from services.product_service import ProductService





class Invoices:
    isSaleAlreadyDone = False

    @staticmethod
    def borrar_factura_click():
        # 1. Identificamos qué botón envió la señal
        boton = QtWidgets.QApplication.focusWidget()  # O mejor:
        # Si lo prefieres más robusto:
        # boton = globals.ui.tableInvoiceList.sender()

        # Obtenemos el botón específico
        button = QtWidgets.QApplication.instance().focusWidget()

        # 2. Localizamos la posición del botón en la tabla
        # Esto es más seguro que usar el 'index' del bucle
        button_pos = button.mapToParent(QtCore.QPoint(0, 0))
        index = globals.ui.tableInvoiceList.indexAt(button_pos)

        if index.isValid():
            fila = index.row()
            # 3. Obtenemos el ID de la columna 0
            id_registro = globals.ui.tableInvoiceList.item(fila, 0).text()

            mbox = QtWidgets.QMessageBox()
            mbox.setWindowTitle("Warning")
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            mbox.setText("Delete invoice?")
            mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            mbox.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
            mbox.setStyleSheet(globals.mboxStyleSheet)
            resultExec = mbox.exec()
            if resultExec == QtWidgets.QMessageBox.StandardButton.Yes:
                # Aquí llamarías a tu backend:
                InvoiceService.delete_invoice(id_registro)
                Invoices.loadTableFac() # Refrescar tabla
                Invoices.cleanInv() # Borramos los campos de texto

    @staticmethod
    def dataCustomer(widget):
        try:
            dni = widget.text().strip().upper()
            if dni == "":
                dni = "00000000T"
                globals.ui.txtDniCustomerFac.setText(dni)

            cliente = CustomerService.get_by_dni(dni)
            if cliente:

                #print("DBG -----------------------------------------------")
                #print(record) ['32516522L', '20/01/2022', 'Domínguez Soto', 'Lucía', 'lucía.domínguez@example.com', '647009029', 'Calle Luna 33', 'Cádiz', 'Cádiz', 'electronic', 'True']
                #print("DBG -----------------------------------------------")

                globals.ui.lblNameInv.setText(cliente.name + " " + cliente.surname)
                globals.ui.lblInvoiceTypeInv.setText(cliente.invoice_type.capitalize())
                globals.ui.lblAddressInv.setText(cliente.address) if dni == "00000000T" else globals.ui.lblAddressInv.setText(
                    cliente.address + ", " + cliente.city_name + ", " + cliente.province_name)
                globals.ui.lblMobileInv.setText(cliente.mobile)
                # globals.ui.lblStatusInv.setText("Inactivo" if cliente.historical == "True" else "Activo")
                print("Doy de alta la factura")
            else:
                mbox = QtWidgets.QMessageBox()
                mbox.setWindowTitle("Invoice")
                mbox.setIcon(QtWidgets.QMessageBox.Icon.Information)
                mbox.setText("Customer doesn't exist.")
                mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                mbox.setStyleSheet(globals.mboxStyleSheet)
                mbox.exec()
                Invoices.cleanInv()
                print("No doy de alta la factura")
        except Exception as e:
            print("error en saveInvoice", e)

    @staticmethod
    def checkDni():
        dni = globals.ui.txtDniCustomerFac.text().strip().upper()
        globals.ui.txtDniCustomerFac.setText(dni)
        Invoices.dataCustomer(globals.ui.txtDniCustomerFac)

    @staticmethod
    def cleanInv():
        try:
            globals.ui.txtDniCustomerFac.setText("")
            globals.ui.lblNumFac.setText("")
            globals.ui.lblFechaFac.setText("")

            globals.ui.lblNameInv.setText("")
            globals.ui.lblInvoiceTypeInv.setText("")
            globals.ui.lblAddressInv.setText("")
            globals.ui.lblMobileInv.setText("")
            globals.ui.lblStatusInv.setText("")
            Invoices.activeSales()
            globals.sales = []
        except Exception as e:
            print("error en cleanInv", e)

    @staticmethod
    def saveInvoice():
        # Variable para recordar la factura creada
        new_invoice_id = None

        # Conseguir el DNI de la caja de texto
        dni = globals.ui.txtDniCustomerFac.text().strip().upper()
        if dni == "":
            dni = "00000000T"

        # Conseguir el cliente de la BBDD
        cliente = CustomerService.get_by_dni(dni)

        if cliente:
            # Poner DNI en la caja de texto
            globals.ui.txtDniCustomerFac.setText(dni)
            # Poner la fecha actual en la caja de texto
            data = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
            globals.ui.lblFechaFac.setText(data)

            # Crear factura
            factura = None
            try:
                factura = InvoiceService.create(customer_dni=dni, items=None)
            except Exception as e:
                print(f"ERROR AL CREAR FACTURA: {e}")

            if factura != None:  # Si el proceso no falla
                new_invoice_id = factura.id  # <--- 1. GUARDAMOS EL ID

                # Mensaje de exito
                mbox = QtWidgets.QMessageBox()
                mbox.setWindowTitle("Invoice")
                mbox.setIcon(QtWidgets.QMessageBox.Icon.Information)
                mbox.setText("Invoice Saved")
                mbox.setStyleSheet(globals.mboxStyleSheet)
                QtCore.QTimer.singleShot(1000, mbox.close)
                mbox.exec()
            else:
                mbox = QtWidgets.QMessageBox()
                mbox.setWindowTitle("Invoice")
                mbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                mbox.setText("Error al crear la factura")
                mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                mbox.setStyleSheet(globals.mboxStyleSheet)
                mbox.exec()

        else:
            mbox = QtWidgets.QMessageBox()
            mbox.setWindowTitle("Invoice")
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            mbox.setText("Missing Information")
            mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
            mbox.setStyleSheet(globals.mboxStyleSheet)
            mbox.exec()

        # Recargamos la tabla (esto borra la selección visual)
        Invoices.loadTableFac(False)

        # <--- 2. LÓGICA PARA AUTO-SELECCIONAR LA NUEVA FACTURA
        if new_invoice_id:
            # Buscamos en la tabla la fila que tiene el ID de la nueva factura
            table = globals.ui.tableInvoiceList
            for row in range(table.rowCount()):
                item_id = table.item(row, 0)  # Columna 0 es el ID
                if item_id and item_id.text() == str(new_invoice_id):
                    # A. Seleccionamos visualmente la fila
                    table.selectRow(row)

                    # B. Llamamos al funcion que carga los datos y habilita la edición
                    Invoices.selectInvoice()

                    # C. Hacemos scroll hasta la fila (por si la tabla es muy larga)
                    table.scrollToItem(item_id)
                    break

    @staticmethod
    def loadTableFac(showData=False):
        try:
            # records = conexion.Conexion.allInvoice()
            # record: ['16', '00000000T', '26/11/2025-09:42']
            records = InvoiceService.get_all()
            globals.ui.tableInvoiceList.setRowCount(0)
            index = 0
            for record in records:
                if showData and record == records[0]:
                    globals.ui.lblNumFac.setText(str(record.id))
                    globals.ui.lblFechaFac.setText(str(record.date))

                # print(record)
                globals.ui.tableInvoiceList.setRowCount(index + 1)
                globals.ui.tableInvoiceList.setItem(index, 0, QtWidgets.QTableWidgetItem(str(record.id)))
                globals.ui.tableInvoiceList.setItem(index, 1, QtWidgets.QTableWidgetItem(str(record.customer_dni)))
                globals.ui.tableInvoiceList.setItem(index, 2, QtWidgets.QTableWidgetItem(str(record.date)))

                btn_del = QtWidgets.QPushButton()
                btn_del.setIcon(QIcon("./img/basura.png"))
                btn_del.setIconSize(QtCore.QSize(30, 30))
                btn_del.setFixedSize(32, 32)
                btn_del.setStyleSheet("border: none; background-color: transparent")
                globals.ui.tableInvoiceList.setCellWidget(index, 3, btn_del)
                # Asigno funcion del boton
                btn_del.clicked.connect(Invoices.borrar_factura_click)

                globals.ui.tableInvoiceList.item(index, 0).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
                globals.ui.tableInvoiceList.item(index, 1).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignCenter.AlignCenter)
                globals.ui.tableInvoiceList.item(index, 2).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)

                #CREAR BOTON ELIMINAR FILA
                index += 1
            Invoices.checkDni()
        except Exception as e:
            print("error en loadTableFac", e)

    @staticmethod
    def selectInvoice():
        """

        esta funcion carga los datos de una factura a los campos de texto

        """
        try:
            # Pone to.do a 0 y carga los datos que están en la propia fila
            globals.subtotal = 0
            globals.sales = []
            globals.ui.lblStatusInv.setText("Activa")
            row = globals.ui.tableInvoiceList.selectedItems()
            data = [dato.text() for dato in row]
            globals.ui.lblNumFac.setText(data[0])
            globals.ui.txtDniCustomerFac.setText(data[1])
            globals.ui.lblFechaFac.setText(data[2])
            Invoices.checkDni()

            #selectedSales = conexion.Conexion.loadSalesByFac(data[0])

            # data[0] -> id
            # Carga las ventas de la factura seleccionada
            sales = InvoiceService.get_by_id(int(data[0])).details

            if sales != []: # Si existen ventas -> se bloqueara la edicion (factura inactiva)
                globals.ui.lblStatusInv.setText("Cerrada")
                Invoices.isSaleAlreadyDone = True
                Invoices.activeSales() # calcula las columnas
                globals.ui.tableInvoiceProducts.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # hace que no se pueda editar la tabla

                # Va iterando los datos de las ventas rellenando la tabla
                #         1 id     2 name       3 pvp    4 canti   5 total
                # [['5', '11', 'Mobile', '185.36€', '1', '185.36€']]
                # rellena la tabla
                for row, sale in enumerate(sales):
                    print(sale)
                    globals.ui.tableInvoiceProducts.setItem(row, 0, QtWidgets.QTableWidgetItem(str(sale.product_id))) # 2
                    globals.ui.tableInvoiceProducts.item(row, 0).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

                    globals.ui.tableInvoiceProducts.setItem(row, 1, QtWidgets.QTableWidgetItem(str(sale.product_name))) # 3
                    globals.ui.tableInvoiceProducts.setItem(row, 2, QtWidgets.QTableWidgetItem(str(sale.product_price) + '€')) # 4
                    globals.ui.tableInvoiceProducts.setItem(row, 3, QtWidgets.QTableWidgetItem(str(sale.quantity)))# 5
                    globals.ui.tableInvoiceProducts.setItem(row, 4, QtWidgets.QTableWidgetItem(str(sale.subtotal) + '€')) # 6
                    globals.ui.tableInvoiceProducts.item(row, 1).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    globals.ui.tableInvoiceProducts.item(row, 2).setTextAlignment(
                        QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                    globals.ui.tableInvoiceProducts.item(row, 3).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                globals.ui.tableInvoiceProducts.setStyleSheet("""
                                                       QTableWidget::item {
                                                            background-color: rgb(255, 255, 202); 
                                                            color: black;
                                                       }
                                                       """)
            else: # si no tiene ventas, permite la edicion
                globals.ui.tableInvoiceProducts.setEditTriggers(
                    QAbstractItemView.EditTrigger.AllEditTriggers)
                Invoices.activeSales()

                # globals.ui.tableInvoiceProducts.itemChanged.connect()

        except Exception as e:
            print("error en selectInvoice", e)

    @staticmethod
    def activeSales(row=None):
        try:
            # Si no se pasa fila, añadimos la primera fila
            if row is None:
                row = 0
                globals.ui.tableInvoiceProducts.setRowCount(1)
            else:
                # Si es fila nueva, aumentamos el rowCount
                if row >= globals.ui.tableInvoiceProducts.rowCount():
                    globals.ui.tableInvoiceProducts.setRowCount(row + 1)

            globals.ui.tableInvoiceProducts.setStyleSheet("""
                                       /* Fila seleccionada */
                                       QTableWidget::item:selected {
                                           background-color: #4d5780;  
                                           color: white;                         
                                       }
                                       """)

            # Columna 0 (código)
            globals.ui.tableInvoiceProducts.setItem(row, 0, QtWidgets.QTableWidgetItem(""))
            globals.ui.tableInvoiceProducts.item(row, 0).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            globals.ui.tableInvoiceProducts.setItem(row, 1, QtWidgets.QTableWidgetItem(""))
            globals.ui.tableInvoiceProducts.item(row, 1).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            # Columna 2 (price)
            globals.ui.tableInvoiceProducts.setItem(row, 2, QtWidgets.QTableWidgetItem(""))

            # Columna 3 (cantidad)
            globals.ui.tableInvoiceProducts.setItem(row, 3, QtWidgets.QTableWidgetItem(""))
            globals.ui.tableInvoiceProducts.item(row, 3).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            # Columna 4 (total)
            globals.ui.tableInvoiceProducts.setItem(row, 4, QtWidgets.QTableWidgetItem(""))

            # --- NUEVO: COLUMNA 5 (BOTÓN ELIMINAR) ---
            # Limpiamos cualquier widget previo en la columna 5 por seguridad
            globals.ui.tableInvoiceProducts.removeCellWidget(row, 5)


        except Exception as error:
            print("error active sales", error)

    @staticmethod
    def calculate_totals():
        try:
            globals.subtotal = 0.0
            iva_rate = 0.21

            # Sumamos el total de todas las ventas guardadas en la lista
            for sale in globals.sales:
                # sale[5] es el total de la línea (ej: "150.00€")
                globals.subtotal += float(str(sale[5]).replace('€', ''))

            globals.subtotal = round(globals.subtotal, 2)
            iva = round(globals.subtotal * iva_rate, 2)
            total = round(globals.subtotal + iva, 2)

            # Actualizamos etiquetas
            globals.ui.lblSubTotalInv.setText(f"{globals.subtotal:.2f} €")
            globals.ui.lblIVAInv.setText(f"{iva:.2f} €")
            globals.ui.lblTotalInv.setText(f"{total:.2f} €")
        except Exception as e:
            print("Error recalculando totales:", e)

    @staticmethod
    def crear_boton_borrar(row):
        # Doble comprobación de seguridad: Si está cerrada, no hacemos nada.
        if globals.ui.lblStatusInv.text() == "Cerrada":
            return

        # Si ya hay un widget (un botón), no lo volvemos a crear para no gastar memoria
        if globals.ui.tableInvoiceProducts.cellWidget(row, 5) is not None:
            return

        btn_del = QtWidgets.QPushButton()
        btn_del.setIcon(QIcon("./img/basura.png"))
        btn_del.setFixedSize(24, 24)
        btn_del.setStyleSheet("border: none; background-color: transparent; cursor: pointer;")
        btn_del.clicked.connect(Invoices.borrar_venta_click)

        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.addWidget(btn_del)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        globals.ui.tableInvoiceProducts.setCellWidget(row, 5, container)

    @staticmethod
    def borrar_venta_click():
        try:
            # 1. Obtener el botón pulsado
            boton = QtWidgets.QApplication.focusWidget()
            if not boton: return

            # 2. Obtener la posición y la fila
            button_pos = boton.mapToParent(QtCore.QPoint(0, 0))
            index = globals.ui.tableInvoiceProducts.indexAt(button_pos)

            if index.isValid():

                # 3. Eliminar de globals.sales
                # Solo eliminamos si la fila corresponde a una venta guardada
                # (evitamos borrar la fila vacía de "nueva entrada" si no tiene datos)
                row = index.row()
                mbox = QtWidgets.QMessageBox()
                mbox.setWindowTitle("Warning")
                mbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                mbox.setText("Delete product from invoice?")
                mbox.setStandardButtons(
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
                mbox.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
                mbox.setStyleSheet(globals.mboxStyleSheet)
                resultExec = mbox.exec()
                if resultExec == QtWidgets.QMessageBox.StandardButton.Yes:
                    if row < len(globals.sales):
                        del globals.sales[row]

                        # 4. Eliminar la fila visualmente
                        globals.ui.tableInvoiceProducts.removeRow(row)

                        # 5. Recalcular totales
                        Invoices.calculate_totals()
                    else:
                        # Si el usuario intenta borrar la fila vacía que se genera automáticamente
                        # podemos simplemente limpiarla o no hacer nada.
                        # Si decidimos borrarla visualmente:
                        globals.ui.tableInvoiceProducts.removeRow(row)

        except Exception as e:
            print("Error al borrar venta:", e)
    @staticmethod
    def cellChangedSales(item):
        # print("cell changed sales:")
        try:
            iva = 0.21
            row = item.row()
            col = item.column()
            if col not in (0, 3):
                return

            value = item.text().strip()
            if value == "":
                return

            globals.ui.tableInvoiceProducts.blockSignals(True)

            # Columna 0 entonces buscar producto y rellenar nombre y precio
            if col == 0:
                # data = conexion.Conexion.selectProduct(value) # selecciona producto por ID
                # [15, 'Jamon Serrano', '21', 'Foods', '55.4€']

                producto = ProductService.get_by_id(value) # busca un producto por ID
                if producto:
                    globals.ui.tableInvoiceProducts.setItem(row, 1, QtWidgets.QTableWidgetItem(str(producto.name)))
                    globals.ui.tableInvoiceProducts.setItem(row, 2, QtWidgets.QTableWidgetItem(str(producto.unit_price)))
                    globals.ui.tableInvoiceProducts.setItem(row, 3, QtWidgets.QTableWidgetItem(str(1))) # Amount 1 por defecto
                    globals.ui.tableInvoiceProducts.item(row, 2).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

                    # Calcula el total
                    total = float(producto.unit_price.split("€")[0]) * 1
                    globals.ui.tableInvoiceProducts.setItem(row, 4, QtWidgets.QTableWidgetItem(str(total) + "€")) # Amount 1 por defecto


                else:
                    mbox = QtWidgets.QMessageBox()
                    mbox.setWindowTitle("Invoice")
                    mbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                    mbox.setText("Product do not exist")
                    mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                    mbox.setStyleSheet(globals.mboxStyleSheet)
                    mbox.exec()
                    globals.ui.tableInvoiceProducts.setItem(row, 0, QtWidgets.QTableWidgetItem("")) # Limpia el ID
            # Columna 3 → calcular total
            elif col == 3:
                cantidad = float(value)
                precio_item = globals.ui.tableInvoiceProducts.item(row, 2)
                if precio_item:
                    precio = float(precio_item.text().replace('€', ''))
                    tot = round(precio * cantidad, 2)
                    globals.ui.tableInvoiceProducts.setItem(row, 4, QtWidgets.QTableWidgetItem(str(tot) + '€'))
                    globals.ui.tableInvoiceProducts.item(row, 4).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight
                                                                                  | QtCore.Qt.AlignmentFlag.AlignVCenter)

            globals.ui.tableInvoiceProducts.blockSignals(False)

            # Comprobar si la fila actual está completa y añadir nueva fila
            if all([
                globals.ui.tableInvoiceProducts.item(row, 0) and globals.ui.tableInvoiceProducts.item(row,
                                                                                                      0).text().strip(),
                globals.ui.tableInvoiceProducts.item(row, 1) and globals.ui.tableInvoiceProducts.item(row,
                                                                                                      1).text().strip(),
                globals.ui.tableInvoiceProducts.item(row, 2) and globals.ui.tableInvoiceProducts.item(row,
                                                                                                      2).text().strip(),
                globals.ui.tableInvoiceProducts.item(row, 3) and globals.ui.tableInvoiceProducts.item(row,
                                                                                                      3).text().strip(),
                globals.ui.tableInvoiceProducts.item(row, 4) and globals.ui.tableInvoiceProducts.item(row,
                                                                                                      4).text().strip()
            ]):
                #if len(globals.sales) - 1 >= row:
                #   globals.sales.pop(row)

                if len(globals.sales) - 1 >= row:
                    globals.sales[row] = [globals.ui.lblNumFac.text(), globals.ui.tableInvoiceProducts.item(row, 0).text().strip(),
                     globals.ui.tableInvoiceProducts.item(row, 1).text().strip(),
                     globals.ui.tableInvoiceProducts.item(row, 2).text().strip(),
                     globals.ui.tableInvoiceProducts.item(row, 3).text().strip(),
                     globals.ui.tableInvoiceProducts.item(row, 4).text().strip()]
                else:
                    globals.sales.append(
                    [globals.ui.lblNumFac.text(), globals.ui.tableInvoiceProducts.item(row, 0).text().strip(),
                     globals.ui.tableInvoiceProducts.item(row, 1).text().strip(),
                     globals.ui.tableInvoiceProducts.item(row, 2).text().strip(),
                     globals.ui.tableInvoiceProducts.item(row, 3).text().strip(),
                     globals.ui.tableInvoiceProducts.item(row, 4).text().strip()])
                Invoices.crear_boton_borrar(row)
                rowCount = globals.ui.tableInvoiceProducts.rowCount()
                if rowCount == len(globals.sales):
                    Invoices.activeSales(row=rowCount)
                globals.subtotal = 0
                for sale in globals.sales:
                    globals.subtotal += float(sale[5].replace('€', ''))
                iva = round(globals.subtotal * iva, 2)
                total = round(globals.subtotal + iva, 2)
                globals.ui.lblSubTotalInv.setText(f"{globals.subtotal:.2f} €")
                globals.ui.lblIVAInv.setText(str(iva) + ' €')
                globals.ui.lblTotalInv.setText(str(total) + ' €')
            print(globals.sales)
        except Exception as error:
            print("Error en cellChangedSales:", error)
            globals.ui.tableSales.blockSignals(False)

    @staticmethod
    def saveSales():
        try:
            factura = InvoiceService.get_by_id(int(globals.ui.lblNumFac.text()))
        except:
            factura = None
        if factura is not None:

            mbox = QtWidgets.QMessageBox()
            mbox.setWindowTitle("Warning")
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            mbox.setText("Do you want to emit this invoice?")
            mbox.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            mbox.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
            mbox.setStyleSheet(globals.mboxStyleSheet)
            resultExec = mbox.exec()
            if resultExec == QtWidgets.QMessageBox.StandardButton.Yes:
                # Guardar todas las ventas en BBDD
                persist_sales(factura)
                # imprimir factura si existe
                Reports.reportInvoices( idfac = factura.id )
        else:
            mbox = QtWidgets.QMessageBox()
            mbox.setWindowTitle("Invoice")
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Question)
            mbox.setText("Invoice does not exist. Do you want to save this invoice?")
            mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            mbox.setStyleSheet(globals.mboxStyleSheet)
            resultExec = mbox.exec()
            if resultExec == QtWidgets.QMessageBox.StandardButton.Yes:

                # Guardar factura
                # conexion.Conexion.saveSales(globals.sales)
                factura = None
                try:
                    factura = InvoiceService.create( customer_dni = globals.ui.txtDniCustomerFac.text(), items = None )
                except Exception as error:
                    print("Error al salvar la factura: ", error)


                # Guarda productos en BBDD
                persist_sales(factura)

                globals.ui.tableInvoiceProducts.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                globals.ui.tableInvoiceProducts.setStyleSheet("""
                                                           QTableWidget::item {
                                                                background-color: rgb(255, 255, 202); 
                                                                color: black;
                                                           }
                                                           """)

                #imprimir factura
                Reports.reportInvoices( idfac = factura.id )

def persist_sales(factura: Invoice):
    for sale in globals.sales:
        print(sale)
        try:
            InvoiceService.add_product(
                id_factura=factura.id,
                producto=InvoiceDetail(
                    invoice_id=factura.id,
                    product_id=int(sale[1]),
                    product_name=sale[2],
                    product_price=str(sale[3].split('€')[0]),
                    quantity=int(sale[4]),
                    subtotal=float(str(sale[5]).split("€")[0]),
                ),
            )
        except Exception as error:
            print("Error al salvar la venta: ", error)