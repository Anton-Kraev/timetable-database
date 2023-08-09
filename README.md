# timetable-database
Для того, чтобы реализовывать инструменты для работы с расписанием  СПБГУ, необходимо иметь данные с [`timetable`](https://timetable.spbu.ru/) в структурированном виде. Данный проект представляет из себя базу данных, в которую переодически выгружаются данные с timetable. Для работы с расписанием предоставляются файлы в формате `.csv` в директории CSV. Расписание постоянно выгружается на месяц вперед(с учетом текущей недели). Также, можно упростить работу с базой данных и получить акутальное состояние базы данных с расписанием на месяц вперед(для этого Вам понадобятся прокси из-за ограничений timetable API).
#### Prerequisites:
1. [Download and install Python](https://www.python.org/downloads/)
   
#### Для получения акутального состояния базы данных необходимо:
1. Склонировать этот репозиторий
```
https://github.com/MinyazevR/timetable-database.git
```
2. Install requirements
```
pip install -r requirements.txt
```
3. Cоздать базу данных
4. Поменять файл config.py в корневой директории, установив DATABASE_URL. Пример для PostgreSQL:
```
DATABASE_URI = 'postgresql+asyncpg://<username>:<password>@localhost:<port>/<database_name>'
```
5. В файле config.py добавить proxy urls в переменную all_connectors(2-ух хватит):
```
all_connectors = ['http://login:password@IP', 'http://login:password@IP']
```
6. В файл events_proxies_urls, который представляет из себя пул прокси, добавьте proxy urls(желательно иметь 14+ url, но можно иметь и 5, увеличив при этом количество обрабатываемых запросов для каждого прокси)
7. Обновить базу данных до актуального состояния(все миграции находятся в `migrations`)
```
alembic upgrade head
```
8. Заполнить таблицы, запустив main.py (запускать с аргументом events только после users, потому что таблицы, связанные с расписанием заполняются на основе таблиц, связанных с пользователями)
```
python3 main.py users
python3 main.py events
```
