# FOODGRAM PROJECT - [«Продуктовый помощник»](http://www.myrecipesfoodgram.ga/).
____
[![Build Status](https://travis-ci.com/h0diush/foodgram-project-react.svg?branch=master)](https://travis-ci.com/h0diush/foodgram-project-react)



- В папке *frontend* находятся файлы, необходимые для сборки фронтенда приложения.
- В папке *infra* — заготовка инфраструктуры проекта: конфигурационный файл nginx и docker-compose.yml.
- В папке *backend* API сервис на _DRF_, _Djoser_, _Django_.
- В папке *docs* — файлы спецификации API.


## Инфраструктура

- Проект работает с СУБД PostgreSQL.
- Проект запущен на сервере в Яндекс.Облаке в трёх контейнерах: nginx, PostgreSQL и Django+Gunicorn. Контейнер с проектом обновляется на Docker Hub
- В nginx настроена раздача статики, остальные запросы переадресуются в Gunicorn.
- Данные сохраняются в volumes.
- Код соответствует PEP8.


### Для запуска проекта 
- клонировать репозиторий ```https://github.com/h0diush/foodgram-project-react.git```
- Создать файл ```.env``` в папке backend и заполнить его:
```
* DB_ENGINE=django.db.backends.postgresql_psycopg2
* DB_NAME=postgres
* POSTGRES_USER=  #имя пользователя postgres
* POSTGRES_PASSWORD=  #пароль пользователя postgres
* DB_HOST=db
* DB_PORT=5432
* EMAIL_HOST= # Имя хоста используемое для отправки электронных писем
* EMAIL_HOST_USER= #Имя пользователя используемое при подключении к SMTP серверу указанному в EMAIL_HOST. Если не указано, Django не будет выполнять авторизацию
* EMAIL_HOST_PASSWORD= #Пароль для подключения к SMTP сервера, который указан в EMAIL_HOST. Эта настройка используется вместе с EMAIL_HOST_USER для авторизации при подключении к SMTP серверу. Если эти настройки пустые, Django будет подключаться без авторизации.
* EMAIL_PORT= #Порт, используемый при подключении к SMTP серверу указанному в EMAIL_HOST.
```
- Перейти ав директорию *infra* ```cd infra/```
- ### !ВАЖНО! Для работы сервиса необходим заранее установленный Docker и docker-compose
- Запустить контейнер ```docker-compose up -d --build```

