import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pytube import YouTube
from youtubesearchpython import VideosSearch
from pytube.exceptions import RegexMatchError
from datetime import datetime
import logging
import codecs


# Удаление старого файла журнала, если он существует
if os.path.exists('spotyToD.log'):
    os.remove('spotyToD.log')

# Установка настроек логирования
logging.basicConfig(filename='spotyToD.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Настройка авторизации через OAuth в Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='',
                                               client_secret='',
                                               redirect_uri='http://localhost:8888/callback',
                                               scope='user-library-read'))

# Функция для подсчета уникальных треков в папке
def count_unique_tracks_in_folder(folder_path):
    """
    Подсчитывает количество уникальных треков в заданной папке.
    """
    unique_tracks = set()
    for _, _, files in os.walk(folder_path):
        for file in files:
            unique_tracks.add(file.split('.')[0])
    return len(unique_tracks)

def download_track(track_name):
    try:
        # Поиск трека на YouTube
        url = find_youtube_url_by_song_name(track_name)
        if url:
            yt = YouTube(url)
            video = yt.streams.filter(only_audio=True).first()
            # Скачивание трека в формате mp3
            video.download(output_path="D:/test", filename=f"{track_name}.mp3")
            logging.info(f"Скачивание завершено: {track_name}")
            print(f"Трек с названием {track_name} скачан.")
            return True
        else:
            logging.warning(f"Видео с названием {track_name} не найдено на YouTube.")
            print(f"Видео с названием {track_name} не найдено на YouTube.")
            return False
    except Exception as e:
        logging.error(f"Ошибка при скачивании трека {track_name}: {e}")
        print(f"Ошибка при скачивании трека {track_name}: {e}")
        return False

def find_youtube_url_by_song_name(song_name):
    try:
        # Поиск видео на YouTube по названию и автору
        videos_search = VideosSearch(song_name, limit=1)
        result = videos_search.result()
        if result['result']:
            return result['result'][0]['link']
    except Exception as e:
        logging.error(f"Ошибка при поиске видео: {e}")
        print(f"Ошибка при поиске видео: {e}")
    return None

def analyze_existing_tracks(folder_path):
    try:
        # Анализ существующих треков в папке
        existing_tracks = os.listdir(folder_path)
        logging.info(f"Анализ существующих композиций по пути {folder_path} - Найдено {len(existing_tracks)} треков:")
        for track in existing_tracks:
            logging.info(track)
        return existing_tracks
    except Exception as e:
        logging.error(f"Ошибка при анализе существующих композиций: {e}")
        print(f"Ошибка при анализе существующих композиций: {e}")
        return []

def get_all_favorite_tracks(sp, total_limit=500, batch_limit=50): #КОЛ ВО ТРЭКОВ ДЛЯ СКАЧИВАНИЯ! ИЗМЕНИТЬ ПРИ НАДОБНОСТИ!
    """
    Получает все любимые треки пользователя из Spotify.
    
    :param sp: Объект spotipy.Spotify для взаимодействия с API Spotify.
    :param total_limit: Общий предел количества треков для загрузки (по умолчанию 500).
    :param batch_limit: Предел количества треков в каждом запросе (по умолчанию 50).
    :return: Список объектов треков из Spotify.
    """
    offset = 0
    favorite_tracks = []
    while offset < total_limit:
        tracks = sp.current_user_saved_tracks(limit=batch_limit, offset=offset)
        if not tracks['items']:
            break  # Прерываем цикл, если достигли конца списка треков
        favorite_tracks.extend(tracks['items'])
        offset += batch_limit
    return favorite_tracks

def main():
    try:
        # Папка для скачивания треков
        download_folder = "D:/test"                                     # ПУТЬ ДЛЯ СКАЧИВАНИЯ ТРЭКОВ! ИЗМЕНИТЬ ЕСЛИ НУЖНО!
        # Создание папки, если она не существует
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        # Анализ существующих треков
        existing_tracks = analyze_existing_tracks(download_folder)

        # Использование функции для получения всех любимых треков
        all_favorite_tracks = get_all_favorite_tracks(sp, total_limit=800, batch_limit=50)

        # Чтение списка уже скачанных треков из файла
        downloaded_tracks_file = "downloaded_tracks.txt"
        downloaded_tracks = []
        if os.path.exists(downloaded_tracks_file):
            with codecs.open(downloaded_tracks_file, 'r', encoding='utf-8') as file:
                downloaded_tracks = file.read().splitlines()

        # Скачивание новых треков
        for item in all_favorite_tracks:  # Используем all_favorite_tracks здесь
            track_name = item['track']['name']
            artist_name = item['track']['artists'][0]['name']
            query = f"{track_name} {artist_name}"
            if query not in existing_tracks and query not in downloaded_tracks:
                if download_track(query):
                    downloaded_tracks.append(query)

        # Запись списка скачанных треков в файл
        with codecs.open(downloaded_tracks_file, 'w', encoding='utf-8') as file:
            for query in downloaded_tracks:
                file.write(query + '\n')

        logging.info(f"Скачено - {len(downloaded_tracks)} треков (всего в папке было - {len(existing_tracks)} треков)")
        print(f"Скачено - {len(downloaded_tracks)} треков (всего в папке было - {len(existing_tracks)} треков)")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()
