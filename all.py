import os
import time

from PyQt5 import QtWidgets, QtCore, uic

from src.window.runnable import TableRowWorker

import time

from PyQt5 import QtCore

from src.common.session import Proxies
from src.facebook import Facebook
from src.traodoisub import Traodoisub


from collections import defaultdict
from dataclasses import dataclass, field

from libs.util import format_proxies
from src.common.response import AppResponse, ResponseEnum
from src.common.session import AppSession


from dataclasses import dataclass, field

import facebook
import requests

from libs.util import get_valid_path
from src.common.response import AppResponse, ResponseEnum


@dataclass
class Facebook:
    uid: str = field(default=None, repr=True)
    token: str = field(default=None, repr=True)
    proxy_string: str = field(default=None, repr=True)

    total: int = field(default=0, repr=True, init=False)
    success: int = field(default=0, repr=True, init=False)
    failed: int = field(default=0, repr=True, init=False)

    name: str = field(default='', repr=True, init=False)
    init_success: bool = field(default=False, repr=True, init=False)
    init_message: str = field(default='', repr=True, init=False)

    def __post_init__(self) -> None:
        if not self.token:
            return
        set_token_result = self.__set_token(self.token)
        if set_token_result.status == ResponseEnum.ERROR:
            self.init_message = set_token_result.message
            return

        self.init_success = True

    def comment_post(self, url_or_path: str, comment_string: str):
        valid_path = get_valid_path(url_or_path=url_or_path)

        try:
            result = self.__graph.put_comment(valid_path, comment_string)
            self.success += 1
            return AppResponse(status=ResponseEnum.SUCCESS, message=str(result))
        except Exception as err:
            self.failed += 1
            return AppResponse(status=ResponseEnum.ERROR, message=str(err))
        finally:
            self.total += 1

    def like_post(self, url_or_path: str):
        valid_path = get_valid_path(url_or_path=url_or_path)

        try:
            result = self.__graph.put_like(valid_path)
            self.success += 1
            return AppResponse(status=ResponseEnum.SUCCESS, message=str(result))
        except Exception as err:
            self.failed += 1
            return AppResponse(status=ResponseEnum.ERROR, message=str(err))
        finally:
            self.total += 1

    def __set_token(self, facebook_token):
        session = requests.Session()
        self.__graph = facebook.GraphAPI(
            session=session,
            access_token=facebook_token,
            version=3.1)

        try:
            result = self.__graph.request('/me')
            self.name = result['name']

            return AppResponse(status=ResponseEnum.SUCCESS)
        except Exception as err:
            return AppResponse(status=ResponseEnum.ERROR, message=str(err))


@dataclass
class Traodoisub:
    # ? init
    username: str = field(default=None, repr=True, init=True)
    password: str = field(default=None, repr=True, init=True)
    proxy_string: str = field(default=None, repr=True, init=True)

    # ? Not init
    cookie: str = field(default=None, repr=True, init=False)
    token: str = field(default=None, repr=True, init=False)
    coin: int = field(default=0, repr=True, init=False)
    die_coin: int = field(default=0, repr=True, init=False)
    history: defaultdict[dict] = field(
        default_factory=lambda: defaultdict(dict), init=False)
    init_success: bool = field(default=False, repr=True, init=False)
    init_message: str = field(default='', repr=True, init=False)
    _base_url: str = field(
        default='https://traodoisub.com/api/', repr=False, init=False)

    def __post_init__(self):
        self.proxies = None
        self.headers = None

        if self.proxy_string:
            proxies = format_proxies(self.proxy_string)
        else:
            proxies = {}

        self._session: AppSession = AppSession(
            timeout=10, proxies=proxies)

        # ? get cookie
        cookie_result = self.__get_cookie(self.username, self.password)
        if cookie_result.status == ResponseEnum.ERROR:
            self.init_message = 'Lấy cookie trao đổi sub lỗi'
            return
        self.cookie = cookie_result.data
        self._session.headers.update({'cookie': self.cookie})

        # ? get token
        token_result = self.__get_token()
        if token_result.status == ResponseEnum.ERROR:
            self.init_message = 'Lấy token trao đổi sub lỗi'
            return
        self.token = token_result.data

        self.init_success = True

    def __get_cookie(self, username: str, password: str) -> AppResponse:
        url = self._base_url + 'scr/login.php'
        data = {
            'username': username,
            'password': password
        }
        try:
            result = self._session.post(
                url, data=data).cookies.get_dict()
            cookie = 'PHPSESSID=' + result["PHPSESSID"] + ';'
            return AppResponse(status=ResponseEnum.SUCCESS, data=cookie)
        except Exception as err:
            return AppResponse(status=ResponseEnum.ERROR, message=str(err))

    def __get_token(self) -> AppResponse:
        try:
            url = self._base_url + 'view/setting/load.php'

            result = self._session.get(
                url, headers=self.headers, timeout=15, proxies=self.proxies).json()

            token = result['tokentds']
            return AppResponse(status=ResponseEnum.SUCCESS, data=token)
        except Exception as err:
            return AppResponse(status=ResponseEnum.ERROR, message=str(err))

    def set_facebook(self, facebook_account) -> AppResponse:
        url = self._base_url + '?fields=run&id=' + \
            facebook_account['id'] + '&access_token=' + self.token
        try:
            result = self._session.get(url).json()
            if 'success' in result:
                return AppResponse(status=ResponseEnum.SUCCESS)

            return AppResponse(status=ResponseEnum.ERROR)
        except Exception as err:
            return AppResponse(status=ResponseEnum.ERROR, message=str(err))


