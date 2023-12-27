import sys
import time
from PyQt5.QtCore import Qt, QRunnable, QObject, pyqtSlot, pyqtSignal, QThreadPool
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QWidget

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)

class SeleniumWorker(QRunnable):
    def __init__(self, url):
        super(SeleniumWorker, self).__init__()
        self.url = url
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            # Initialize Selenium WebDriver (you may need to adjust the path to your WebDriver)
            driver = webdriver.Chrome()

            # Open the provided URL
            driver.get(self.url)

            # Perform some simple action (e.g., searching on Google)
            search_box = driver.find_element("name", "q")
            search_box.send_keys("PyQt5 QThreadPool example")
            search_box.send_keys(Keys.RETURN)

            # Simulate a delay (e.g., to simulate a time-consuming task)
            time.sleep(5)

            # Emit the result signal
            self.signals.result.emit(f"Task completed for {self.url}")

        except Exception as e:
            # Emit the error signal if an exception occurs
            self.signals.error.emit((type(e), e.args))

        finally:
            # Close the WebDriver
            driver.quit()

            # Emit the finished signal
            self.signals.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.central_widget = QLabel("Click the button to start tasks.")
        self.central_widget.setAlignment(Qt.AlignCenter)

        self.start_button = QPushButton("Start Tasks")
        self.start_button.clicked.connect(self.start_tasks)

        layout = QVBoxLayout()
        layout.addWidget(self.central_widget)
        layout.addWidget(self.start_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def start_tasks(self):
        urls = ["https://www.google.com", "https://www.yahoo.com", "https://www.bing.com"]

        for url in urls:
            worker = SeleniumWorker(url)
            worker.signals.result.connect(self.display_result)
            worker.signals.error.connect(self.display_error)

            # Execute the worker in the thread pool
            self.threadpool.start(worker)

    def display_result(self, result):
        current_text = self.central_widget.text()
        self.central_widget.setText(f"{current_text}\n{result}")

    def display_error(self, error):
        current_text = self.central_widget.text()
        self.central_widget.setText(f"{current_text}\nError: {error}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())