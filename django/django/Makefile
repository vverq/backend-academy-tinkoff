# сначала надо создать миграции по моделям из models.py
.PHONY: create-migrations
create-migrations:
	python manage.py makemigrations

# потом надо накатить миграции на БД
.PHONY: migrate-to-db
migrate-to-db:
	python manage.py migrate

# запуск сервера
.PHONY: run
run:
	python manage.py runserver

# создание пользователя для админки
.PHONY: super-user
super-user:
	python manage.py createsuperuser
