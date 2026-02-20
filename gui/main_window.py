# Loader
# Copyright (C) rb1b
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Главное окно приложения"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QLineEdit, QPushButton, QLabel,
                             QProgressBar, QTextEdit, QMessageBox,
                             QGroupBox, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from gui.widgets import SettingsGroup
from threads.download_thread import DownloadThread
from config.settings import APP_NAME, APP_VERSION


class LoaderWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.download_thread = None
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, 600, 500)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)

        # Заголовок
        title_label = QLabel(APP_NAME)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #4A90E2; padding: 10px;")
        main_layout.addWidget(title_label)

        # Группа настроек
        self.settings_group = SettingsGroup()
        main_layout.addWidget(self.settings_group)

        # Поле для ссылки
        url_label = QLabel("Ссылка на видео:")
        main_layout.addWidget(url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://site.com/view/<video_id>")
        self.url_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        main_layout.addWidget(self.url_input)

        # Кнопка загрузки
        self.download_btn = QPushButton("📥 Загрузить")
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.download_btn.clicked.connect(self.start_download)
        main_layout.addWidget(self.download_btn)

        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Текстовое поле для вывода информации
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        main_layout.addWidget(self.log_text)

        # Статус бар
        # self.statusBar().showMessage("Готов к работе")     КОМ

        main_layout.addStretch(1)

    def log_message(self, message):
        """Добавляет сообщение в лог"""
        self.log_text.append(message)
        QApplication.processEvents()

    def start_download(self):
        """Начинает загрузку"""
        url = self.url_input.text().strip()

        if not url or 'coub.com/view/' not in url:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректную ссылку")
            return

        # Блокируем кнопку
        self.download_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_text.clear()

        # Получаем выбранные настройки
        sync_method = self.settings_group.get_sync_method()
        enable_loop_detection = self.settings_group.is_loop_detection_enabled()

        # Создаем и запускаем поток
        self.download_thread = DownloadThread(url, sync_method, enable_loop_detection)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.status.connect(self.log_message)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.error.connect(self.show_error)
        self.download_thread.start()

    def update_progress(self, desc, percent, downloaded, total):
        """Обновляет прогресс"""
        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total / (1024 * 1024)

        self.progress_bar.setValue(int(percent))
        self.statusBar().showMessage(f"{desc}: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")

    def download_finished(self, result_path, success):
        """Завершение загрузки"""
        self.download_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success and result_path:
            self.log_message(f"✅ Загрузка завершена успешно!")
            self.log_message(f"📁 Файл сохранен: {result_path}")
            # self.statusBar().showMessage(f"Готово! Файл: {os.path.basename(result_path)}")  КОМ

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Успех")
            msg.setText(f"Успешно загружен!\n\nФайл: {os.path.basename(result_path)}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            self.log_message("❌ Загрузка не удалась")
            self.statusBar().showMessage("Ошибка загрузки")

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Ошибка")
            msg.setText("Не удалось загрузить видео. Проверьте ссылку и соединение с интернетом.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def show_error(self, error_msg):
        self.log_message(f"⚠️ Ошибка: {error_msg}")

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.terminate()
            self.download_thread.wait()
        event.accept()