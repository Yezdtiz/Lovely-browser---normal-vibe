import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QVBoxLayout
from PyQt5.QtGui import QFont, QIcon

class WidgetDesign(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Design Example")
        
        layout = QVBoxLayout(self)

        # 1. Button Design
        self.button = QPushButton("Click Me")
        
        # Set a property (icon)
        self.button.setIcon(QIcon('path/to/icon.png')) 
        
        # Set a property (font)
        font = QFont("Arial", 14)
        self.button.setFont(font)
        
        # Set a complex style using a stylesheet (preferred for visuals)
        self.button.setStyleSheet("background-color: orange; color: black; border: 3px solid red;")
        
        layout.addWidget(self.button)

        # 2. Line Edit Design
        self.line_edit = QLineEdit()
        
        # Set a property (placeholder text)
        self.line_edit.setPlaceholderText("Enter your username...")
        
        # Set a property (echo mode for password)
        # self.line_edit.setEchoMode(QLineEdit.Password) 
        
        # Set a style using a stylesheet
        self.line_edit.setStyleSheet("border-bottom: 1px solid gray; padding: 8px;")
        
        layout.addWidget(self.line_edit)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WidgetDesign()
    window.show()
    sys.exit(app.exec_())