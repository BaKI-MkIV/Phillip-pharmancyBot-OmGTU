from bs4 import BeautifulSoup
import requests

login_url = 'https://www.omgtu.ru/ecab/'
session = requests.Session()

login_data = {
    'username': 'Konstantin_Barsukov_8293',
    'password': '4aece897'
}

# Отправка POST-запроса для авторизации
response = requests.post(login_url, data=login_data, verify=False)

# Проверка успешности авторизации
if response.status_code == 200:
    print("Авторизация прошла успешно!")
    response = session.get('https://up.omgtu.ru/index.php?r=student/index', verify=False)
    if response.status_code == 200:
        print(response.status_code)
        soup = BeautifulSoup(response.text, "html.parser")
        description = []
        for row in soup.find_all('tr'):
            cells = row.find_all('td', class_='info') + row.find_all('td', class_='success')
            if cells:
                descipline = cells[0].text.strip()
                description.append(descipline)

        print(description)

else:
    print("Ошибка при авторизации:", response.status_code)


#Konstantin_Barsukov_8293
#4aece897


