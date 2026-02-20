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

"""Работа с API"""

import requests
import json
from config.settings import API_BASE_URL, USER_AGENT


class API:
    """Класс для работы с API"""

    def __init__(self):
        self.headers = {'User-Agent': USER_AGENT}

    def get_media_info(self, media_id):
        """Получает информацию о видео по ID"""
        api_url = f"{API_BASE_URL}{media_id}"
        response = requests.get(api_url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def extract_media_id(self, url):
        """Извлекает ID из URL"""
        return url.split('/')[-1]

    def get_video_urls(self, data):
        """Получает URL видео в максимальном качестве"""
        video_versions = data['file_versions']['html5']['video']

        from config.settings import QUALITY_SETTINGS
        priority = QUALITY_SETTINGS['VIDEO_QUALITY']['priority']

        for quality in priority:
            if quality in video_versions:
                return video_versions[quality]['url'], quality

        # Если ничего не найдено, берем 'med'
        return video_versions['med']['url'], 'med'

    def get_audio_url(self, data):
        """Получает URL аудио"""
        return data['file_versions']['html5']['audio']['high']['url']

    def extract_metadata(self, data):
        """Извлекает метаданные из данных видео"""
        media_title = data.get('title', '')
        tags = data.get('tags', [])
        tags_list = [tag['title'] for tag in tags if tag.get('title')]
        music_data = data.get('music')

        return {
            'title': media_title,
            'tags': tags_list,
            'music': music_data
        }