class WorkerSignals(QtCore.QObject):
    # Define your custom signal
    finished = QtCore.pyqtSignal(dict)


class TableRowWorker(QtCore.QRunnable):
    def __init__(self, index: int, tds_username: str, tds_password: str, facebook_uid: str, facebook_token: str):
        super().__init__()
        self.key = None
        self.index: int = index
        self.tds_username: str = tds_username
        self.tds_password: str = tds_password
        self.facebook_uid: str = facebook_uid
        self.facebook_token: str = facebook_token
        self.proxy_string: str = ''
        self.current_coin: int = 0
        self.working_coin: int = 0
        self.current_job: int = 0
        self.status: str = ''

        self.key: float

        self.proxies: Proxies
        self.facebook: Facebook
        self.traodoisub: Traodoisub

        self.signals = WorkerSignals()

    def set_key(self, key: float):
        self.key = key

    def add_proxy(self, proxy_string: str):
        self.proxy_string = proxy_string

    def run(self):
        time.sleep(0.3)
        self._send('running', 'Start')
        # if not self.facebook:
        #     self.facebook = Facebook(
        #         uid=self.facebook_uid,
        #         token=self.facebook_token,
        #         proxy_string=self.proxy_string
        #     )

        if int(self.key) > int(time.time()):
            diff = int(self.key) - int(time.time())
            print('diff', diff)
            for i in range(diff):
                self._send('running', 'do job after: ' +
                           str(diff - i) + ' s')
                time.sleep(1)

        time.sleep(1)
        self._send('running', 'Start')
        time.sleep(2)
        self.current_job += 2
        self.current_coin += 400
        self.working_coin += 400
        self._send('running', 'Done job')

        time.sleep(1)
        self._send('countdown', 'Countdown', 30)

    def _send(self, status: str, message: str, delay_time: int = 0):
        data = {
            'status': status,
            'message': message,
            'index': self.index,
            'delay_time': delay_time,
            'key': self.key
        }
        self.status = message
        self.signals.finished.emit(data)
        pass


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self._proxy_data = []
        self.start_all_btn = None
        self.import_proxy_btn = None
        self.import_facebook_btn = None
        self.facebook_table = None

        # ? Index
        # self.__username_index = 0
        # self.__password_index = 1
        # self.__facebook_id_index = 2
        # self.__facebook_token_index = 3
        # self.__proxy_index = 4
        # self.__status_index = 5
        # self.__action_index = 6

        # ? Load ui
        ui_path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(ui_path, "../../ui/main.ui")
        uic.loadUi(path, self)
        self.setWindowTitle('Tool Trao doi sub')
        self.setBaseSize(1040, 650)
        self.show()

        # ? Define Main object
        self.facebook_table: QtWidgets.QTableWidget
        self.facebook_table.setFixedSize(1000, 400)
        self.facebook_table.setColumnWidth(0, 80)
        self.facebook_table.setColumnWidth(1, 80)
        self.facebook_table.setColumnWidth(2, 80)
        self.facebook_table.setColumnWidth(3, 80)
        self.facebook_table.setColumnWidth(4, 80)
        self.facebook_table.setColumnWidth(5, 80)
        self.facebook_table.setColumnWidth(6, 80)
        self.facebook_table.setColumnWidth(7, 80)
        self.facebook_table.setColumnWidth(9, 80)

        # ? Resize headers
        header = self.facebook_table.horizontalHeader()
        header.setSectionResizeMode(
            8, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            8, QtWidgets.QHeaderView.Stretch)

        # ? Config button
        self.import_facebook_btn: QtWidgets.QPushButton
        self.import_proxy_btn: QtWidgets.QPushButton
        self.start_all_btn: QtWidgets.QPushButton
        self.import_facebook_btn.clicked.connect(self.import_facebook)
        self.import_proxy_btn.clicked.connect(self.import_proxy)
        self.start_all_btn.clicked.connect(self._start_all)

        self.buttons = {}

        # ? Create thread pool
        self.thread_pool = QtCore.QThreadPool()
        self.max_thread = 2
        self.current_thread = 0
        # ? Table data
        self._table_data = {}

        # ? All workers: int is unix time
        self._pending_workers: dict[float, TableRowWorker] = {}
        self._running_workers: dict[float, TableRowWorker] = {}
        self._complete_workers: dict[float, TableRowWorker] = {}
        self._stopping_worker: dict[float, TableRowWorker] = {}

    def _start_all(self):
        for index in range(len(self._pending_workers.items())):
            key, worker = next(iter(self._pending_workers.items()))
            worker.set_key(key)
            self._running_workers[key] = self._pending_workers.pop(key)
            self.thread_pool.start(worker)
            self.current_thread += 1
            if self.current_thread >= self.max_thread:
                break

    def _receive_message(self, data):
        self._update_row_by_worker(self._running_workers[data['key']])
        if data['status'] == 'success':
            self._complete_workers[data['key']
                                   ] = self._running_workers.pop(data['key'])
            self._start_next_worker()

        if data['status'] == 'countdown':
            self._pending_workers[data['key'] + data['delay_time']
                                  ] = self._running_workers.pop(data['key'])
            self._start_next_worker()

        print('pending', len(self._pending_workers), 'running', len(
            self._running_workers), 'complete', len(self._complete_workers))

    def _start_next_worker(self):
        if not len(self._pending_workers) > 0:
            self.current_thread -= 1
            return

        key = min(self._pending_workers.keys())
        # Get the corresponding item
        worker = self._pending_workers[key]
        worker.set_key(key)
        self._running_workers[key] = self._pending_workers.pop(key)
        self.thread_pool.start(worker)

    def import_facebook(self):
        filename = QtWidgets.QFileDialog.getOpenFileName()
        file_path = filename[0]

        if not file_path or not os.path.exists(file_path):
            return

        # ? Count row
        with open(file_path, 'r') as files:
            row_count = sum(1 for _ in files)

        if row_count > 0:
            self.facebook_table.clearContents()
            self.facebook_table.setRowCount(row_count)
            self._table_data = {}
            self._pending_workers: dict[float, TableRowWorker] = {}
            self._running_workers: dict[float, TableRowWorker] = {}
            self._complete_workers: dict[float, TableRowWorker] = {}
            self._stopping_worker: dict[float, TableRowWorker] = {}

        with open(file_path, 'r') as files:
            try:
                for index, row in enumerate(files):
                    parts = row.split('|')
                    data = parts[:5]
                    if len(data) < 5 or not isinstance(data[0], str) or not isinstance(data[4], str):
                        self.facebook_table.setRowCount(0)
                        self.show_error('Không đúng định dạng')
                        break

                    worker = TableRowWorker(
                        index=index,
                        tds_username=parts[0],
                        tds_password=parts[1],
                        facebook_uid=parts[2],
                        facebook_token=parts[3],
                    )
                    worker.signals.finished.connect(self._receive_message)
                    worker.setAutoDelete(False)
                    self._pending_workers[int(
                        time.time()) + index / 10000] = worker
                    self._init_row_by_worker(worker=worker)
            except Exception as err:
                self.facebook_table.setRowCount(0)
                self.show_error('Không đúng định dạng')
                print('Err', str(err))

    def import_proxy(self):
        filename = QtWidgets.QFileDialog.getOpenFileName()
        file_path = filename[0]

        if not file_path or not os.path.exists(file_path):
            return

        self._proxy_data = []
        # The 'row_count' variable now contains the total number of rows in the file
        with open(file_path, 'r') as files:
            for index, row in enumerate(files):
                self._proxy_data.append(row[:-1])

        index = 0
        for key, worker in self._pending_workers.items():
            index_of_proxy = index % len(self._proxy_data)
            worker.add_proxy(self._proxy_data[index_of_proxy])
            self._update_row_by_worker(worker=worker)
            index += 1

    def _init_row_by_worker(self, worker: TableRowWorker):
        self._update_row(
            worker.index, 0, worker.tds_username)
        self._update_row(
            worker.index, 1, '************')
        self._update_row(
            worker.index, 2, worker.facebook_uid)
        self._update_row(
            worker.index, 3, '************')

    def _update_row_by_worker(self, worker: TableRowWorker):
        self._update_row(
            worker.index, 4, worker.proxy_string)
        self._update_row(
            worker.index, 5, worker.current_coin)
        self._update_row(
            worker.index, 6, worker.working_coin)
        self._update_row(
            worker.index, 7, worker.current_job)
        self._update_row(
            worker.index, 8, worker.status)

    def _update_row(self, index_row: int, index_column: int, data):
        self.facebook_table.setItem(
            index_row, index_column, QtWidgets.QTableWidgetItem(str(data)))

    def show_error(self, message):
        error_message = str(message)
        error_box = QtWidgets.QMessageBox(self)
        error_box.setIcon(QtWidgets.QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(error_message)
        error_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        error_box.exec_()
