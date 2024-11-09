import threading
import time
import logging
import random
import json

from datetime import datetime, timedelta

import logger_setup

from work import work_profile


def load_profiles(file_path="profiles.json"):
    with open(file_path, "r") as f:
        data = json.load(f)
    # Преобразуем значения last_paint и last_claim в объекты datetime
    for profile_id in data:
        data[profile_id]["last_paint"] = datetime.fromisoformat(
            data[profile_id]["last_paint"]
        )
        data[profile_id]["last_claim"] = datetime.fromisoformat(
            data[profile_id]["last_claim"]
        )
    return data


# Сохранение обновленных данных об аккаунтах в JSON файл
def save_profiles(data, file_path="profiles.json"):
    # Преобразуем значения last_paint и last_claim обратно в строки
    for profile_id in data:
        data[profile_id]["last_paint"] = data[profile_id]["last_paint"].strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        data[profile_id]["last_claim"] = data[profile_id]["last_claim"].strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def calculate_day_profit():
    start_profiles = load_profiles("start_profiles.json")
    profiles = load_profiles("profiles.json")
    profit = {}
    for id in profiles:
        profit[id] = {}
        profit[id]["balance"] = f"{start_profiles[id]["balance"]} -> {profiles[id]["balance"]} (+{start_profiles[id]["balance"] - profiles[id]["balance"]})"
        if profiles[id]["is_max"] != start_profiles[id]["is_max"]:
            profit[id]["is_max"] = f"{start_profiles[id]["is_max"]} -> {profiles[id]["is_max"]}"
    
    with open("profit.json", "w") as f:
        json.dump(profit, f, indent=4)


# Функция для запуска задач в потоках с использованием семафора
def run_work_in_threads(works, profiles):
    threads = []
    for profile_id in works:
        thread = threading.Thread(target=work_profile, args=(profile_id, profiles))
        threads.append(thread)
        thread.start()

    # Ждем завершения всех потоков
    for thread in threads:
        thread.join()


# Проверка и выполнение задач по расписанию
def check_and_run_work(profiles, start=False):
    work_to_run = []
    now = datetime.now()
    for profile_id, data in profiles.items():
        if start:  # Случайный отбор для первого запуска за день
            if random.randint(0, 1):
                continue

        if now - data["last_paint"] >= timedelta(hours=random.uniform(1.5, 2.2)):
            work_to_run.append(profile_id)

    random.shuffle(work_to_run)
    run_work_in_threads(work_to_run, profiles)


def main():
    is_started = True
    logging.info("Script is started")
    while True:
        current_hour = datetime.now().hour
        if 10 <= current_hour <= 15:
            is_started = False
            calculate_day_profit()
            logging.info("Night - Script is paused")
            time.sleep(random.randint(21600, 23000))

        else:
            profiles = load_profiles()

            if not is_started:
                save_profiles(profiles, "start_profiles.json")
                logging.info("Morning - Script is unpaused")
                check_and_run_work(
                    profiles, start=True
                )  # Проверяем и запускаем задачи для аккаунтов, если время истекло
                save_profiles(profiles)
                is_started = True
                time.sleep(2400)

            else:
                check_and_run_work(
                    profiles
                )  # Проверяем и запускаем задачи для аккаунтов, если время истекло
                save_profiles(profiles)
                time.sleep(600)


if __name__ == "__main__":
    main()
