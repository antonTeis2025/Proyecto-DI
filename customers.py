import csv
import datetime
import re
import shutil

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QMessageBox

import globals
from conexion import Conexion
from models import Customer
from services.customer_service import CustomerService
from services.location_service import LocationService


def rellenarTextos(customer: Customer):
    # Poner los textos
    globals.ui.txtDnicli.setText(customer.dni)
    globals.ui.txtAltacli.setText(customer.add_data)
    globals.ui.txtApelcli.setText(customer.surname)
    globals.ui.txtNombrecli.setText(customer.name)
    globals.ui.txtEmailcli.setText(customer.email)
    globals.ui.txtMobilecli.setText(customer.mobile)
    globals.ui.txtAddresscli.setText(customer.address)
    globals.ui.cmbProvincecli.setCurrentText(customer.province_name)
    globals.ui.cmbCitycli.setCurrentText(customer.city_name)

    if str(customer.invoice_type) == "paper":
        globals.ui.rbtFacpapel.setChecked(True)
    else:
        globals.ui.rbtFace.setChecked(True)
    if str(customer.historical) == "False":
        globals.ui.lblWarning.setText("Hystoricarl Client")
        globals.ui.lblWarning.setStyleSheet("background-color: rgb(255,255,200); color: red;")


class Customers:


    @staticmethod
    def checkDni():
        """
        Módulo para comprobar si el DNI esta correcto

        """
        try:
            globals.ui.txtDnicli.editingFinished.disconnect(Customers.checkDni)
            dni = globals.ui.txtDnicli.text()
            dni = str(dni).upper()
            globals.ui.txtDnicli.setText(dni)
            tabla = "TRWAGMYFPDXBNJZSQVHLCKE"
            dig_ext = "XYZ"
            reemp_dig_ext = {'X': '0', 'Y': '1', 'Z': '2'}
            numeros = "1234567890"
            if len(dni) == 9:
                dig_control = dni[8]
                dni = dni[:8]
                if dni[0] in dig_ext:
                    dni = dni.replace(dni[0], reemp_dig_ext[dni[0]])
                if len(dni) == len([n for n in dni if n in numeros]) and tabla[int(dni) % 23] == dig_control:
                    globals.ui.txtDnicli.setStyleSheet('background-color: rgb(255, 255, 220);')
                else:
                    globals.ui.txtDnicli.setStyleSheet('background-color:#FFC0CB;')
                    globals.ui.txtDnicli.setText(None)
                    globals.ui.txtDnicli.setFocus()
            else:
                globals.ui.txtDnicli.setStyleSheet('background-color:#FFC0CB;')
                globals.ui.txtDnicli.setText(None)
                globals.ui.txtDnicli.setPlaceholderText("Invalid DNI")

        except Exception as error:
            print("error en validar dni ", error)
        finally:
            globals.ui.txtDnicli.editingFinished.connect(Customers.checkDni)

    @staticmethod
    def capitalizar(texto, widget):
        """
        Función para capitalizar el texto pasado en el widget dado.

        :param texto:
        :type texto: basestring
        :param widget:
        :type widget: widget
        """
        try:
            texto = texto.title()
            widget.setText(texto)
        except Exception as error:
            print("error en capitalizar texto ", error)

    @staticmethod
    def checkEmail(email):
        """
        Comprueba si el email tiene  un formato valido.

        :param email:
        :type email: basestring
        """
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if re.match(patron, email):
            globals.ui.txtEmailcli.setStyleSheet('background-color: rgb(255, 255, 220);')
        else:
            globals.ui.txtEmailcli.setStyleSheet('background-color: #FFC0CB;')
            globals.ui.txtEmailcli.setText(None)
            globals.ui.txtEmailcli.setPlaceholderText("Invalid Email")

    @staticmethod
    def checkMobile(numero):
        """

        Comprueba si el numero de telefono tiene  un formato valido.

        :param numero:
        :type numero: basestring
        """
        patron = r'^[67]\d{8}$'
        if re.match(patron, numero):
            globals.ui.txtMobilecli.setStyleSheet('background-color: rgb(255, 255, 220);')
        else:
            globals.ui.txtMobilecli.setStyleSheet('background-color: #FFC0CB;')
            globals.ui.txtMobilecli.setText(None)
            globals.ui.txtMobilecli.setPlaceholderText("Invalid Number")

    @staticmethod
    def loadTablecli(var):
        """

        Funcion para cargar la tabla de clientes de la base de datos a la aplicacion.

        :param var: Incica si tambien se deben incluir los que no son historicos o no
        :type var: bool
        """
        try:
            # var indica si está el historico activado o no # si está activado el historico es false
            # listTabCustomers = Conexion.listCustomers(var)
            if var:
                customers = CustomerService.get_all(True) # Activos e inactivos (chkbx)
            else:
                customers = CustomerService.get_all(False) # Solo activos

            # ['32516522L', '20/01/2022', 2'Domínguez Soto', '3Lucía', '4lucía.domínguez@example.com', '5647009029', '6Calle Luna 33', '7prov', '8muni', '9electronic', '10True']
            index = 0
            for record in customers:
                globals.ui.tableCustomerList.setRowCount(index + 1)
                globals.ui.tableCustomerList.setItem(index, 0, QtWidgets.QTableWidgetItem(str(record.surname)))
                globals.ui.tableCustomerList.setItem(index, 1, QtWidgets.QTableWidgetItem(str(record.name)))
                globals.ui.tableCustomerList.setItem(index, 2, QtWidgets.QTableWidgetItem(str(" " + record.mobile) + " "))
                globals.ui.tableCustomerList.setItem(index, 3, QtWidgets.QTableWidgetItem(str(record.province_name)))
                globals.ui.tableCustomerList.setItem(index, 4, QtWidgets.QTableWidgetItem(str(record.city_name)))
                globals.ui.tableCustomerList.setItem(index, 5, QtWidgets.QTableWidgetItem(str(record.invoice_type)))
                if record.historical == "True":
                    globals.ui.tableCustomerList.setItem(index, 6, QtWidgets.QTableWidgetItem("Alta"))
                else:
                    globals.ui.tableCustomerList.setItem(index, 6, QtWidgets.QTableWidgetItem("Baja"))
                globals.ui.tableCustomerList.item(index, 0).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignLeft.AlignVCenter)
                globals.ui.tableCustomerList.item(index, 1).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignLeft.AlignVCenter)
                globals.ui.tableCustomerList.item(index, 2).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignCenter.AlignCenter)
                globals.ui.tableCustomerList.item(index, 3).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignCenter.AlignCenter)
                globals.ui.tableCustomerList.item(index, 4).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignCenter.AlignCenter)
                globals.ui.tableCustomerList.item(index, 5).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignCenter.AlignCenter)
                index += 1
        except Exception as error:
            print("error en loadTablecli ", error)

    @staticmethod
    def selectCustomer():
        """

        Carga los datos de el cliente que esté seleccionado en la tabla.

        """
        try:

            # Obtener el movil del cliente recien pulsado
            row = globals.ui.tableCustomerList.selectedItems()
            data = [dato.text() for dato in row]
            mobile = str(data[2]).replace(" ", "")
            # Obtener el cliente a partir del movil
            customer = CustomerService.get_by_mobile(mobile)

            # dataComplet = Conexion.dataOneCustomer(data[2].strip())

            globals.estado = customer.historical #Set la variable de estado del clienta el selecionarlo para el modify

            rellenarTextos(customer)
            globals.ui.txtDnicli.setEnabled(False)
            globals.ui.txtDnicli.setStyleSheet('background-color: rgb(255, 255, 220);')
        except Exception as e:
            print("error en selectCustomer ", e)

    @staticmethod
    def delCustomer():
        """

        Cambia el estado del cliente a historico. Antes manda una confirmación de la acción

        """
        try:
            mbox = QtWidgets.QMessageBox()
            mbox.setWindowTitle("Warning")
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            mbox.setText("Delete Customer?")
            mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            mbox.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
            mbox.setStyleSheet(globals.mboxStyleSheet)
            resultExec = mbox.exec()
            if resultExec == QtWidgets.QMessageBox.StandardButton.Yes:
                dni = globals.ui.txtDnicli.text()

                cliente = CustomerService.get_by_dni(dni)

                try:
                    CustomerService.delete(str(cliente.dni))

                    mbox1 = QtWidgets.QMessageBox()
                    mbox1.setWindowTitle("Information")
                    mbox1.setIcon(QtWidgets.QMessageBox.Icon.Information)
                    mbox1.setText("Delete Customer Exito")
                    mbox1.setStyleSheet(globals.mboxStyleSheet)
                    mbox1.exec()
                    print(f"Eliminado cliente con DNI {cliente.dni}")
                except:
                    mbox1 = QtWidgets.QMessageBox()
                    mbox1.setWindowTitle("Information")
                    mbox1.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                    mbox1.setText("Delete Customer Fail. Contact with administrator or try again later")
                    mbox1.setStyleSheet(globals.mboxStyleSheet)
                    mbox1.exec()


                Customers.loadTablecli(True)
            elif resultExec == QtWidgets.QMessageBox.StandardButton.No:
                mbox1 = QtWidgets.QMessageBox()
                mbox1.setWindowTitle("Information")
                mbox1.setIcon(QtWidgets.QMessageBox.Icon.Information)
                mbox1.setText("Customer Not Deleted")
                mbox1.setStyleSheet(globals.mboxStyleSheet)
                mbox1.exec()
            else:
                mbox2 = QtWidgets.QMessageBox()
                mbox2.setWindowTitle("Warning")
                mbox2.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                mbox2.setText("Error. Contact with administrator or try again later")
                mbox2.setStyleSheet(globals.mboxStyleSheet)
                mbox2.exec()

        except Exception as e:
            print("error en delCustomer ", e)

    @staticmethod
    def historicoCli():
        """

        Mustra los clientes en funcion de el estado del chkHistoriccli.

        """
        try:
            if globals.ui.chkHistoriccli.isChecked():
                var = False # si esta checkeado e sfalse
            else:
                var = True
            Customers.loadTablecli(var)
        except Exception as e:
            print("error en historicoCli ", e)

    @staticmethod
    def saveCli():
        """

        Guarda un cliente en la base de datos.

        """
        try:
            mbox = QtWidgets.QMessageBox()
            mbox.setWindowTitle("Question?")
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Question)
            mbox.setText("You Want to save this customer?")
            mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            mbox.setStyleSheet(globals.mboxStyleSheet)
            if mbox.exec() == QtWidgets.QMessageBox.StandardButton.Yes:



                # newCli = [globals.ui.txtDnicli.text(), globals.ui.txtAltacli.text(), globals.ui.txtApelcli.text(),
                #          globals.ui.txtNombrecli.text(), globals.ui.txtEmailcli.text(), globals.ui.txtMobilecli.text(),
                #          globals.ui.txtAddresscli.text(), globals.ui.cmbProvincecli.currentText(),
                #          globals.ui.cmbCitycli.currentText(),
                #          ]
                if globals.ui.rbtFacpapel.isChecked():
                    factura = "paper"
                else:
                    factura = "electronic"
                # newCli.append(factura)

                cus = CustomerService.create(
                    dni = globals.ui.txtDnicli.text(),
                    surname = globals.ui.txtApelcli.text(),
                    name = globals.ui.txtNombrecli.text(),
                    email = globals.ui.txtEmailcli.text(),
                    mobile = globals.ui.txtMobilecli.text(),
                    address = globals.ui.txtAddresscli.text(),
                    province_name = globals.ui.cmbProvincecli.currentText(),
                    city_name = globals.ui.cmbCitycli.currentText(),
                    invoice_type = factura,
                    add_data = globals.ui.txtAltacli.text(),
                )

                if cus:
                    mbox = QtWidgets.QMessageBox()
                    mbox.setWindowTitle("Information")
                    mbox.setIcon(QtWidgets.QMessageBox.Icon.Information)
                    mbox.setText("Client Added")
                    mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes)
                    mbox.setStyleSheet(globals.mboxStyleSheet)
                    mbox.exec()
                else:
                    mbox = QtWidgets.QMessageBox()
                    mbox.setWindowTitle("Warning")
                    mbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                    mbox.setText("Error. Client not added, contact with administrator or try again later")
                    mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes)
                    mbox.setStyleSheet(globals.mboxStyleSheet)
                    mbox.exec()
                Customers.loadTablecli(True)
        except Exception as e:
            print("error en saveCli ", e)

    def cleanCli(self):
        """

        Limpia la zona de los datos del cliente en la aplicación.

        """
        import events
        try:
            cli = [globals.ui.txtDnicli, globals.ui.txtAltacli, globals.ui.txtApelcli,
                   globals.ui.txtNombrecli, globals.ui.txtEmailcli, globals.ui.txtMobilecli,
                   globals.ui.txtAddresscli,
                   ]
            for i, dato in enumerate(cli):
                cli[i] = dato.setText("")
            events.Events.loadProvincia(self)
            globals.ui.cmbCitycli.clear()
            globals.ui.txtEmailcli.setStyleSheet('background-color: #f4f7fa;')
            globals.ui.txtEmailcli.setPlaceholderText("")
            globals.ui.txtMobilecli.setStyleSheet('background-color: #f4f7fa;')
            globals.ui.txtMobilecli.setPlaceholderText("")
            globals.ui.txtDnicli.setStyleSheet('background-color: #f4f7fa;')
            globals.ui.txtDnicli.setPlaceholderText("")
            globals.ui.txtDnicli.setEnabled(True)
            globals.ui.lblWarning.setText("")
            globals.ui.lblWarning.setStyleSheet("background-color: #e6ecf3;")

        except Exception as e:
            print("error en cleanCli ", e)

    def modifCli(self):
        """

        Modifica los datos del cliente que se este modificando en ese momento.

        """
        try:
            if globals.estado == str(False):
                mbox = QtWidgets.QMessageBox()
                mbox.setWindowTitle("Information")
                mbox.setIcon(QtWidgets.QMessageBox.Icon.Information)
                mbox.setText("Client no activated. Do you want to activate it?")
                mbox.setStandardButtons(
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
                mbox.setStyleSheet(globals.mboxStyleSheet)
                if mbox.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
                    globals.estado = str(True)

            mbox = QtWidgets.QMessageBox()
            mbox.setWindowTitle("Question")
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Question)
            mbox.setText("Modify Customer?")
            mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            mbox.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
            mbox.setStyleSheet(globals.mboxStyleSheet)
            if mbox.exec() == QtWidgets.QMessageBox.StandardButton.Yes:


                dni = globals.ui.txtDnicli.text()


                # modifCli = [globals.ui.txtAltacli.text(), globals.ui.txtApelcli.text(),
                #             globals.ui.txtNombrecli.text(), globals.ui.txtEmailcli.text(),
                #            globals.ui.txtMobilecli.text(),
                #            globals.ui.txtAddresscli.text(), globals.ui.cmbProvincecli.currentText(),
                #            globals.ui.cmbCitycli.currentText(), globals.estado
                #            ]

                # modifCli.append(factura)

                if globals.ui.rbtFacpapel.isChecked():
                    factura = "paper"
                else:
                    factura = "electronic"

                up = CustomerService.update(
                    dni = dni, # pk

                    add_data = globals.ui.txtAltacli.text(),
                    surname = globals.ui.txtApelcli.text(),
                    name = globals.ui.txtNombrecli.text(),
                    email = globals.ui.txtEmailcli.text(),
                    mobile = globals.ui.txtMobilecli.text(),
                    address = globals.ui.txtAddresscli.text(),
                    province_name = globals.ui.cmbProvincecli.currentText(),
                    city_name = globals.ui.cmbCitycli.currentText(),
                    historical = globals.estado,
                    invoice_type = factura
                )



                if up:
                    mbox = QtWidgets.QMessageBox()
                    mbox.setWindowTitle("Information")
                    mbox.setIcon(QtWidgets.QMessageBox.Icon.Information)
                    mbox.setText("Client Modified")
                    mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                    mbox.setStyleSheet(globals.mboxStyleSheet)
                    mbox.exec()
                else:
                    mbox = QtWidgets.QMessageBox()
                    mbox.setWindowTitle("Warning")
                    mbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                    mbox.setText("Error. Client not modified")
                    mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                    mbox.setStyleSheet(globals.mboxStyleSheet)
                    mbox.exec()
                Customers.loadTablecli(True)
                globals.ui.chkHistoriccli.setChecked(False)
            else:
                mbox.hide()
        except Exception as e:
            print("error en modifCli ", e)

    @staticmethod
    def buscaCli():
        """

        Busca el cliente por el DNI indicado en la aplicacion.

        """
        try:
            # Obtenemos DNI de caja de texto
            dni = globals.ui.txtDnicli.text()

            # Obtenemos la entidad
            customer = CustomerService.get_by_dni(dni)

            if not customer: # Manejar que no encuentre el cliente
                mbox = QtWidgets.QMessageBox()
                mbox.setWindowTitle("Information")
                mbox.setIcon(QtWidgets.QMessageBox.Icon.Information)
                mbox.setText("Client Not Exists")
                mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                mbox.setStyleSheet(globals.mboxStyleSheet)
                mbox.exec()
            else:

                # Cambiar color de las cajas
                boxes = [globals.ui.txtDnicli, globals.ui.txtAltacli, globals.ui.txtApelcli,
                         globals.ui.txtNombrecli, globals.ui.txtEmailcli, globals.ui.txtMobilecli,
                         globals.ui.txtAddresscli]
                for box in boxes:
                    box.setStyleSheet("background-color: #f4f7fa;")

                rellenarTextos(customer)

        except Exception as e:
            print("error en buscaCli ", e)


