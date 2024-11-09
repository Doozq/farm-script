import logging
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from config import api_login_url, driver_path, token
import json

import logger_setup

def auth(token):
    try:
        logging.info("Starting authentication.")
        response = requests.post(
            api_login_url,
            json={"token": token},
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            logging.info("Successful login: {}".format(response.json()))
        else:
            logging.error(
                f"Authentication failed with status code: {response.status_code}, response: {response.text}"
            )
            raise ConnectionError("Failed to connect using the token.")

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed during authentication: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred during authentication: {e}")
        raise


def get_profiles_id():
    try:
        logging.info(f"Attempting to get browser profiles")

        all_profiles = []

        headers: dict = {"Authorization": f"Bearer {token}"}

        req_url = "https://anty-api.com/browser_profiles"
        response = requests.get(req_url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        response_json = response.json()

        for i in response_json["data"]:
            all_profiles.append(
                (i["id"], i["name"])
            )  # Помещаем в список, каждый профиль

        profiles = all_profiles[::-1]

        accounts = {}

        for profile in profiles:
            accounts[profile[0]] = {
                "name": profile[1],
                "balance": 0,
                "is_max": False,
                "last_paint": "2024-11-01T23:01:12",
                "last_claim": "2024-11-01T23:01:12"
            }

        with open("profiles.json", "w") as write_file:
            json.dump(accounts, write_file, indent=4)

        logging.info("Browser profiles successfully get.")

        return all_profiles

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed get profiles: {e}")
        raise

    except Exception as e:
        logging.error(f"An unexpected error occurred while getting profiles: {e}")
        raise


def get_driver(profile_id):
    try:
        logging.info(f"Attempting to start browser profile with ID: {profile_id}")
        req_url = f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1"
        response = requests.get(req_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        response_json = response.json()
        port = str(response_json["automation"]["port"])

        chrome_driver_path = Service(driver_path)
        options = webdriver.ChromeOptions()
        options.debugger_address = f"127.0.0.1:{port}"

        driver = webdriver.Chrome(service=chrome_driver_path, options=options)
        logging.info("WebDriver successfully initialized.")

        return driver

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to start browser profile: {e}")
        raise
    except KeyError as e:
        logging.error(f"Unexpected response format: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while getting the driver: {e}")
        raise


def close_profile(profile_id):
    try:
        req_url = f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/stop"
        response = requests.get(req_url)
        response_json = response.json()
        if response_json["success"]:
            logging.info("Profile closed successfully.")
        else:
            raise

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to close browser profile: {e}")
        raise
    except KeyError as e:
        logging.error(f"Unexpected response format: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while closing the profile: {e}")
        raise
