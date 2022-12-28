# 1 Описание 
## 1.1 Общая информация 
Асинхронное учебное веб-приложение для изучения взаимодействия python, библиотек для работы с БД и веб-окружением.
Используется БД SQLite, фреймворки sqlalchemy для взаимодействия с БД, fastAPI для реализации асинхронной работы.
В БД создано 3 связанных таблицы: Товары, Магазины, Покупки с указанием id магазина и товара
Связи Магазины - Покупки  и Товары - Покупки реализованы по полям id соответствующих сущностей и являются связями "Один ко многим". 
!Все поля id являются целочисленными, это нужно учитывать при заполнении таблиц!

## 1.2 Структура таблиц БД
Ниже представлена dbml схема модели данных. Визуализировать ее можно инструментом dbdiagram.io

DBML

Table store { // магазины торговой сети (уникальные адреса)
  id integer [pk, increment]
  address varchar [unique]
}

Table item { // товарные позиции (уникальные наименования)
  id integer [pk, increment]
  name varchar [unique]
  price float
}

Table sales { // продажи
  id integer [pk, increment]
  sale_time datetime [not null, default: `now()`]
  item_id integer [ref: < item.id]
  store_id integer [ref: < store.id]
}

# 2 Подготовка к запуску
Перед запуском приложения необходимо установить библиотеки для python, перечисленные в файле requirements.txt:  
pip install -r requirements.txt  
При написании данного приложения использовалась версия Python 3.9.12, pip - 22.0.4  

# 3 Запуск и остановка приложения
Для запуска приложения необходимо в командной строке ввести команду:  
uvicorn main_dz:app  
В случае успешного запуска появится сообщение  
INFO:     Application startup complete.  
После этого сервер веб-приложения запустится по адресу и порту http://127.0.0.1:8000/
Если Uvicorn настроен на другой адрес и порт, следует использовать их сочетание в дальнейшем при написании запросов.  
Для остановки работы приложения используется сочетание клавиш Ctrl+C  
Подтверждением остановки служат сообщения  
INFO:     Application shutdown complete.
INFO:     Finished server process

# 4 Основные запросы
## 4.1 Отображение всех товарных позиций
Тип запроса: GET  
Адрес запроса: http://127.0.0.1:8000/items/  
Тело запроса/доп. информация: нет  
Формат ответа: JSON:  
{"id": <id товара>,  
"name": <Наименование товара>,  
"price": <Цена товара>}  
## 4.2 Отображение информации по всем магазинам
Тип запроса: GET  
Адрес запроса: http://127.0.0.1:8000/stores/  
Тело запроса/доп. информация: нет  
Формат ответа: JSON:  
{"id": <id магазина>,  
"address": <Адрес магазина>}  
## 4.3 Ввод данных о новой продаже
Тип запроса: POST  
Адрес запроса: http://127.0.0.1:8000/sales/  
Тело запроса/доп. информация: Text - JSON:
{"item_id": <id товара>,
"store_id": <id магазина>  }  
Формат ответа: JSON:  
{"id": <id покупки, автозаполнение>,
"sale_time": <id покупки, автозаполнение текущей даты-времени>,
"item_id": <id товара>,
"store_id": <id магазина>}
## 4.4 Отображение топ-10 самых доходных магазинов за месяц 
Тип запроса: GET  
Адрес запроса: http://127.0.0.1:8000/top10stores/  
Тело запроса/доп. информация: нет  
Формат ответа: JSON:  
{"id": <id магазина>,  
"Адрес": <Адрес магазина>,
"Суммарная выручка": <Выручка за месяц>}  
Магазины отсортированы по выручке по убыванию
## 4.5 Отображение топ-10 самых продаваемых товаров
Тип запроса: GET  
Адрес запроса: http://127.0.0.1:8000/top10items/  
Тело запроса/доп. информация: нет  
Формат ответа: JSON: 
{"id": <id товара>,
"Наименование": <Наименование товара>,
"Количество проданных товаров": <Количество проданных товаров>}
Товары отсортированы по количеству продаж по убыванию  

# 5 Дополнительные запросы
## 5.1 Ввод данных о новом товаре
Тип запроса: POST  
Адрес запроса: http://127.0.0.1:8000/items/  
Тело запроса/доп. информация: Text - JSON:
{"name": <id товара>,
"price": <Цена товара, число с плавающей точкой, разделитель десятичных знаков - точка>  }  
Формат ответа: JSON:  
{"id": <id товара, автозаполнение>,
"name": <id товара>,
"price": <Цена товара>}
## 5.2 Ввод данных о новом магазине
Тип запроса: POST  
Адрес запроса: http://127.0.0.1:8000/stores/  
Тело запроса/доп. информация: Text - JSON:
{"address": <Адрес магазина>}  
Формат ответа: JSON:  
{"id": <id магазина, автозаполнение>,  
"address": <Адрес магазина>} 

# 6 Первоначальное блоковое заполнение тестовыми данными из файла при пустой базе (для продвинутых пользователей)
## 6.1 Общая информация
В папке с проектом уже есть заполненная БД sales__.db, однако, если по каким-то причинам она отсутствует, то будет создана при запуске приложения. Есть возможность заполнить ее из excel-файла в папке проекта tables_fill.xlsx, также в нем реализованы таблицы с результатами запросов на топ-10, их результаты можно сравнить с тем, что выдает приложение 
## 6.2 Заполнение таблицы товаров
Тип запроса: POST  
Адрес запроса: http://127.0.0.1:8000/items-fillfromfile/
Тело запроса/доп. информация: нет 
Источник:
Файл в папке проекта tables_fill.xlsx, лист items (поле id не передается, назначается автоматически, начиная с 1. в файле должно быть заполнено также)
Формат ответа:
"Items filled from file"
Запрос делается единоразово, при повторном будет ошибка из-за дублирования наименований
## 6.3 Заполнение таблицы магазинов
Тип запроса: POST  
Адрес запроса: http://127.0.0.1:8000/stores-fillfromfile/
Тело запроса/доп. информация: нет 
Источник:
Файл в папке проекта tables_fill.xlsx, лист stores (поле id не передается, назначается автоматически, начиная с 1. в файле должно быть заполнено также)
Формат ответа:
"Stores filled from file"
Запрос делается единоразово, при повторном будет ошибка из-за дублирования наименований
## 6.4 Заполнение таблицы продаж
Тип запроса: POST  
Адрес запроса: http://127.0.0.1:8000/sales-fillfromfile/
Тело запроса/доп. информация: нет 
Источник:
Файл в папке проекта tables_fill.xlsx, лист sales (поле id не передается, назначается автоматически, начиная с 1. в файле должно быть заполнено также)
Формат ответа:
"Sales filled from file"
Запрос делается единоразово, при повторном будет несовпадение с файлом tables_fill.xlsx из-за дублирования продаж, но приложение не выдаст ошибку