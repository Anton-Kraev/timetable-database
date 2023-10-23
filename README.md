# timetable-database
Для того, чтобы реализовывать инструменты для работы с расписанием  СПБГУ, необходимо иметь данные с [`Timetable`](https://timetable.spbu.ru/) в структурированном виде. Данный проект представляет из себя базу данных, в которую переодически выгружаются данные с Timetable при помощи [`Timetable API`](https://timetable.spbu.ru/api/v1). Для работы с расписанием предоставляются файлы в формате `.csv` в директории CSV.Также, можно упростить работу с базой данных и получить акутальное состояние базы данных(для этого Вам понадобятся прокси из-за ограничений Timetable API).
#### Prerequisites:
1. [Download and install Python](https://www.python.org/downloads/)
   
#### Для получения акутального состояния базы данных необходимо:
1. Сделать fork этого репозитория и склонировать его.
2. Install requirements
```
pip install -r requirements.txt
```
3. Поменять файл config.py в корневой директории, установив DATABASE_URL. Пример для PostgreSQL:
```
DATABASE_URI = 'postgresql+asyncpg://<username>:<password>@localhost:<port>/<database_name>'
```
4. В файле config.py добавить proxy urls в переменную all_connectors(2-ух хватит):
```
all_connectors = ['http://login:password@IP', 'http://login:password@IP']
```
5. В файл events_proxies_urls, который представляет из себя пул прокси, добавьте proxy urls(желательно иметь 14+ url)
6. Обновить(cоздать все отношения) базу данных до актуального состояния(все миграции находятся в `migrations`)
```
alembic upgrade head
```
7. Заполнить таблицы, запустив main.py скрипт
```
python3 main.py users
python3 main.py events
```
