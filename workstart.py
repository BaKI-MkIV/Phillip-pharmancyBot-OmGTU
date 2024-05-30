from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import logging
from dotenv import load_dotenv

# Установка уровня логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot token
load_dotenv('api.env')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CLASSES_SAVE_PATH = 'classes_from_pages'

if not os.path.exists(CLASSES_SAVE_PATH):
    os.makedirs(CLASSES_SAVE_PATH)

def took_took(url, driver):
    try:
        driver.get(url)
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")

        all_classes = set()
        for tag in soup.find_all(class_=True):
            classes = tag.get("class")
            if classes:
                for cls in classes:
                    all_classes.add(cls)

        # Получаем доменное имя из URL
        parsed_url = urlparse(url)
        domain_name = parsed_url.netloc

        # Записываем классы в файл
        write_classes_to_file(all_classes, domain_name)

        return soup  # Возвращаем объект BeautifulSoup вместо строки
    except Exception as e:
        logger.error(f"Error while processing URL {url}: {e}")
        return None

def write_classes_to_file(classes, domain_name):
    filename = os.path.join(CLASSES_SAVE_PATH, f"{domain_name}_classes.txt")
    try:
        with open(filename, "w", encoding="utf-8") as file:
            for cls in sorted(classes):
                file.write(f"{cls}\n")
        logger.info(f"Classes have been written to {filename}")
    except Exception as e:
        logger.error(f"Error while writing to file {filename}: {e}")

def finderAptekaRu(page):
    results = []
    try:
        blocks = page.findAll('div', class_='catalog-card')
        for block in blocks:
            target = block.find('span', class_='catalog-card__name emphasis')
            if target:
                text = target.get("title")
                need = block.find('a')
                link = need.get('href')
                results.append(f"Product: {text}\nLink: https://apteka.ru{link}")
    except Exception as e:
        logger.error(f"Error while finding products on page: {e}")
    return results

async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Please provide a search term.")
        return

    options = Options()
    options.add_argument('--headless')
    service = EdgeService()
    driver = webdriver.Edge(service=service, options=options)

    try:
        search_bp = '/omsk/search/?q='
        aptru_way = 'https://apteka.ru' + search_bp + query
        aptru = took_took(aptru_way, driver)
        if aptru:
            results = finderAptekaRu(aptru)
            if results:
                message = "\n\n".join(results[:8])
                if len(results) > 8:
                    message += f"\n\nМенее подходящие варианты вы можете найти на сайте аптеки по ссылке: {aptru_way}"
                await update.message.reply_text(message)
            else:
                await update.message.reply_text("No results found.")
        else:
            await update.message.reply_text("Failed to fetch the page.")
    except Exception as e:
        logger.error(f"Error during search process: {e}")
        await update.message.reply_text("An error occurred while processing your request.")
    finally:
        driver.quit()

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("find", find))

    app.run_polling()

if __name__ == "__main__":
    main()
