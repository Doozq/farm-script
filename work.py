import time
import random
import threading
import logging


from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta

import logger_setup
import dolphin
from config import token
from coordinate import colibrate_systems
from paint import start_paint
from claim import claim, get_balance
from upgrade import check_upgrade


MAX_THREADS = 4
semaphore = threading.Semaphore(MAX_THREADS)


def work_profile(profile_id, profiles):
    with semaphore:
        profile_name = profiles[profile_id]["name"]
        try:
            
            # Авторизация и создание драйвера
            dolphin.auth(token=token)
            driver = dolphin.get_driver(profile_id=profile_id)
            driver.implicitly_wait(15)

            logging.info(f"Profile {profile_name}. Driver for initialized and authenticated.")

            # Открытие Telegram и переход в нужный чат
            driver.get("https://web.telegram.org")
            logging.info(f"Profile {profile_name}. Opened Telegram Web.")

            chat = driver.find_element(By.XPATH, "//a[@href='#7249432100']")
            chat.click()
            logging.info(f"Profile {profile_name}. Navigated to the chat.")

            # Начало взаимодействия с ботом
            start = driver.find_element(By.XPATH, "//*[text() = 'start']")
            start.click()
            logging.info(f"Profile {profile_name}. Started interaction with the bot.")

            # Переход в iframe с канвасом
            iframe = driver.find_element(By.XPATH, "//iframe")
            driver.switch_to.frame(iframe)
            logging.info(f"Profile {profile_name}. Switched to canvas iframe.")

            # Открытие шаблона
            template = driver.find_elements(
                By.XPATH, "//div[@class='_buttons_container_b4e6p_17']//button"
            )[1]
            time.sleep(3)
            template.click()
            time.sleep(2)
            template.click()
            logging.info(f"Profile {profile_name}. Template selected.")

            # Поиск элемента канваса
            canvas = driver.find_element(By.XPATH, "//canvas[@id='canvasHolder']")

            # Калибровка системы координат
            (
                x_canvas_zero,
                y_canvas_zero,
                x_pixel_zero,
                y_pixel_zero,
                x_pixel_end,
                y_pixel_end,
                ratio_x,
                ratio_y,
            ) = colibrate_systems(driver, canvas)
            logging.info(f"Profile {profile_name}. System calibrated.")

            # Запуск покраски
            start_paint(
                x_canvas_zero,
                y_canvas_zero,
                x_pixel_zero,
                y_pixel_zero,
                x_pixel_end,
                y_pixel_end,
                ratio_x,
                ratio_y,
                driver,
                canvas,
                profile_id,
                profiles,
            )

            now = datetime.now()
            if now - profiles[profile_id]["last_claim"] >= timedelta(
                hours=random.uniform(5, 8)
            ):
                claim(driver, profile_id, profiles)

            if profiles[profile_id]["is_max"] == False:
                check_upgrade(driver, profile_id, profiles)

            logging.info(f"Profile {profile_name}. Work with profile {profile_id} is completed.")

        except Exception as e:
            logging.error(f"Profile {profile_name}. An error occurred in work: {e}")
            raise

        finally:
            # Закрытие драйвера при завершении работы
            try:
                driver.quit()
                logging.info(f"Profile {profile_name}. Driver closed successfully.")
                dolphin.close_profile(profile_id)

            except Exception as e:
                logging.error(f"Profile {profile_name}. Error closing the driver: {e}")
