import os
from PyQt6 import QtSql, QtWidgets
import globals
from globals import mboxStyleSheet

class Conexion:
    """
    Clase para manejar la conexión y operaciones sobre la base de datos SQLite
    de clientes, productos y facturación mediante PyQt6.
    """

    def db_conexion(self=None):
        """
        Establece la conexión con la base de datos SQLite y verifica su validez.

        :return: True si la conexión es correcta y la base de datos es válida, False en caso contrario.
        :rtype: bool
        """
        # 🔐 Carpeta escribible del usuario
        appdata = os.getenv("APPDATA")
        ruta_dir = os.path.join(appdata, "SuperTeis")
        os.makedirs(ruta_dir, exist_ok=True)

        # 🗄️ Ruta FINAL de la base de datos
        ruta_db = os.path.join(ruta_dir, "bbdd.sqlite")

        if not os.path.isfile(ruta_db):
            import shutil
            origen = os.path.join(os.path.dirname(__file__), "data", "bbdd.sqlite")
            shutil.copy(origen, ruta_db)

        if not os.path.isfile(ruta_db):
            QtWidgets.QMessageBox.critical(None, 'Error', 'El archivo de la base de datos no existe.',
                                           QtWidgets.QMessageBox.StandardButton.Cancel)
            return False
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName(ruta_db)

        if db.open():
            query = QtSql.QSqlQuery()
            query.exec("SELECT name FROM sqlite_master WHERE type='table';")

            if not query.next():
                QtWidgets.QMessageBox.critical(None, 'Error', 'Base de datos vacía o no válida.',
                                               QtWidgets.QMessageBox.StandardButton.Cancel)
                return False
            else:
                mbox = QtWidgets.QMessageBox()
                mbox.setWindowTitle("Information")
                mbox.setIcon(QtWidgets.QMessageBox.Icon.Information)
                mbox.setText('Conexión Base de Datos realizada')
                mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                mbox.setStyleSheet(mboxStyleSheet)
                mbox.exec()
                return True
        else:
            QtWidgets.QMessageBox.critical(None, 'Error', 'No se pudo abrir la base de datos.',
                                           QtWidgets.QMessageBox.StandardButton.Cancel)
            return False

    def listProv(self=None):
        """
        Lista todas las provincias existentes en la base de datos.

        :return: Lista de nombres de provincias.
        :rtype: list[str]
        """
        listProv = []
        query = QtSql.QSqlQuery()
        query.exec("SELECT * FROM provincias;")
        if query.exec():
            while query.next():
                listProv.append(query.value(1))
        return listProv

    @staticmethod
    def listMuniProv(provincia):
        """
        Obtiene los municipios correspondientes a una provincia dada.

        :param provincia: Nombre de la provincia.
        :type provincia: str
        :return: Lista de nombres de municipios pertenecientes a la provincia.
        :rtype: list[str]
        """
        try:
            listMunicipios = []
            query = QtSql.QSqlQuery()
            query.prepare(
                "SELECT * FROM municipios WHERE idprov = (SELECT idprov FROM provincias WHERE provincia = :provincia)")
            query.bindValue(":provincia", provincia)
            if query.exec():
                while query.next():
                    listMunicipios.append(query.value(1))
            return listMunicipios
        except Exception as e:
            print("error en listMunicipios", e)

    @staticmethod
    def listCustomers(var):
        """
        Lista todos los clientes o solo los históricos según el parámetro.

        :param var: True para listar solo clientes históricos, False para todos.
        :type var: bool
        :return: Lista de clientes, cada cliente es una lista de sus campos.
        :rtype: list[list]
        """
        listCustomers = []
        query = QtSql.QSqlQuery()
        if var:
            query.prepare("SELECT * FROM customers WHERE historical = :true ORDER BY surname;")
            query.bindValue(":true", "True")
        else:
            query.prepare("SELECT * FROM customers ORDER BY surname;")
        if query.exec():
            while query.next():
                row = [query.value(i) for i in range(query.record().count())]
                listCustomers.append(row)
        return listCustomers

    @staticmethod
    def dataOneCustomer(dato):
        """
        Obtiene los datos de un cliente a partir de su móvil o DNI/NIE.

        :param dato: Número de móvil o DNI/NIE del cliente.
        :type dato: str
        :return: Lista con los datos del cliente, vacía si no se encuentra.
        :rtype: list
        """
        try:
            result = []
            query = QtSql.QSqlQuery()
            query.prepare("SELECT * FROM customers WHERE mobile = :dato")
            query.bindValue(":dato", dato)
            if query.exec():
                while query.next():
                    for i in range(query.record().count()):
                        result.append(query.value(i))
            if len(result) == 0:
                query = QtSql.QSqlQuery()
                query.prepare("SELECT * FROM customers WHERE dni_nie = :dato")
                query.bindValue(":dato", dato)
                if query.exec():
                    while query.next():
                        for i in range(query.record().count()):
                            result.append(query.value(i))
            return result
        except Exception as e:
            print("error en dataOneCustomer", e)

    @staticmethod
    def delCli(dni):
        """
        Marca un cliente como no histórico (eliminación lógica).

        :param dni: DNI/NIE del cliente.
        :type dni: str
        :return: True si la operación fue exitosa, False en caso contrario.
        :rtype: bool
        """
        try:
            query = QtSql.QSqlQuery()
            query.prepare("UPDATE customers SET historical = :false WHERE dni_nie = :dni")
            query.bindValue(":dni", dni)
            query.bindValue(":false", "False")
            return query.exec()
        except Exception as e:
            print("error en delCli", e)
            return False

    @staticmethod
    def addCli(newcli):
        """
        Agrega un nuevo cliente a la base de datos.

        :param newcli: Lista con los datos del cliente en el siguiente orden:
                       [dni_nie, adddata, surname, name, mail, mobile, address, province, city, invoicetype]
        :type newcli: list
        :return: True si la operación fue exitosa, False en caso contrario.
        :rtype: bool
        """
        try:
            query = QtSql.QSqlQuery()
            query.prepare(
                "INSERT INTO customers (dni_nie, adddata, surname, name, mail, mobile, address, province, city, invoicetype, historical) "
                "VALUES (:dnicli, :adddata, :surname, :name, :mail, :mobile, :address, :province, :city, :invoicetype, :historical)")
            query.bindValue(":dnicli", str(newcli[0]))
            query.bindValue(":adddata", str(newcli[1]))
            query.bindValue(":surname", str(newcli[2]))
            query.bindValue(":name", str(newcli[3]))
            query.bindValue(":mail", str(newcli[4]))
            query.bindValue(":mobile", str(newcli[5]))
            query.bindValue(":address", str(newcli[6]))
            query.bindValue(":province", str(newcli[7]))
            query.bindValue(":city", str(newcli[8]))
            query.bindValue(":invoicetype", str(newcli[9]))
            query.bindValue(":historical", str(True))
            return query.exec()
        except Exception as e:
            print("error addCli", e)
            return False

    @staticmethod
    def modifCli(dni, modifCli):
        """
        Modifica los datos de un cliente existente.

        :param dni: DNI/NIE del cliente a modificar.
        :type dni: str
        :param modifCli: Lista con los nuevos datos del cliente en el siguiente orden:
                         [adddata, surname, name, mail, mobile, address, province, city, historical, invoicetype]
        :type modifCli: list
        :return: True si la operación fue exitosa, False en caso contrario.
        :rtype: bool
        """
        try:
            query = QtSql.QSqlQuery()
            query.prepare(
                "UPDATE customers SET adddata = :adddata, surname = :surname, name = :name, mail = :mail, "
                "mobile = :mobile, address = :address, province = :province, city = :city, "
                "invoicetype = :invoicetype, historical = :historical WHERE dni_nie = :dni")
            query.bindValue(":dni", dni)
            query.bindValue(":adddata", str(modifCli[0]))
            query.bindValue(":surname", str(modifCli[1]))
            query.bindValue(":name", str(modifCli[2]))
            query.bindValue(":mail", str(modifCli[3]))
            query.bindValue(":mobile", str(modifCli[4]))
            query.bindValue(":address", str(modifCli[5]))
            query.bindValue(":province", str(modifCli[6]))
            query.bindValue(":city", str(modifCli[7]))
            query.bindValue(":invoicetype", str(modifCli[9]))
            query.bindValue(":historical", str(modifCli[8]))
            return query.exec()
        except Exception as e:
            print("error modifyCli", e)
            return False

    @staticmethod
    def addProduct(newProduct):
        """
        Agrega un nuevo producto a la base de datos.

        :param newProduct: Lista con los datos del producto en el siguiente orden:
                           [name, family, stock, unitPrice]
        :type newProduct: list
        :return: True si la operación fue exitosa, False en caso contrario.
        :rtype: bool
        """
        try:
            query = QtSql.QSqlQuery()
            query.prepare(
                "INSERT INTO products (name, stock, family, unitPrice) VALUES (:name, :stock, :family, :unitPrice)")
            query.bindValue(":name", str(newProduct[0]))
            query.bindValue(":stock", str(newProduct[2]))
            query.bindValue(":family", str(newProduct[1]))
            query.bindValue(":unitPrice", str(newProduct[3]))
            return query.exec()
        except Exception as e:
            print("error addProduct", e)
            return False

    @staticmethod
    def listProducts():
        """
        Lista todos los productos existentes en la base de datos.

        :return: Lista de productos, cada producto es una lista de sus campos.
        :rtype: list[list]
        """
        products = []
        query = QtSql.QSqlQuery()
        query.exec("SELECT * FROM products;")
        if query.exec():
            while query.next():
                row = [query.value(i) for i in range(query.record().count())]
                products.append(row)
        return products

    @staticmethod
    def dataOneProduct(name):
        """
        Obtiene los datos de un producto por su nombre.

        :param name: Nombre del producto.
        :type name: str
        :return: Lista con los datos del producto, vacía si no se encuentra.
        :rtype: list
        """
        try:
            result = []
            query = QtSql.QSqlQuery()
            query.prepare("SELECT * FROM products WHERE name = :dato")
            query.bindValue(":dato", name)
            if query.exec():
                while query.next():
                    for i in range(query.record().count()):
                        result.append(query.value(i))
            return result
        except Exception as e:
            print("error en dataOneProduct", e)
            return []

    @staticmethod
    def modifyProduct(modifProduct):
        """
        Modifica los datos de un producto existente.

        :param modifProduct: Lista con los datos del producto en el siguiente orden:
                             [name, stock, family, unitPrice]
        :type modifProduct: list
        :return: True si la operación fue exitosa, False en caso contrario.
        :rtype: bool
        """
        try:
            query = QtSql.QSqlQuery()
            query.prepare(
                "UPDATE products SET stock = :stock, family = :family, unitPrice = :unitPrice WHERE name = :name")
            query.bindValue(":name", str(modifProduct[0]))
            query.bindValue(":stock", str(modifProduct[1]))
            query.bindValue(":family", str(modifProduct[2]))
            query.bindValue(":unitPrice", str(modifProduct[3]))
            return query.exec()
        except Exception as e:
            print("error modifyProduct", e)
            return False

    @staticmethod
    def delProduct(name):
        """
        Elimina un producto de la base de datos.

        :param name: Nombre del producto.
        :type name: str
        :return: True si la operación fue exitosa, False en caso contrario.
        :rtype: bool
        """
        try:
            query = QtSql.QSqlQuery()
            query.prepare("DELETE FROM products WHERE name = :dato")
            query.bindValue(":dato", name)
            return query.exec()
        except Exception as e:
            print("error delProduct", e)
            return False

    # Métodos de facturación
    @staticmethod
    def buscaCli(dni):
        """
        Comprueba si existe un cliente por su DNI/NIE.

        :param dni: DNI/NIE del cliente.
        :type dni: str
        :return: True si el cliente existe, False en caso contrario.
        :rtype: bool
        """
        try:
            query = QtSql.QSqlQuery()
            query.prepare("SELECT * FROM customers WHERE dni_nie = :dato")
            query.bindValue(":dato", dni)
            if query.exec():
                return query.next()
        except Exception as e:
            print("error en buscaCli", e)
            return False

    @staticmethod
    def insertInvoice(dni, date):
        """
        Inserta una nueva factura para un cliente.

        :param dni: DNI/NIE del cliente.
        :type dni: str
        :param date: Fecha de la factura.
        :type date: str
        :return: True si la operación fue exitosa, False en caso contrario.
        :rtype: bool
        """
        try:
            query = QtSql.QSqlQuery()
            query.prepare("INSERT INTO invoices (dni_nie, date) VALUES (:dni, :date)")
            query.bindValue(":dni", dni)
            query.bindValue(":date", date)
            return query.exec()
        except Exception as e:
            print("error en insertInvoice", e)
            return False

    @staticmethod
    def allInvoice():
        """
        Obtiene todas las facturas de la base de datos.

        :return: Lista de facturas, cada factura es una lista de sus campos.
        :rtype: list[list]
        """
        try:
            records = []
            query = QtSql.QSqlQuery()
            query.prepare("SELECT * FROM invoices ORDER BY idFac DESC;")
            if query.exec():
                while query.next():
                    row = [str(query.value(i)) for i in range(query.record().count())]
                    records.append(row)
            return records
        except Exception as e:
            print("error en allInvoice", e)
            return []

    @staticmethod
    def selectProduct(item):
        """
        Obtiene un producto por su código.

        :param item: Código del producto.
        :type item: str
        :return: Lista con los datos del producto, vacía si no se encuentra.
        :rtype: list
        """
        try:
            records = []
            query = QtSql.QSqlQuery()
            query.prepare("SELECT * FROM products WHERE code = :code")
            query.bindValue(":code", item)
            if query.exec():
                while query.next():
                    for i in range(query.record().count()):
                        records.append(query.value(i))
            return records
        except Exception as e:
            print("error selectProduct", e)
            return []

    @staticmethod
    def saveSales(sales):
        """
        Guarda las ventas de una factura en la base de datos.

        :param sales: Lista de ventas, cada venta contiene
                      [idFac, idProduct, productName, productPrice, amount, totalPrice]
        :type sales: list[list]
        """
        try:
            for sale in sales:
                query = QtSql.QSqlQuery()
                query.prepare(
                    "INSERT INTO sales (idFac, idProduct, productName, productPrice, amount, totalPrice) "
                    "VALUES (:idFac, :idProduct, :productName, :productPrice, :amount, :totalPrice)")
                query.bindValue(":idFac", sale[0])
                query.bindValue(":idProduct", int(sale[1]))
                query.bindValue(":productName", sale[2])
                query.bindValue(":productPrice", float(sale[3].replace('€', '')))
                query.bindValue(":amount", int(sale[4]))
                query.bindValue(":totalPrice", float(sale[5].replace('€', '')))
                query.exec()
        except Exception as e:
            print("error en saveSales", e)

    @staticmethod
    def loadSalesByFac(idFac):
        """
        Carga las ventas asociadas a una factura.

        :param idFac: ID de la factura.
        :type idFac: int
        :return: Lista de ventas, cada venta es una lista de sus campos.
        :rtype: list[list]
        """
        try:
            records = []
            query = QtSql.QSqlQuery()
            query.prepare("SELECT * FROM sales WHERE idFac = :idFac;")
            query.bindValue(":idFac", idFac)
            if query.exec():
                while query.next():
                    row = [str(query.value(i)) for i in range(query.record().count())]
                    records.append(row)
            print(records)
            return records
        except Exception as e:
            print("error en loadSalesByFac", e)
            return []

    @staticmethod
    def existeFacturaSales(idFac):
        """
        Comprueba si existen ventas asociadas a una factura.

        :param idFac: ID de la factura.
        :type idFac: int
        :return: True si existen ventas para la factura, False en caso contrario.
        :rtype: bool
        """
        try:
            query = QtSql.QSqlQuery()
            query.prepare("SELECT * FROM sales WHERE idFac = :idFac")
            query.bindValue(":idFac", idFac)
            if query.exec():
                return query.next()
        except Exception as e:
            print("error en existeFacturaSales", e)
            return False
