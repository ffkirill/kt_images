# Web-сервис для хранения изображений.

Для работы с базой данных использован асинхронный драйвер aiopg, список изображений отдается сервером
chunk'ам в поточном режиме, размер chunk'а устанавливается через настройки. Таким образом исключается
создание промежуточной структуры данных на стороне веб-приложения.

Для инициализации и обслуживания базы данных разработан механизм fixtures.

Слой представления веб-приложения написан с использованием билиотеки aihttp-pydantic, которая
использует аннотации типов для генерации JSON-схемы API стандарта OpenAPI и валидации данных.

Предполагается, что все команды выполнятся в корневой директории проекта (содержащей .git)


## Структура проекта

  - docker-composer.yml - декларация Docker-Compose
  - api - корневая директория веб-приложения
    - openapi.json - JSON - схема API
    - requirements.txt - зависимости проекта для установки через pip
    - README.md - Этот readme.
    - Dockerfile
  - data - внешнее хранилище ресурсов postgresqls


## Инициализация Postgres и работа с проектом

  Команды будут выполняться в контейнерах. На машине разработчика целесообразно использовать локальнай интерпретатор и запущенный контейнер db с postgres. Для целей разработки у контейнера Postgres открыт порт 5432 для внешнего соединения. На машине разработчика контейнер db имеет ip адрес, установленный dsn в api/src/kt_images/base_settings.py

  ### Выполняем сборку контейнеров и старт:

  `root# docker-compose build`

  `root# docker-compose up`


  ### Инициализируем БД

  Команды выполняем в контейнере веб-приложения. 
  Аналогичного результата можно добиться установив необходимые зависимости
  и используя python локально.

  - Запросим список fixtures
  
  `root# docker-compose exec -T api python3 -m kt_images.manage.load_fixtures --list_all`
  >['00_drop-tables.sql', '01_ddl.sql', '02_create-index.sql']

  - Применим все fixtures. Инициалзация начинается с drop tables

  `root# docker-compose exec -T api python3 -m kt_images.manage.load_fixtures --apply_all`
  

  ## Работа с API
  ### Получение JSON-схемы API

  `root# docker-compose exec -T api python3 -m aiohttp_pydantic.oas kt_images.wsgi:app`
  TODO: отразить amounts


  ### Получение списка изображений через curl

  `user$  curl -X GET http://localhost:8080/images`
  > [{"totalImages": 0, "totalChunks": 0}]`


  ### Загрузка изображения, поиск по тегам, просмотр

  - Загрузка метаданных

  `curl -H "Content-Type: application/json" -X POST http://localhost:8080/images --data '{"filename": "example.jpg", "tags": ["example_1", "jpeg", "canon"]}' -w %{http_code}`
  >{"image_id": 19, "filename": "example.jpg", "tags": ["example_1", "jpeg", "canon"]}
  >201


  - Поиск по тегам

  Варианты использования:
    * tag=...
    * tags_all=...&tags_all=...
    * tags_any=...&tags_any=...


  `curl -X GET http://localhost:8080/images?tag=canon -w %{http_code}`
  >[[{"image_id": 1, "filename": "example.jpg", "tags": ["example_1", "jpeg", "canon"]}], {"totalImages": 1, "totalChunks": 1}]
  >200
  
  `curl -X GET http://localhost:8080/images?tags_all=canon&tags_all=jpeg -w %{http_code}`
  >[[{"image_id": 1, "filename": "example.jpg", "tags": ["example_1", "jpeg", "canon"]}], {"totalImages": 1, "totalChunks": 1}]
  >200

  `curl -X GET http://localhost:8080/images?tags_any=canon&tags_any=nikon -w %{http_code}`
  >[[{"image_id": 1, "filename": "example.jpg", "tags": ["example_1", "jpeg", "canon"]}], {"totalImages": 1, "totalChunks": 1}]
  >200

  `curl -X GET http://localhost:8080/images?tag=canon2 -w %{http_code}`
  >[{"totalImages": 0, "totalChunks": 0}]
  >200
  

  - Запрос одного изображения

  `curl -X GET http://localhost:8080/images/1 -w %{http_code}`
  >[{"totalImages": 0, "totalChunks": 0}]
  >200
  >{"image_id": 1, "filename": "example.jpg", "tags": ["example_1", "jpeg", "canon"]}
  
   `curl -X GET http://localhost:8080/images/22 -w %{http_code}`
  >{"error": "Image <22> is not found"}
  >404
 
 
  - Загрузка файла изображения
  TODO: Написать поточный загрузчик через POST
  - Получение файла изображения
  TODO: Написать View с поточным response

​```
# Задание
​
## Основное

 * Создать сервис с веб-апи для сохранения изображений и тегов к ним. Сервис должен позволять получать список изображений и их тегов, фильтрацию изображений по тегам и скачивание/просмотр изображений.
 * Для хранения информации (возможно и самих изображений) использовать postgres.
​
## Дополнительное
 * Создать Dockerfile и docker-compose.yml для запуска сервиса и БД.
 * Описать методы api в readme.md проекта.
 * Создать cli утилиту для работы с веб-апи.
 ```
 
 
    
   
