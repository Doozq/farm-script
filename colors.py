import io
import logging
from PIL import Image
from templates import templates

import logger_setup

def color_from_template(x, y, template):
    try:
        start_x, start_y = template["start"]
        t_x, t_y = x - start_x, y - start_y

        # Загружаем изображение шаблона
        image = Image.open(template["path"])

        # Получаем цвет пикселя из изображения
        color = image.getpixel((t_x, t_y))

        return color[:3]

    except KeyError as e:
        logging.error(f"Template 'lufi' or its start coordinates not found: {e}")
        raise
    except FileNotFoundError as e:
        logging.error(f"Template image file not found: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred in color_from_template: {e}")
        raise


def color_from_screen(x, y, canvas):
    try:
        # Снимаем скриншот с canvas
        screen = canvas.screenshot_as_png
        image = Image.open(io.BytesIO(screen))

        # Определяем координаты пикселя на скриншоте
        s_x = x + canvas.size["width"] // 2 + 1
        s_y = y + canvas.size["height"] // 2 + 1

        # Получаем цвет пикселя на экране
        color = image.getpixel((s_x, s_y))

        return color

    except AttributeError as e:
        logging.error(f"Canvas object might be None or incorrect: {e}")
        raise
    except IOError as e:
        logging.error(f"Error while processing the screenshot: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred in color_from_screen: {e}")
        raise
