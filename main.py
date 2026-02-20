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

import sys
from PyQt5.QtWidgets import QApplication

from gui.main_window import LoaderWindow
from core.utils import check_ffmpeg


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Проверка наличия ffmpeg
    if not check_ffmpeg():
        print("Ошибка: ffmpeg не найден. Установите ffmpeg и добавьте в PATH.")
        print("Скачать можно с: https://ffmpeg.org/download.html")
        sys.exit(1)

    window = LoaderWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()