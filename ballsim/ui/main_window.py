import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Slot

class MainWindow(QMainWindow):
    """
    A unified main window for all BallSim application functionality.
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Window Setup
        self.setWindowTitle("BallSim")
        self.resize(1280, 720)
        self.setAnimated(True)
        self.setDockNestingEnabled(False)

        self.setStatusBar(self.statusBar())

        self.setup_menu_bar()
    
    def setup_menu_bar(self):
        """
        Initialize the QMenuBar and populate it with QMenus.
        """
        menu_bar = self.menuBar()

        # File Menu Setup
        file_menu = menu_bar.addMenu("&File")

        new_action = QAction("&New Scene", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.setStatusTip("Create a new Scene")
        new_action.triggered.connect(self.do_something)
        file_menu.addAction(new_action)

        open_action = QAction("&Open Scene", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setStatusTip("Open an existing .json Scene file")
        open_action.triggered.connect(self.do_something)
        file_menu.addAction(open_action)

        save_action = QAction("&Save Scene", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setStatusTip("Save the current Scene")
        save_action.triggered.connect(self.do_something)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save Scene &As", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.setStatusTip("Save the current Scene as a new .json file")
        save_as_action.triggered.connect(self.do_something)
        file_menu.addAction(save_as_action)

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.setStatusTip("Quit the application")
        quit_action.triggered.connect(self.do_something)
        file_menu.addAction(quit_action)

        # Edit Menu Setup
        edit_menu = menu_bar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.setStatusTip("Undo the last non-destructive action")
        undo_action.triggered.connect(self.do_something)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.setStatusTip("Revert the last undo action")
        redo_action.triggered.connect(self.do_something)
        edit_menu.addAction(redo_action)

        # Render Menu Setup
        render_menu = menu_bar.addMenu("&Render")

        render_action = QAction("&Render", self)
        render_action.setStatusTip("Export the current Scene as a new .mp4 file")
        render_action.triggered.connect(self.do_something)
        render_menu.addAction(render_action)

        # Help Menu Setup
        help_menu = menu_bar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.do_something)
        help_menu.addAction(about_action)

    @Slot()
    def do_something(self):
        sender = self.sender()
        action_name = sender.text() if sender else "Unknown Action"
        print(f"Action triggered: {action_name}")