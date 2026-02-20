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

"""Пользовательские виджеты"""

from PyQt5.QtWidgets import (QGroupBox, QVBoxLayout, QLabel,
                             QComboBox, QCheckBox)


class SettingsGroup(QGroupBox):
    """Группа настроек загрузки"""

    def __init__(self):
        super().__init__("Настройки загрузки")
        self.init_ui()

    def init_ui(self):
        settings_layout = QVBoxLayout()

        # Метод синхронизации
        sync_label = QLabel("Метод синхронизации:")
        settings_layout.addWidget(sync_label)

        self.sync_combo = QComboBox()
        self.sync_combo.addItem("Метод 1", 1)
        self.sync_combo.addItem("Метод 2", 2)
        settings_layout.addWidget(self.sync_combo)

        # Оптимизация циклов
        self.loop_checkbox = QCheckBox("Оптимизация циклов")
        self.loop_checkbox.setChecked(True)
        settings_layout.addWidget(self.loop_checkbox)

        self.setLayout(settings_layout)

    def get_sync_method(self):
        """Возвращает выбранный метод синхронизации"""
        return self.sync_combo.currentData()

    def is_loop_detection_enabled(self):
        """Возвращает, включена ли оптимизация циклов"""
        return self.loop_checkbox.isChecked()