import sys
from PySide6.QtWidgets import QApplication
from ballsim.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("BallSim")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()