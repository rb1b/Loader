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

"""Поток для загрузки"""

import os
import tempfile
import shutil
from PyQt5.QtCore import QThread, pyqtSignal

from core.api import API
from core.downloader import FileDownloader
from core.video_processor import VideoProcessor
from core.metadata import MetadataHandler
from core.utils import sanitize_filename, get_accurate_duration
from config.settings import QUALITY_SETTINGS


class DownloadThread(QThread):
    """Поток для загрузки"""
    progress = pyqtSignal(str, float, int, int)  # desc, percent, downloaded, total
    status = pyqtSignal(str)
    finished = pyqtSignal(str, bool)  # result_path, success
    error = pyqtSignal(str)

    def __init__(self, media_url, sync_method, enable_loop_detection=True):
        super().__init__()
        self.media_url = media_url
        self.sync_method = sync_method  # 1 или 2
        self.enable_loop_detection = enable_loop_detection

        # Инициализация компонентов
        self.api = API()
        self.downloader = FileDownloader()
        self.processor = VideoProcessor()
        self.metadata_handler = MetadataHandler()

    def run(self):
        try:
            # self.status.emit("Начинаю обработку...")   КОМ
            result = self.download_media_high_quality()
            if result:
                self.finished.emit(result, True)
            else:
                self.finished.emit("", False)
        except Exception as e:
            self.error.emit(f"Ошибка: {str(e)}")
            self.finished.emit("", False)

    def download_media_high_quality(self):
        """Скачивает видео с максимальным качеством и точной синхронизацией"""
        temp_dir = tempfile.mkdtemp(prefix="media_")
        self.status.emit(f"Рабочая директория: {temp_dir}")

        try:
            media_id = self.api.extract_media_id(self.media_url)
            data = self.api.get_media_info(media_id)

            # Извлекаем метаданные
            metadata = self.api.extract_metadata(data)
            media_title = metadata['title']
            tags_list = metadata['tags']
            music_data = metadata['music']

            # Формируем имя файла
            output_filename = self._generate_filename(media_id, media_title, music_data)
            # self.status.emit(f"Название видео: {media_title[:100]}")   КОМ

            # Получаем URL для загрузки
            video_url, quality = self.api.get_video_urls(data)
            audio_url = self.api.get_audio_url(data)
            self.status.emit(f"Качество видео: {quality}")

            # Скачиваем файлы
            video_path = os.path.join(temp_dir, 'video.mp4')
            audio_path = os.path.join(temp_dir, 'audio.mp3')

            if not self._download_files(video_url, audio_url, video_path, audio_path):
                return None

            # Получаем длительности
            audio_duration = get_accurate_duration(audio_path)
            video_single_duration = get_accurate_duration(video_path)

            if video_single_duration == 0 or audio_duration == 0:
                self.error.emit("Не удалось определить длительность файлов")
                return None

            # Определяем точную длительность цикла
            # self.status.emit("Определение точной длительности цикла...")    КОМ
            exact_loop_duration = self.processor.find_exact_loop_duration(video_path, temp_dir)

            # Находим оптимальное количество циклов
            loops = self.processor.find_optimal_loop_count(
                audio_duration, exact_loop_duration, self.enable_loop_detection
            )
            # self.status.emit(f"Оптимальное количество циклов: {loops}")    КОМ

            # Создаем зацикленное видео
            # self.status.emit("Создание зацикленного видео...")    КОМ
            looped_video = os.path.join(temp_dir, 'looped.mp4')
            if not self.processor.create_looped_video_concat(
                    video_path, loops, looped_video, temp_dir
            ):
                self.error.emit("Ошибка создания зацикленного видео")
                return None

            # Синхронизируем видео и аудио
            # self.status.emit("Синхронизация видео и аудио...")    КОМ
            sync_video_no_meta = os.path.join(temp_dir, 'sync_no_meta.mp4')

            if not self._sync_video_audio(looped_video, audio_path, sync_video_no_meta):
                return None

            # Добавляем метаданные
            # self.status.emit("Добавление метаданных...")    КОМ
            sync_video_with_meta = os.path.join(temp_dir, 'sync_with_meta.mp4')
            self.metadata_handler.add_universal_metadata(
                sync_video_no_meta, sync_video_with_meta,
                media_title, tags_list, music_data
            )

            # Копируем результат
            final_output = os.path.join(os.getcwd(), output_filename)
            shutil.copy2(sync_video_with_meta, final_output)

            # Финальная информация
            file_size = os.path.getsize(final_output) / (1024 * 1024)
            self.status.emit(f"Файл: {output_filename}")
            # self.status.emit(f"Размер: {file_size:.1f} MB, Циклов: {loops}")   КОМ

            return final_output

        except Exception as e:
            self.error.emit(f"Ошибка обработки: {str(e)}")
            return None
        finally:
            if not QUALITY_SETTINGS['PROCESSING']['KEEP_TEMP_FILES']:
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass

    def _generate_filename(self, media_id, media_title, music_data):
        """Генерирует имя выходного файла"""
        sanitized_title = sanitize_filename(media_title)

        music_info = ""
        if music_data:
            music_title = music_data.get('title', '').strip()
            music_album = music_data.get('album_name', '').strip()

            if music_title and music_album:
                music_info = f"{music_title}; {music_album}"
            elif music_title:
                music_info = music_title
            elif music_album:
                music_info = music_album

        if music_info:
            file_title = sanitize_filename(music_info)
        else:
            file_title = sanitized_title

        if file_title:
            return f'sync{self.sync_method}_{media_id}_{file_title}.mp4'
        else:
            return f'sync{self.sync_method}_{media_id}.mp4'

    def _download_files(self, video_url, audio_url, video_path, audio_path):
        """Скачивает видео и аудио файлы"""
        self.status.emit("Загрузка видео...")
        if not self.downloader.download_file(video_url, video_path, "видео", self.progress.emit):
            self.error.emit("Ошибка загрузки видео")
            return False

        self.status.emit("Загрузка аудио...")
        if not self.downloader.download_file(audio_url, audio_path, "аудио", self.progress.emit):
            self.error.emit("Ошибка загрузки аудио")
            return False

        return True

    def _sync_video_audio(self, looped_video, audio_path, output_path):
        """Синхронизирует видео и аудио выбранным методом"""
        if self.sync_method == 1:
            if not self.processor.sync_video_audio_method1(
                    looped_video, audio_path, output_path
            ):
                self.error.emit("Ошибка синхронизации (метод 1)")
                return False
        else:
            if not self.processor.sync_video_audio_method2(
                    looped_video, audio_path, output_path
            ):
                self.error.emit("Ошибка синхронизации (метод 2)")
                return False
        return True