import logging
import time
import random

from selenium.webdriver.common.by import By

import logger_setup

from claim import get_balance


def upgrade(levels, boost, price_index, boost_index, driver, profile_id, profiles):
    try:
        profile_name = profiles[profile_id]["name"]
        balance = get_balance(driver)

        price_elemnt = driver.find_elements(
            By.XPATH, "//span[contains(@class, 'price_text')]"
        )[price_index]
        price = int(price_elemnt.text)

        if price < balance:
            boost_element = driver.find_elements(
                By.XPATH, "//div[contains(@class, 'boost_item')]"
            )[boost_index]
            boost_element.click()
            time.sleep(2)

            buy_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'PX')]")
            buy_btn.click()
            time.sleep(random.uniform(2.5, 4))

            new_levels = driver.find_elements(
                By.XPATH, "//span[contains(@class, 'level_text')]"
            )
            new_levels = [int(i.text.split(" ")[0]) for i in new_levels]

            if new_levels[boost_index] == levels[boost_index] + 1:
                balance = get_balance(driver)

                profiles[profile_id]["balance"] = balance

                logging.info(
                    f"Profile {profile_name}. Upgrade of {boost} completed. Level: {levels[boost_index]} -> {new_levels[boost_index]}, Price: {price}, Balance: {balance}"
                )
                check_upgrade(driver, profile_id, profiles)

            else:
                logging.error(f"Profile {profile_name}. Error in level difference after upgrade")
                raise

        else:
            logging.info(f"Profile {profile_name}. No balance for upgrade. Price: {price}, Balance: {balance}")

            header = driver.find_element(
                By.XPATH, "//div[contains(@class, 'header_placeholder')]"
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", header)
            time.sleep(1)

            back_btn = driver.find_element(
                By.XPATH, "//span[contains(@class, 'telegram_icons _icon')]"
            )
            back_btn.click()
            time.sleep(1)

    except Exception as e:
        logging.error(f"Profile {profile_name}. Error in upgrade: {e}")
        raise


def check_upgrade(driver, profile_id, profiles):
    try:
        profile_name = profiles[profile_id]["name"]
        balance_btn = driver.find_element(By.XPATH, "//div[contains(@class, 'number')]")
        balance_btn.click()

        boosts_btn = driver.find_element(By.XPATH, "//*[text()='Boosts']")
        boosts_btn.click()
        time.sleep(1)

        levels = driver.find_elements(
            By.XPATH, "//span[contains(@class, 'level_text')]"
        )

        driver.execute_script("arguments[0].scrollIntoView(true);", levels[2])
        time.sleep(1)

        levels = [int(i.text.split(" ")[0]) for i in levels]

        if levels[2] < 7:
            upgrade(levels, "Energy Limit", -1, 2, driver, profile_id, profiles)

        elif (levels[1] <= levels[0] or levels[0] == 7) and levels[1] < 11:
            upgrade(levels, "Recharging Speed", -1, 1, driver, profile_id, profiles)

        elif levels[0] < 7:
            upgrade(levels, "Paint Reward", 0, 0, driver, profile_id, profiles)

        else:
            logging.info(f"Profile {profile_name}. All upgrades is maximum")

            profiles[profile_id]["is_max"] = True

            header = driver.find_element(
                By.XPATH, "//div[contains(@class, 'header_placeholder')]"
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", header)
            time.sleep(1)

            back_btn = driver.find_element(
                By.XPATH, "//span[contains(@class, 'telegram_icons _icon')]"
            )
            back_btn.click()
            time.sleep(1)

        return

    except Exception as e:
        logging.error(f"Profile {profile_name}. Error in check_upgrade: {e}")
        raise
