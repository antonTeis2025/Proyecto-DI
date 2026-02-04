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
from services.product_service import ProductService


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
                #newProduct = [globals.ui.txtNameProduct.text(), globals.ui.cmbFamilyProduct.currentText(),
                #              globals.ui.txtStockProduct.text(), globals.ui.txtUnitPrice.text()]

                producto = ProductService.create(
                    name = globals.ui.txtNameProduct.text(),
                    family = globals.ui.cmbFamilyProduct.currentText(),
                    stock = globals.ui.txtStockProduct.text(),
                    price = globals.ui.txtUnitPrice.text() + "€"
                )

                if  producto:
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
            print("error en saveProduct ", e)

    @staticmethod
    def loadTableProducts():
        try:
            #print("load table productos")
            # listTabCustomers = Conexion.listProducts()
            productos = ProductService.get_all()
            index = 0
            globals.ui.tableProducts.setSortingEnabled(False)
            for record in productos:
                # [11, 'Mobile', '231', 'Electronic', '185.36€']
                globals.ui.tableProducts.setRowCount(index + 1)
                globals.ui.tableProducts.setItem(index, 0, QtWidgets.QTableWidgetItem(str(record.id)))
                globals.ui.tableProducts.setItem(index, 1, QtWidgets.QTableWidgetItem(str(record.name)))
                globals.ui.tableProducts.setItem(index, 2, QtWidgets.QTableWidgetItem(str(record.stock)))
                globals.ui.tableProducts.setItem(index, 3, QtWidgets.QTableWidgetItem(str(record.family)))
                globals.ui.tableProducts.setItem(index, 4, QtWidgets.QTableWidgetItem(str(record.unit_price)))
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
            # print(data): ['14', 'Pantalon', '25', 'Clothes', '3.35€']
            # dataComplet = Conexion.dataOneProduct(data[1])

            producto = ProductService.get_by_id(int(data[0]))

            globals.ui.lblCode.setText(str(producto.id))
            globals.ui.txtNameProduct.setText(str(producto.name))
            globals.ui.txtStockProduct.setText(str(producto.stock))
            globals.ui.cmbFamilyProduct.setCurrentText(str(producto.family))
            globals.ui.txtUnitPrice.setText(str(producto.unit_price))

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
                # modifProduct = [globals.ui.txtNameProduct.text(), globals.ui.txtStockProduct.text(),
                #            globals.ui.cmbFamilyProduct.currentText(), globals.ui.txtUnitPrice.text()
                #            ]


                id = int(ProductService.get_by_name(globals.ui.txtNameProduct.text()).id)
                product = ProductService.update(
                    product_id = id,
                    name = globals.ui.txtNameProduct.text(),
                    stock = globals.ui.txtStockProduct.text(),
                    family = globals.ui.cmbFamilyProduct.currentText(),
                    unit_price = globals.ui.txtUnitPrice.text()
                )

                if product is not None:
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

                producto = ProductService.get_by_name(name)

                deleted = ProductService.delete(int(producto.id))

                if deleted is not None:
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