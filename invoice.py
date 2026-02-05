import datetime
from itertools import product

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QAbstractItemView
from sqlalchemy.engine import row

import conexion
import globals
from conexion import Conexion
from models import InvoiceDetail
from reports import Reports
from services.customer_service import CustomerService
from services.invoice_service import InvoiceService
from services.product_service import ProductService


class Invoice:
    isSaleAlreadyDone = False

    @staticmethod
    def dataCustomer(widget):
        try:
            dni = widget.text().strip().upper()
            if dni == "":
                dni = "00000000T"
                globals.ui.txtDniCustomerFac.setText(dni)
            if conexion.Conexion.buscaCli(dni):
                record = conexion.Conexion.dataOneCustomer(dni)
                globals.ui.lblNameInv.setText(record[3] + " " + record[2])
                globals.ui.lblInvoiceTypeInv.setText(record[9].capitalize())
                globals.ui.lblAddressInv.setText(record[6]) if dni == "00000000T" else globals.ui.lblAddressInv.setText(
                    record[6] + ", " + record[8] + ", " + record[7])
                globals.ui.lblMobileInv.setText(record[5])
                globals.ui.lblStatusInv.setText("Inactivo" if record[4] == "True" else "Activo")
                print("Doy de alta la factura")
            else:
                mbox = QtWidgets.QMessageBox()
                mbox.setWindowTitle("Invoice")
                mbox.setIcon(QtWidgets.QMessageBox.Icon.Information)
                mbox.setText("Customer doesn't exist.")
                mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                mbox.setStyleSheet(globals.mboxStyleSheet)
                mbox.exec()
                Invoice.cleanInv()
                print("No doy de alta la factura")
        except Exception as e:
            print("error en saveInvoice", e)

    @staticmethod
    def checkDni():
        dni = globals.ui.txtDniCustomerFac.text().strip().upper()
        globals.ui.txtDniCustomerFac.setText(dni)
        Invoice.dataCustomer(globals.ui.txtDniCustomerFac)

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
            Invoice.activeSales()
            globals.sales = []
        except Exception as e:
            print("error en cleanInv", e)

    @staticmethod
    def saveInvoice():
        # Conseguir el DNI de la caja de texto
        dni = globals.ui.txtDniCustomerFac.text().strip().upper()
        if dni == "":
            dni = "00000000T"
        # Conseguir el cliente de la BBDD

        cliente = CustomerService.get_by_dni(dni)
        # print("DBG---------------------------")
        # print(cliente)
        # print("DBG---------------------------")
        if cliente:
            # Poner DNI en la caja de texto
            globals.ui.txtDniCustomerFac.setText(dni)
            # Poner la fecha actual en la caja de texto
            data = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
            globals.ui.lblFechaFac.setText(data)
            # Crear factura
            factura = None
            try:
                factura = InvoiceService.create(customer_dni = dni, items = None)
            except Exception as e:
                print(f"ERROR AL CREAR FACTURA: {e}")

            if factura != None: # Si el proceso no falla
                Invoice.loadTableFac(True)
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
            mbox.setText("Misseing Information")
            mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
            mbox.setStyleSheet(globals.mboxStyleSheet)
            mbox.exec()

        Invoice.loadTableFac(False)

    @staticmethod
    def loadTableFac(showData=False):
        try:
            # records = conexion.Conexion.allInvoice()
            # record: ['16', '00000000T', '26/11/2025-09:42']
            records = InvoiceService.get_all()
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

                globals.ui.tableInvoiceList.item(index, 0).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
                globals.ui.tableInvoiceList.item(index, 1).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignCenter.AlignCenter)
                globals.ui.tableInvoiceList.item(index, 2).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)

                #CREAR BOTON ELIMINAR FILA
                index += 1
            Invoice.checkDni()
        except Exception as e:
            print("error en loadTableFac", e)

    @staticmethod
    def selectInvoice():
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
            Invoice.checkDni()

            #selectedSales = conexion.Conexion.loadSalesByFac(data[0])

            # data[0] -> id
            # Carga las ventas de la factura seleccionada
            sales = InvoiceService.get_by_id(int(data[0])).details

            if sales != []: # Si existen ventas -> se bloqueara la edicion (factura inactiva)
                Invoice.isSaleAlreadyDone = True
                Invoice.activeSales() # calcula las columnas
                globals.ui.tableInvoiceProducts.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # hace que no se pueda editar la tabla
                globals.ui.lblStatusInv.setText("Cerrada")
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
                Invoice.activeSales()

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

        except Exception as error:
            print("error active sales", error)

    @staticmethod
    def cellChangedSales(item):
        print("cell changed sales:")
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

                rowCount = globals.ui.tableInvoiceProducts.rowCount()
                if rowCount == len(globals.sales):
                    Invoice.activeSales(row=rowCount)
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
            # imprimir factura si existe
            Reports.reportInvoices( idfac = factura.id )
        else:
            mbox = QtWidgets.QMessageBox()
            mbox.setWindowTitle("Invoice")
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Question)
            mbox.setText("Do you want to save this invoice?")
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


                # Guardar sus productos recorriendo la tabla
                productos = Invoice.getInvoiceProducts()
                # todo: implementar esto
                for producto in productos:
                    if producto != productos[productos.count()-1]:
                        try:
                            InvoiceService.add_product(
                                id_factura = factura.id,
                                producto = InvoiceDetail(
                                    invoice_id = factura.id,
                                    product_id = int(producto.Code),
                                    product_name = producto.Name,
                                    product_price = str(producto.Price),
                                    quantity = producto.Amount,
                                    subtotal = float(str(producto.Total).split("€")[0]),
                                ),
                            )
                        except Exception as error:
                            print("Error al salvar la venta: ", error)

                globals.ui.tableInvoiceProducts.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                globals.ui.tableInvoiceProducts.setStyleSheet("""
                                                           QTableWidget::item {
                                                                background-color: rgb(255, 255, 202); 
                                                                color: black;
                                                           }
                                                           """)

                #imprimir factura
                Reports.reportInvoices( idfac = factura.id )

    @staticmethod
    def getInvoiceProducts():

        lista_ventas = []

        tabla = globals.ui.tableInvoiceProducts

        datos_tabla = []

        for f in range(tabla.rowCount()):
            datos_fila = {}
            for c in range(tabla.columnCount()):
                # Usamos el encabezado de la columna como clave del diccionario
                header = tabla.horizontalHeaderItem(c).text()
                item = tabla.item(f, c)
                datos_fila[header] = item.text() if item else ""

            datos_tabla.append(datos_fila)

        return datos_tabla
        # print("DBG Extract products-----------------------------------")
        # print(datos_tabla) [{'Code': '15', 'Name': 'Jamon Serrano', 'Price': '55.4€', 'Amount': '1', 'Total': '55.4€'}, {'Code': '13', 'Name': 'Lasaña', 'Price': '2.21€', 'Amount': '1', 'Total': '2.21€'}, {'Code': '', 'Name': '', 'Price': '', 'Amount': '', 'Total': ''}]
        # print("DBG----------------------------------------------------")