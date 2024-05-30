from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urlparse


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

    finally:
        pass


def write_classes_to_file(classes, domain_name):
    filename = f"classes_from_pages/{domain_name}_classes.txt"
    with open(filename, "w", encoding="utf-8") as file:
        for cls in sorted(classes):
            file.write(f"{cls}\n")
    print(f"Classes have been written to {filename}")


def finderEApteka(page):
    blocks = page.findAll('section', class_='listing-card')
    for block in blocks:
        target = block.find('h5', class_='listing-card__title')
        if target :
            need = target.find('a')
            text = need.get_text()
            print(text)


def finderAptekaRu(page):
    blocks = page.findAll('div', class_='catalog-card')
    for block in blocks:
        target = block.find('span', class_='catalog-card__name emphasis')
        if target :
            text = target.get("title")
            print(text)
            need = block.find('a')
            link = need.get('href')
            print(f'Link : https://apteka.ru{link}', '\n')


if __name__ == "__main__":

    driver = webdriver.Edge()

    elem = 'target'
    search_bp = '/omsk/search/?q='

    aptru_way = 'https://apteka.ru' + search_bp + elem
    eapt_way = 'https://www.eapteka.ru' + search_bp + elem

    aptru = took_took(aptru_way, driver)
    eapt = took_took(eapt_way, driver)

    driver.quit()