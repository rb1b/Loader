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

"""Работа с метаданными видео"""

import subprocess
import re
import os


class MetadataHandler:
    """Класс для работы с метаданными"""

    @staticmethod
    def add_universal_metadata(input_path, output_path, media_title, tags_list, music_data=None):
        """Добавляет универсальные метаданные, совместимые с Windows и Linux"""
        # Формируем строку тегов
        tags_str = MetadataHandler._format_tags(tags_list)

        # Формируем основной заголовок
        main_title = MetadataHandler._format_main_title(media_title, music_data)

        try:
            cmd = [
                'ffmpeg', '-i', input_path,
                '-c', 'copy',
                '-metadata', f'title={main_title[:200]}',
            ]

            if tags_str:
                cmd.extend(['-metadata', f'comment=Tags: {tags_str[:500]}'])

            cmd.extend(['-metadata', f'description=CVideo: {media_title[:200]}'])

            if music_data:
                MetadataHandler._add_music_metadata(cmd, music_data)

            cmd.extend([
                '-metadata', 'encoder=ffmpeg',
                '-movflags', '+faststart',
                '-brand', 'mp42',
                '-y', output_path
            ])

            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except Exception as e:
            return False

    @staticmethod
    def _format_tags(tags_list):
        """Форматирует список тегов в строку"""
        if not tags_list:
            return ''

        clean_tags = []
        for tag in tags_list:
            clean_tag = tag.replace('"', '').replace("'", "").strip()
            clean_tag = re.sub(r'[^\w\s\-.,:;!?()]', '', clean_tag)
            if clean_tag:
                clean_tags.append(clean_tag)

        return '; '.join(clean_tags) if clean_tags else ''

    @staticmethod
    def _format_main_title(media_title, music_data):
        """Форматирует основной заголовок"""
        if not music_data:
            return media_title

        music_title = music_data.get('title', '').strip()
        music_album = music_data.get('album_name', '').strip()

        if music_title and music_album:
            return f"{music_title}; {music_album}"
        elif music_title:
            return music_title
        elif music_album:
            return music_album

        return media_title

    @staticmethod
    def _add_music_metadata(cmd, music_data):
        """Добавляет метаданные о музыке"""
        music_title = music_data.get('title', '').strip()
        music_album = music_data.get('album_name', '').strip()
        music_artist = music_data.get('artist_title', '').strip()

        if music_title:
            cmd.extend(['-metadata', f'album={music_album[:200]}'])
        if music_artist:
            cmd.extend(['-metadata', f'artist={music_artist[:200]}'])
            cmd.extend(['-metadata', f'composer={music_artist[:200]}'])