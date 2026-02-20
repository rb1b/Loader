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

"""Настройки качества и обработки"""

QUALITY_SETTINGS = {
    'VIDEO_QUALITY': {
        'priority': ['higher', 'high', 'med'],
        'default': 'med'
    },

    'PROCESSING': {
        'ENABLE_PROGRESS': True,
        'KEEP_TEMP_FILES': False,
        'OUTPUT_FORMAT': 'mp4',
        'ENABLE_LOOP_DETECTION': True,
        'USE_CONCAT_METHOD': True,
        'SYNC_PRECISION': 0.001
    }
}

# Версия приложения
APP_VERSION = "2.0.0"
APP_NAME = "Loader"

# Настройки API
API_BASE_URL = "https://coub.com/api/v2/coubs/"
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Настройки загрузки
DOWNLOAD_CHUNK_SIZE = 8192
DOWNLOAD_TIMEOUT = 30