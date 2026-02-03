import events
import globals
import styles
from dlgCalendar import *
from dlgAbout import *
from datetime import datetime

class Calendar(QtWidgets.QCalendarWidget):
    def __init__(self):
        super(Calendar, self).__init__()
        globals.vencal = Ui_dlgCalendar()
        globals.vencal.setupUi(self)

        day = datetime.now().day
        month = datetime.now().month
        year = datetime.now().year

        globals.vencal.Calendar.setSelectedDate(QtCore.QDate(year, month, day))
        globals.vencal.Calendar.clicked.connect(events.Events.loadData)
class About(QtWidgets.QDialog):
    def __init__(self):
        super(About, self).__init__()
        globals.venAbout = Ui_dlgAbout()
        globals.venAbout.setupUi(self)
        globals.venAbout.btnCloseAbout.clicked.connect(self.close)
        self.setStyleSheet(styles.load_stylesheet())
        #  globals.venAbaout.btnCloseAbout.clicked.connect(events.Events.closeAbout)

class FileDialogOpen(QtWidgets.QFileDialog):
    def __init__(self):
        super(FileDialogOpen, self).__init__()