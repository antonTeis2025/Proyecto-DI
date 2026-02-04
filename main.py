
import styles
from Products import Products
from conexion import *
from invoice import Invoice
from models.Product import ProductFamily
from venAux import *
import events
from customers import *
from reports import *
from events import *
from window import *
import globals
import sys

class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        globals.ui = Ui_MainWindow()
        globals.ui.setupUi(self)

        # Instance
        globals.vencal = Calendar()
        globals.venAbout = About()
        globals.dlgopen = FileDialogOpen()
        # self.invoice = Invoice()
        # Invoice.activeSales()


        # Eventos teclado
        self.scClean = QtGui.QShortcut(QtGui.QKeySequence("f11"), self)
        self.scClean.activated.connect(Invoice.saveSales)
        # Cargar Etilos
        self.setStyleSheet(styles.load_stylesheet())

        # Conexion
        varcli = True # Solo muestra clientes True
        Conexion.db_conexion() # Esto seguramente se puede sacar
        Customers.loadTablecli(varcli) # Refactorizao
        Invoice.loadTableFac() # todo
        Events.resizeTabInvProducts()
        Events.resizeTabCustomer(self)
        Events.resizeTabInv()

        # Functions in menu bar
        globals.ui.actionExit.triggered.connect(Events.messageExit)
        globals.ui.actionAbout.triggered.connect(Events.messageAbout)
        globals.ui.actionBackup.triggered.connect(Events.saveBackup)
        globals.ui.actionRestore_Backup.triggered.connect(Events.restoreBackup)
        globals.ui.menuExport_Data_csv.triggered.connect(Events.exportXlsCustomers) # todo
        # -- TODO
        globals.ui.actionCustomer_Report.triggered.connect(Reports.reportCustomers)
        globals.ui.actionProducts_Report.triggered.connect(Reports.reportProducts)


        # Funciones en lineEdit
        # Valida el DNI de los clientes al terminar de editar
        globals.ui.txtDnicli.editingFinished.connect(Customers.checkDni)
        # Capitaliza el nombre del cliente al terminar de editar
        globals.ui.txtNombrecli.editingFinished.connect(lambda: Customers.capitalizar(globals.ui.txtNombrecli.text(), globals.ui.txtNombrecli))
        # Capitaliza el apellido del cliente al terminar de editar
        globals.ui.txtApelcli.editingFinished.connect(lambda: Customers.capitalizar(globals.ui.txtApelcli.text(), globals.ui.txtApelcli))
        globals.ui.txtEmailcli.editingFinished.connect(lambda: Customers.checkEmail(globals.ui.txtEmailcli.text()))
        globals.ui.txtMobilecli.editingFinished.connect(lambda: Customers.checkMobile(globals.ui.txtMobilecli.text()))
        # globals.ui.txtUnitPrice.editingFinished.connect(Products.checkPrice)
        globals.ui.txtDniCustomerFac.editingFinished.connect(Invoice.checkDni)
        globals.ui.txtDniCustomerFac.setText("00000000T")
        Invoice.checkDni()

        # Function of chkHistoriccli
        # Carga los clientes a la tabla cada vez  que se cambia el chbx de historico
        globals.ui.chkHistoriccli.stateChanged.connect(Customers.historicoCli)

        # Functions comboBox
        Events.loadProvincia(self)
        # Cada vez que se selecciona una provincia, se cargan sus municicpios
        globals.ui.cmbProvincecli.currentIndexChanged.connect(events.Events.loadMunicli)



        # Funciones de botones
        globals.ui.btnFechaaltacli.clicked.connect(Events.openCalendar)
        globals.ui.btnDelcli.clicked.connect(Customers.delCustomer) # r
        globals.ui.btnSavecli.clicked.connect(Customers.saveCli) # r
        globals.ui.btnCleancli.clicked.connect(Customers.cleanCli) # r
        globals.ui.btnModycli.clicked.connect(Customers.modifCli) # r
        globals.ui.btnBuscacli.clicked.connect(Customers.buscaCli) # r
        globals.ui.btnCleanFac.clicked.connect(Invoice.cleanInv) # r
        globals.ui.btnSaveFac.clicked.connect(Invoice.saveInvoice) # r
        globals.ui.btnSaveSales.clicked.connect(Invoice.saveSales) # todo: informe facturas

        # Functions of tables
        globals.ui.tableCustomerList.clicked.connect(Customers.selectCustomer) # r
        globals.ui.tableInvoiceList.clicked.connect(Invoice.selectInvoice) # r
        globals.ui.tableInvoiceProducts.itemChanged.connect(Invoice.cellChangedSales) # todo

        #Functions
        events.Events.loadStatusBar(self)

        # Examen products
        # todo
        family = ["Foods", "Forniture", "Clothes", "Electronic"]
        globals.ui.cmbFamilyProduct.addItems(family)
        globals.ui.txtNameProduct.editingFinished.connect(lambda: Customers.capitalizar(globals.ui.txtNameProduct.text(), globals.ui.txtNameProduct))

        globals.ui.btnSaveProduct.clicked.connect(Products.saveProduct) # r
        globals.ui.btnCleaProduct.clicked.connect(Products.cleanProduct)
        globals.ui.btnModifyProduct.clicked.connect(Products.modifyProduct) # r
        globals.ui.btnDeleteProduct.clicked.connect(Products.delProduct) # r



        Products.loadTableProducts() # r
        Events.resizeTabProducts(self)
        globals.ui.tableProducts.clicked.connect(Products.selectProduct) # r

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.showMaximized()
    sys.exit(app.exec())