import csv
import datetime
import os
import shutil
import sys
import time

from PyQt6 import QtWidgets, QtCore, QtGui
import zipfile
import conexion
import globals
from customers import Customers
from services.customer_service import CustomerService
from services.location_service import LocationService


class Events:
    @staticmethod
    def messageExit():
        try:
            mbox = QtWidgets.QMessageBox()
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Question)
            mbox.setWindowIcon(QtGui.QIcon("./img/logo.png"))
            mbox.setWindowTitle("Exit Message")
            mbox.setText("Are you sure you want to exit?")
            mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            mbox.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
            mbox.setStyleSheet(globals.mboxStyleSheet)
            if mbox.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
                sys.exit()
            else:
                mbox.hide()
        except Exception as e:
            print("error salida", e)

    @staticmethod
    def messageAbout():
        try:
            globals.venAbout.show()
        except Exception as e:
            print("error en mostrar version", e)

    @staticmethod
    def closeAbout():
        try:
            globals.venAbout.hide()
        except Exception as e:
            print("error en cerrar version", e)

    def openCalendar(self):
        try:
            globals.vencal.show()
        except Exception as e:
            print("error en claendario", e)

    def loadData(qDate):
        try:
            data = ('{:02d}/{:02d}/{:4d}'.format(qDate.day(), qDate.month(), qDate.year()))
            if globals.ui.panMain.currentIndex() == 0:
                globals.ui.txtAltacli.setText(data)
            time.sleep(0.1)
            globals.vencal.hide()

        except Exception as e:
            print("error en cargar Data", e)


    def loadProvincia(self):
        try:
            globals.ui.cmbProvincecli.clear()
            # list = conexion.Conexion.listProv(self)
            list = LocationService.get_all_provinces()

            provs = [obj.name for obj in list]

            globals.ui.cmbProvincecli.addItems(provs)

        except Exception as e:
            print("error en cargar Provincia:", e)

    def loadMunicli(self):
        try:
            # Obtenemos el objeto provincia segun la que haya seleccionado el usuario
            provinciaTxt = globals.ui.cmbProvincecli.currentText()
            prov = LocationService.get_province_by_name(provinciaTxt)
            # Obtenemos una lista de municipios
            munis = LocationService.get_municipalities_by_province(prov.id)
            # La pasamos a texto
            list = [muni.name for muni in munis]
            # Insertamos dentro del propio comboBox
            globals.ui.cmbCitycli.clear()
            globals.ui.cmbCitycli.addItems(list)
        except Exception as e:
            print("error en cargar Municipio:", e)

    def resizeTabCustomer(self):
        try:
            header = globals.ui.tableCustomerList.horizontalHeader()
            for i in range(header.count()):
                if i == 2:
                    header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
                else:
                    header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Stretch)
                header_items = globals.ui.tableCustomerList.horizontalHeaderItem(i)
                font = header_items.font()
                font.setBold(True)
                header_items.setFont(font)
        except Exception as e:
            print("error en cargar Tab Customer:", e)

    def saveBackup(self):
        try:
            data = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            fileName = data + "_backup.zip"
            directory, file = globals.dlgopen.getSaveFileName(None, "Save Backup File", fileName, "zip")

            if globals.dlgopen.accept and file:
                filezip = zipfile.ZipFile(file, 'w')
                # filezip.write('./data/bbdd.sqlite', os.path.basename('data/bbdd.sqlite'))
                filezip.write('./data/actual.sqlite', os.path.basename('data/actual.sqlite'))
                filezip.close()
                shutil.move(file, directory)
                mbox = QtWidgets.QMessageBox()
                mbox.setIcon(QtWidgets.QMessageBox.Icon.Information)
                mbox.setWindowIcon(QtGui.QIcon("./img/logo.png"))
                mbox.setWindowTitle("Save Backup")
                mbox.setText("Save Backup Done")
                mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                mbox.setStyleSheet(globals.mboxStyleSheet)
                mbox.exec()
        except Exception as e:
            print("error en save backup", e)

    def restoreBackup(self):
        try:
            filename = globals.dlgopen.getOpenFileName(None, "Restore Backup File", '', "*.zip;;All Files (*)")
            file = filename[0]
            if file:
                with zipfile.ZipFile(file, 'r') as bbdd:
                    bbdd.extractall(path='./data' ,pwd=None)
                    #shutil.move('bbdd.sqlite', './data')
                bbdd.close()
                mbox = QtWidgets.QMessageBox()
                mbox.setIcon(QtWidgets.QMessageBox.Icon.Information)
                mbox.setWindowIcon(QtGui.QIcon("./img/logo.png"))
                mbox.setWindowTitle("Restore Backup")
                mbox.setText("Restore Backup Done")
                mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                mbox.setStyleSheet(globals.mboxStyleSheet)
                mbox.exec()
                conexion.Conexion.db_conexion()
                Events.loadProvincia(self)
                Customers.loadTablecli(True)
        except Exception as e:
            print("error en restore backup", e)

    @staticmethod
    def exportXlsCustomers():
        try:
            data = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            copy = str(data) + '_customers.csv'
            directory, file = globals.dlgopen.getSaveFileName(None, "Save Backup file", copy, '.csv')
            # globals.dlgOpen.centrar()
            var = False
            if file:
                records = CustomerService.get_all()
                # records = conexion.Conexion.listCustomers(var)
                with open(file, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['DNI_NIE', 'AddData', 'Surname', 'Name', 'eMail', 'Mobile', 'Address',
                                     'Province', 'City', 'InvoiceType', 'Active'])
                    for record in records:
                        prov = LocationService.get_province_by_municipality(record.municipality_id)
                        writer.writerow(f"{record.dni}, {record.addData}, {record.surname}, {record.name}, {record.email}, {record.mobile}, {record.address}, {prov.name},{record.municipality_id} ,{record.invoice_type}, {record.active}")
                        # writer.writerow(record)
                shutil.move(file, directory)
                mbox = QtWidgets.QMessageBox()
                mbox.setIcon(QtWidgets.QMessageBox.Icon.Information)
                mbox.setWindowIcon(QtGui.QIcon('./img/logo.ico'))
                mbox.setWindowTitle('Export Customers')
                mbox.setText('Export Customers Done')
                mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                mbox.exec()
            else:
                mbox = QtWidgets.QMessageBox()
                mbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                mbox.setWindowIcon(QtGui.QIcon('./img/logo.ico'))
                mbox.setWindowTitle('Export Customers')
                mbox.setText('Export Customers Error')
                mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                mbox.exec()
        except Exception as e:
            print("Error en exportar customers", e)


    def loadStatusBar(self):
        try:
            data = datetime.datetime.now().strftime('%d/%m/%y')
            self.labelstatus = QtWidgets.QLabel(self)
            self.labelstatus.setText(data)
            self.labelstatus.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            globals.ui.statusbar.addPermanentWidget(self.labelstatus)
            self.labelversion = QtWidgets.QLabel(self)
            self.labelversion.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.labelversion.setText("Version 0.0.1")
            self.labelversion.setObjectName("labelversion")
            globals.ui.statusbar.addPermanentWidget(self.labelversion)
        except Exception as e:
            print("error en loadStatusBar", e)

    def resizeTabProducts(self):
        try:
            header = globals.ui.tableProducts.horizontalHeader()
            for i in range(header.count()):
                if i in (0, 2, 4):
                    header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
                else:
                    header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Stretch)
                header_items = globals.ui.tableProducts.horizontalHeaderItem(i)
                font = header_items.font()
                font.setBold(True)
                header_items.setFont(font)
        except Exception as e:
            print("error en cargar Tab Customer:", e)

    @staticmethod
    def resizeTabInvProducts():
        try:
            header = globals.ui.tableInvoiceProducts.horizontalHeader()
            for i in range(header.count()):
                if i == 0:
                    header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
                else:
                    header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Stretch)
                header_items = globals.ui.tableProducts.horizontalHeaderItem(i)
                font = header_items.font()
                font.setBold(True)
                header_items.setFont(font)
        except Exception as e:
            print("error en Resize Tab Inv Products", e)

    @staticmethod
    def resizeTabInv():
        try:
            header = globals.ui.tableInvoiceList.horizontalHeader()
            for i in range(header.count()):
                if i in (0, 1):
                    header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
                elif i == 3:
                    header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Fixed)
                    globals.ui.tableInvoiceList.setColumnWidth(3, 32)
                else:
                    header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Stretch)
                header_items = globals.ui.tableInvoiceList.horizontalHeaderItem(i)
                font = header_items.font()
                font.setBold(True)
                header_items.setFont(font)
        except Exception as e:
            print("error en cargar Tab inv fac:", e)
