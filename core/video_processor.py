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

"""Обработка видео (циклы, синхронизация)"""

import subprocess
import os
import math
from core.utils import get_accurate_duration
from config.settings import QUALITY_SETTINGS


class VideoProcessor:
    """Класс для обработки видео"""

    @staticmethod
    def find_exact_loop_duration(video_path, temp_dir):
        """Определяет ТОЧНУЮ длительность одного цикла после конкатенации"""
        test_loops = 2
        test_output = os.path.join(temp_dir, 'test_loop.mp4')
        concat_file = os.path.join(temp_dir, 'test_concat.txt')

        with open(concat_file, 'w', encoding='utf-8') as f:
            for i in range(test_loops):
                f.write(f"file '{os.path.abspath(video_path)}'\n")

        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-fflags', '+genpts',
            '-vsync', 'cfr',
            '-avoid_negative_ts', 'make_zero',
            '-y', test_output
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            two_loops_duration = get_accurate_duration(test_output)
            if two_loops_duration > 0:
                return two_loops_duration / test_loops
        except Exception as e:
            pass

        return get_accurate_duration(video_path)

    @staticmethod
    def find_optimal_loop_count(audio_duration, video_duration, enable_loop_detection=True):
        """Находит оптимальное количество циклов видео"""
        if not enable_loop_detection:
            return math.ceil(audio_duration / video_duration)

        base_loops = math.ceil(audio_duration / video_duration)
        best_loops = base_loops
        best_diff = abs(audio_duration - (base_loops * video_duration))

        for delta in [-3, -2, -1, 1, 2, 3]:
            test_loops = base_loops + delta
            if test_loops > 0:
                test_diff = abs(audio_duration - (test_loops * video_duration))
                if test_diff < best_diff:
                    best_diff = test_diff
                    best_loops = test_loops

        return best_loops

    @staticmethod
    def create_looped_video_concat(video_path, loops, output_path, temp_dir):
        """Создает зацикленное видео методом конкатенации"""
        concat_file = os.path.join(temp_dir, 'concat.txt')
        with open(concat_file, 'w', encoding='utf-8') as f:
            for i in range(loops):
                f.write(f"file '{os.path.abspath(video_path)}'\n")

        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-fflags', '+genpts',
            '-vsync', 'cfr',
            '-avoid_negative_ts', 'make_zero',
            '-y', output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def sync_video_audio_method1(looped_video_path, audio_path, output_path):
        """Синхронизация видео и аудио. Метод 1"""
        looped_duration = get_accurate_duration(looped_video_path)
        audio_duration = get_accurate_duration(audio_path)

        if abs(looped_duration - audio_duration) < 0.01:
            cmd = [
                'ffmpeg', '-i', looped_video_path,
                '-i', audio_path,
                '-c', 'copy',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                '-avoid_negative_ts', 'make_zero',
                '-y', output_path
            ]
        elif looped_duration > audio_duration:
            cmd = [
                'ffmpeg', '-i', looped_video_path,
                '-i', audio_path,
                '-c', 'copy',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-t', str(audio_duration),
                '-avoid_negative_ts', 'make_zero',
                '-y', output_path
            ]
        else:
            cmd = [
                'ffmpeg', '-i', looped_video_path,
                '-i', audio_path,
                '-c', 'copy',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-t', str(looped_duration),
                '-avoid_negative_ts', 'make_zero',
                '-y', output_path
            ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def sync_video_audio_method2(looped_video_path, audio_path, output_path):
        """Синхронизация видео и аудио. Метод 2"""
        looped_duration = get_accurate_duration(looped_video_path)
        audio_duration = get_accurate_duration(audio_path)
        difference = looped_duration - audio_duration

        if abs(difference) < QUALITY_SETTINGS['PROCESSING']['SYNC_PRECISION']:
            cmd = [
                'ffmpeg', '-i', looped_video_path,
                '-i', audio_path,
                '-c', 'copy',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                '-movflags', '+faststart',
                '-y', output_path
            ]
        elif difference > 0:
            cmd = [
                'ffmpeg', '-i', looped_video_path,
                '-i', audio_path,
                '-c', 'copy',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-t', str(audio_duration),
                '-movflags', '+faststart',
                '-y', output_path
            ]
        else:
            cmd = [
                'ffmpeg', '-i', looped_video_path,
                '-i', audio_path,
                '-c', 'copy',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-t', str(looped_duration),
                '-movflags', '+faststart',
                '-y', output_path
            ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError:
            return False