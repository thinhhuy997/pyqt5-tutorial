import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QMenu, QAction
from PyQt5.QtCore import Qt

class MyTableWidget(QTableWidget):
    def __init__(self):
        super().__init__()

        self.setColumnCount(3)
        self.setRowCount(5)

        for i in range(5):
            for j in range(3):
                item = QTableWidgetItem(f"Row {i+1}, Col {j+1}")
                self.setItem(i, j, item)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self, pos):
        selected_rows = set(index.row() for index in self.selectionModel().selectedRows())

        if len(selected_rows) > 0:
            # Convert the widget coordinates to global coordinates
            global_pos = self.mapToGlobal(pos)

            # Create a context menu
            context_menu = QMenu(self)

            # Add title action (disabled and with a different font)
            title_action = context_menu.addAction("Actions:")
            title_action.setEnabled(False)
            title_font = title_action.font()
            title_font.setBold(True)
            title_action.setFont(title_font)
            title_action.setEnabled(False)

            # Add actions to the context menu
            action_edit = QAction("Edit", self)
            action_delete = QAction("Delete", self)

            # Connect actions to slots (you can implement your own slots)
            action_edit.triggered.connect(lambda: self.editRows(selected_rows))
            action_delete.triggered.connect(lambda: self.deleteRows(selected_rows))

            # Add actions to the context menu
            context_menu.addAction(action_edit)
            context_menu.addAction(action_delete)

            # Show the context menu at the global position
            context_menu.exec_(global_pos)

    def editRows(self, selected_rows):
        print(f"Edit rows {', '.join(map(str, selected_rows))}")

    def deleteRows(self, selected_rows):
        print(f"Delete rows {', '.join(map(str, selected_rows))}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tableWidget = MyTableWidget()
        self.setCentralWidget(self.tableWidget)

        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle('Right-Click Example')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())