import logging
import time
import random

from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import logger_setup

from coordinate import convert_coords_from_pixel_to_canvas
from colors import color_from_template, color_from_screen
from claim import get_balance
from templates import templates
from config import real_colors, pupmkin_colors


def get_energy(driver):
    energy_element = driver.find_element(
        By.XPATH, "//div[contains(@class, 'placeholder')]"
    )
    energy = int(
        energy_element.get_attribute("innerHTML")
        .split("<span")[2][1:]
        .replace("</span>", "")
    )
    return energy


def get_template(driver):
    template_element = driver.find_element(
        By.XPATH, "//img[contains(@src, 'template')]"
    )
    template_key = (
        template_element.get_attribute("src").split("templates/")[1].split(".png")[0]
    )
    template = templates[template_key]
    return template


def start_paint(
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
):
    profile_name = profiles[profile_id]["name"]
    try:
        start_balance = get_balance(driver)
        template = get_template(driver)
        energy = get_energy(driver)
        colored = 0

        while energy != 0:
            x = random.randint(x_pixel_zero, x_pixel_end)
            y = random.randint(y_pixel_zero, y_pixel_end)
            template_color = color_from_template(x, y, template)
            canvas_x, canvas_y = convert_coords_from_pixel_to_canvas(
                x,
                y,
                x_canvas_zero,
                y_canvas_zero,
                x_pixel_zero,
                y_pixel_zero,
                ratio_x,
                ratio_y,
            )
            screen_color = color_from_screen(canvas_x, canvas_y, canvas)

            if template_color != screen_color and screen_color in (real_colors + pupmkin_colors):
                
                miss = not bool(random.randint(0, 49))
                
                if miss:
                    if screen_color in pupmkin_colors:
                        real_colors_except_template = [i for i in real_colors if i != template_color]
                        repaint_color = random.choice(real_colors_except_template)
                    else:
                        repaint_color = screen_color
                    
                    paint(canvas_x, canvas_y, repaint_color, driver, canvas)
                    logging.info(f"Profile {profile_name}. Miss dropped")
                
                else:
                    paint(canvas_x, canvas_y, template_color, driver, canvas)
                
                colored += 1
                time.sleep(random.uniform(1.3, 2))

            energy = get_energy(driver)

        end_balance = get_balance(driver)
        profit = end_balance - start_balance

        profiles[profile_id]["balance"] = end_balance
        profiles[profile_id]["last_paint"] = datetime.now()

        logging.info(
            f"Profile {profile_name}. Painting completed. Pixels colored: {colored}, Profit: {profit}, Balance: {end_balance}"
        )

    except Exception as e:
        logging.error(f"Profile {profile_name}. Error in start_paint: {e}")
        raise


def paint(x, y, color, driver, canvas):
    try:
        action = ActionChains(driver)
        action.move_to_element_with_offset(canvas, x, y)
        action.click()
        action.perform()

        active_color_element = driver.find_element(
            By.XPATH, "//div[contains(@class, 'active_color')]"
        )
        active_color = tuple(
            map(
                int,
                active_color_element.get_attribute("style")
                .replace("background-color: rgb(", "")[:-2]
                .split(", "),
            )
        )

        if active_color != color:
            active_color_element.click()
            opacity = "0"
            while opacity != "1":
                panel = driver.find_element(
                    By.XPATH, "//div[contains(@class, 'expandable_panel_layout')]"
                )
                opacity = panel.get_attribute("style").split(" ")[-1][:-1]
            need_color = driver.find_element(
                By.XPATH, f"//div[contains(@style, '{color}')]"
            )
            need_color.click()

        paint_btn = driver.find_element(By.XPATH, "//span[text()='Paint']")
        paint_btn.click()

        if active_color != color:
            active_color_element.click()

    except Exception as e:
        logging.error(f"Error in paint: {e}")
        raise
