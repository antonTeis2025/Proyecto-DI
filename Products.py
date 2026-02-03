import csv
import datetime
import re
import shutil
from tokenize import String

from PIL.ImageFile import Parser
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QMessageBox

import globals
from conexion import Conexion
import events


class Products:

    @staticmethod
    def saveProduct():
        try:
            mbox = QtWidgets.QMessageBox()
            mbox.setWindowTitle("Question?")
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Question)
            mbox.setText("You Want to save this Product?")
            mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            mbox.setStyleSheet(globals.mboxStyleSheet)
            if mbox.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
                newProduct = [globals.ui.txtNameProduct.text(), globals.ui.cmbFamilyProduct.currentText(),
                              globals.ui.txtStockProduct.text(), globals.ui.txtUnitPrice.text()]

                if  Conexion.addProduct(newProduct) and len(newProduct) > 3:
                    mbox = QtWidgets.QMessageBox()
                    mbox.setWindowTitle("Information")
                    mbox.setIcon(QtWidgets.QMessageBox.Icon.Information)
                    mbox.setText("Product Added")
                    mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes)
                    mbox.setStyleSheet(globals.mboxStyleSheet)
                    mbox.exec()
                else:
                    mbox = QtWidgets.QMessageBox()
                    mbox.setWindowTitle("Warning")
                    mbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                    mbox.setText("Error. Product not added, contact with administrator or try again later.")
                    mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes)
                    mbox.setStyleSheet(globals.mboxStyleSheet)
                    mbox.exec()
                Products.loadTableProducts()
        except Exception as e:
            print("error en saveCli ", e)

    @staticmethod
    def loadTableProducts():
        try:
            listTabCustomers = Conexion.listProducts()
            index = 0
            globals.ui.tableProducts.setSortingEnabled(False)
            for record in listTabCustomers:
                globals.ui.tableProducts.setRowCount(index + 1)
                globals.ui.tableProducts.setItem(index, 0, QtWidgets.QTableWidgetItem(str(record[0])))
                globals.ui.tableProducts.setItem(index, 1, QtWidgets.QTableWidgetItem(str(record[1])))
                globals.ui.tableProducts.setItem(index, 2, QtWidgets.QTableWidgetItem(str(record[2])))
                globals.ui.tableProducts.setItem(index, 3, QtWidgets.QTableWidgetItem(str(record[3])))
                globals.ui.tableProducts.setItem(index, 4, QtWidgets.QTableWidgetItem(str(record[4])))
                globals.ui.tableProducts.item(index, 0).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                globals.ui.tableProducts.item(index, 1).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignCenter.AlignCenter)
                globals.ui.tableProducts.item(index, 2).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                globals.ui.tableProducts.item(index, 3).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignCenter.AlignCenter)
                globals.ui.tableProducts.item(index, 4).setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
                )
                index += 1
            globals.ui.tableProducts.setSortingEnabled(True)
        except Exception as error:
            print("error en loadTablecli ", error)
    @staticmethod
    def selectProduct():
        try:

            row = globals.ui.tableProducts.selectedItems()
            data = [dato.text() for dato in row]
            dataComplet = Conexion.dataOneProduct(data[1])
            globals.ui.lblCode.setText(str(dataComplet[0]))
            globals.ui.txtNameProduct.setText(dataComplet[1])
            globals.ui.txtStockProduct.setText(dataComplet[2])
            globals.ui.cmbFamilyProduct.setCurrentText(dataComplet[3])
            globals.ui.txtUnitPrice.setText(dataComplet[4])

            globals.ui.txtNameProduct.setEnabled(False)
            globals.ui.txtNameProduct.setStyleSheet('background-color: rgb(255, 255, 220);')
        except Exception as e:
            print("error en selecProduct ", e)

    @staticmethod
    def cleanProduct():
        try:
            products = [ globals.ui.txtNameProduct, globals.ui.txtStockProduct, globals.ui.txtUnitPrice]
            for product in products:
                product.setText("")
                product.setStyleSheet('background-color: #f4f7fa;')
            globals.ui.lblCode.setText("Autogenerated code")
            globals.ui.cmbFamilyProduct.setCurrentText("Foods")
            globals.ui.txtNameProduct.setEnabled(True)

        except Exception as e:
            print("error en cleanProduct ", e)
    @staticmethod
    def modifyProduct():
        try:
            mbox = QtWidgets.QMessageBox()
            mbox.setWindowTitle("Question")
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Question)
            mbox.setText("Modify Product?")
            mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            mbox.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
            mbox.setStyleSheet(globals.mboxStyleSheet)
            if mbox.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
                dni = globals.ui.txtNameProduct.text()
                modifProduct = [globals.ui.txtNameProduct.text(), globals.ui.txtStockProduct.text(),
                            globals.ui.cmbFamilyProduct.currentText(), globals.ui.txtUnitPrice.text()
                            ]

                if Conexion.modifyProduct(modifProduct):
                    mbox = QtWidgets.QMessageBox()
                    mbox.setWindowTitle("Information")
                    mbox.setIcon(QtWidgets.QMessageBox.Icon.Information)
                    mbox.setText("Product Modified")
                    mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                    mbox.setStyleSheet(globals.mboxStyleSheet)
                    mbox.exec()
                else:
                    mbox = QtWidgets.QMessageBox()
                    mbox.setWindowTitle("Warning")
                    mbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                    mbox.setText("Error. Product not modified")
                    mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                    mbox.setStyleSheet(globals.mboxStyleSheet)
                    mbox.exec()
                Products.loadTableProducts()
            else:
                mbox.hide()
        except Exception as e:
            print("error en modifyProduct ", e)

    @staticmethod
    def delProduct():
        try:
            mbox = QtWidgets.QMessageBox()
            mbox.setWindowTitle("Warning")
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            mbox.setText("Delete Product?")
            mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            mbox.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
            mbox.setStyleSheet(globals.mboxStyleSheet)
            resultExec = mbox.exec()
            if resultExec == QtWidgets.QMessageBox.StandardButton.Yes:
                name = globals.ui.txtNameProduct.text()
                if Conexion.delProduct(name):
                    mbox1 = QtWidgets.QMessageBox()
                    mbox1.setWindowTitle("Information")
                    mbox1.setIcon(QtWidgets.QMessageBox.Icon.Information)
                    mbox1.setText("Delete Product Exito")
                    mbox1.setStyleSheet(globals.mboxStyleSheet)
                    mbox1.exec()
                else:
                    mbox1 = QtWidgets.QMessageBox()
                    mbox1.setWindowTitle("Information")
                    mbox1.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                    mbox1.setText("Delete Product Fail. Contact with administrator or try again later")
                    mbox1.setStyleSheet(globals.mboxStyleSheet)
                    mbox1.exec()
                Products.loadTableProducts()
            elif resultExec == QtWidgets.QMessageBox.StandardButton.No:
                mbox1 = QtWidgets.QMessageBox()
                mbox1.setWindowTitle("Information")
                mbox1.setIcon(QtWidgets.QMessageBox.Icon.Information)
                mbox1.setText("Product Not Deleted")
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
            print("error en delproduct ", e)

    @staticmethod
    def comaPunto(price):
        return price.replace(',','.')


    @staticmethod
    def checkPrice():
        try:
            price = str(globals.ui.txtUnitPrice.text())
            price = Products.comaPunto(price)
            globals.ui.txtUnitPrice.setText(price)
            if not price.endswith("€"):
                globals.ui.txtUnitPrice.setStyleSheet('background-color: #FFC0CB;')
                globals.ui.txtUnitPrice.setText(None)
                globals.ui.txtUnitPrice.setPlaceholderText("Invalid Cuantity")
                return None
            if price.__contains__ ("."):
                parts = price.split(".")
                if len(parts) > 2:
                    globals.ui.txtUnitPrice.setStyleSheet('background-color: #FFC0CB;')
                    globals.ui.txtUnitPrice.setText(None)
                    globals.ui.txtUnitPrice.setPlaceholderText("Invalid Cuantity")
                    return None
                for number in parts[0]:
                    if number.isdigit():
                        continue
                    else:
                        globals.ui.txtUnitPrice.setStyleSheet('background-color: #FFC0CB;')
                        globals.ui.txtUnitPrice.setText(None)
                        globals.ui.txtUnitPrice.setPlaceholderText("Invalid Cuantity")
                        return None
                if len(parts[1]) > 3:
                    globals.ui.txtUnitPrice.setStyleSheet('background-color: #FFC0CB;')
                    globals.ui.txtUnitPrice.setText(None)
                    globals.ui.txtUnitPrice.setPlaceholderText("Invalid Cuantity")
                    return None

                for number in parts[1][0:len(parts[1])-2]:
                    if number.isdigit():
                        continue
                    else:
                        globals.ui.txtUnitPrice.setStyleSheet('background-color: #FFC0CB;')
                        globals.ui.txtUnitPrice.setText(None)
                        globals.ui.txtUnitPrice.setPlaceholderText("Invalid Cuantity")
                        return None
                globals.ui.txtUnitPrice.setStyleSheet('background-color: rgb(255, 255, 220);')
            elif not price.__contains__("."):
                for number in price[0:len(price)-1]:
                    if number.isdigit():
                        continue
                    else:
                        globals.ui.txtUnitPrice.setStyleSheet('background-color: #FFC0CB;')
                        globals.ui.txtUnitPrice.setText(None)
                        globals.ui.txtUnitPrice.setPlaceholderText("Invalid Cuantity")
                        return None
                globals.ui.txtUnitPrice.setStyleSheet('background-color: rgb(255, 255, 220);')

            else:

                globals.ui.txtUnitPrice.setStyleSheet('background-color: #FFC0CB;')
                globals.ui.txtUnitPrice.setText(None)
                globals.ui.txtUnitPrice.setPlaceholderText("Invalid Cuantity")
        except Exception as e:
            print("error en checkPrice ", e)