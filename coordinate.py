import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

import logger_setup

def colibrate_systems(driver, canvas):
    try:
        x_canvas_top, y_canvas_top, x_canvas_bot, y_canvas_bot = get_workplace(
            driver, canvas
        )
        x_pixel_top, y_pixel_top = convert_coords_from_canvas_to_pixel(
            x_canvas_top, y_canvas_top, driver, canvas
        )

        while (
            x_pixel_top
            == convert_coords_from_canvas_to_pixel(
                x_canvas_top, y_canvas_top, driver, canvas
            )[0]
        ):
            x_canvas_top += 1
        x_pixel_top += 1

        while (
            y_pixel_top
            == convert_coords_from_canvas_to_pixel(
                x_canvas_top, y_canvas_top, driver, canvas
            )[1]
        ):
            y_canvas_top += 1
        y_pixel_top += 1

        x_pixel_bot, y_pixel_bot = convert_coords_from_canvas_to_pixel(
            x_canvas_bot, y_canvas_bot, driver, canvas
        )

        while (
            x_pixel_bot
            == convert_coords_from_canvas_to_pixel(
                x_canvas_bot, y_canvas_bot, driver, canvas
            )[0]
        ):
            x_canvas_bot -= 1
        x_pixel_bot -= 1

        while (
            y_pixel_bot
            == convert_coords_from_canvas_to_pixel(
                x_canvas_bot, y_canvas_bot, driver, canvas
            )[1]
        ):
            y_canvas_bot -= 1
        y_pixel_bot -= 1

        x_ratio = (x_canvas_bot - x_canvas_top + 1) / (x_pixel_bot - x_pixel_top + 1)
        y_ratio = (y_canvas_bot - y_canvas_top + 1) / (y_pixel_bot - y_pixel_top + 1)

        return (
            x_canvas_top,
            y_canvas_top,
            x_pixel_top,
            y_pixel_top,
            x_pixel_bot,
            y_pixel_bot,
            x_ratio,
            y_ratio,
        )

    except Exception as e:
        logging.error(f"Error in colibrate_systems: {e}")
        raise


def get_workplace(driver, canvas):
    try:
        default_template = driver.find_elements(
            By.XPATH, "//div[@class='_buttons_container_b4e6p_17']//button"
        )[0]
        default_template_x, default_template_y = (
            default_template.location["x"],
            default_template.location["y"],
        )
        default_template_width, default_template_height = (
            default_template.size["width"],
            default_template.size["height"],
        )

        canvas_x, canvas_y = canvas.location["x"], canvas.location["y"]
        canvas_width, canvas_height = canvas.size["width"], canvas.size["height"]

        wp_x1 = default_template_x + default_template_width - canvas_width // 2 + 5
        wp_y1 = (
            default_template_y
            + default_template_height
            - canvas_height // 2
            - canvas_y
            + 5
        )

        canvas.click()
        time.sleep(1)

        tnt_btn = driver.find_elements(
            By.XPATH, "//button[contains(@class, 'shop_button')]"
        )[2]
        tnt_btn_y = tnt_btn.location["y"]

        zoom = driver.find_element(
            By.XPATH, "//button[contains(@class, 'button_1yvwv')]"
        )
        zoom_x = zoom.location["x"]

        wp_x2 = zoom_x - canvas_width // 2 - 5
        wp_y2 = tnt_btn_y - canvas_height // 2 - canvas_y - 10

        return wp_x1, wp_y1, wp_x2, wp_y2

    except Exception as e:
        logging.error(f"Error in get_workplace: {e}")
        raise


def convert_coords_from_canvas_to_pixel(x, y, driver, canvas):
    try:
        action = ActionChains(driver)
        action.move_to_element_with_offset(canvas, x, y)
        action.click()
        action.perform()
        time.sleep(0.2)

        element = driver.find_element(
            By.XPATH, "//div[contains(@class, 'pixel_info_text')]"
        )
        text = element.get_attribute("innerHTML")
        coords = text[: text.find("&")]
        x_pixel, y_pixel = coords.split(", ")
        return int(x_pixel), int(y_pixel)

    except Exception as e:
        logging.error(f"Error in convert_coords_from_canvas_to_pixel: {e}")
        raise


def convert_coords_from_pixel_to_canvas(
    x, y, x_canvas_zero, y_canvas_zero, x_pixel_zero, y_pixel_zero, ratio_x, ratio_y
):
    try:
        return (x - x_pixel_zero) * ratio_x + ratio_x / 2 - 1 + x_canvas_zero, (
            y - y_pixel_zero
        ) * ratio_y + ratio_x / 2 - 1 + y_canvas_zero

    except Exception as e:
        logging.error(f"Error in convert_coords_from_pixel_to_canvas: {e}")
        raise
