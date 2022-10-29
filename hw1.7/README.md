# Чат бот с информацией о ТВ программе

В этом домашнем задании ваша цель - сдлать телеграм бота, который дает базовую информацию по ТВ передаче. 

**Вам нельзя использовать библиотеки для создания готовых телеграм ботов!** (но не запрещается посмотреть как они работают)


Используйте API телеграма.

### Ваша задача:

1. Перейдите в документацию по созданию ботов в телеграм: https://core.telegram.org/bots
2. Создайте токен для работы с ботом по инструкции в документации
3. Сделайте клиента для работы с API телеграма (документация к API: https://core.telegram.org/bots/api)
4. Реализуйте логику работы бота по следующему принципу:
   1. У пользователя доступно только одно действие: запрос информации по имени ТВ программы. То есть мы отправляем боту сообщение с названием программы и получаем в ответ информацию об этой программе. (можно использовать `parse_mode = html` для валидации html тегов в тексте описания тв программы)
   2. Если такой программы не найдено или пользователь отправил некоректное сообщение (картинку, стикер и тд.) отправлять сообщение с ошибкой.
   3. Для получения информации о тв программе используйте решение домашки 1.5 (если у вас его нет, напишите мне в телеграм (@indionapolis), я отправлю вам готовый код)
4. Мы можем считать, что у нас только один пользователь
5. Токен телеграма должен быть указан в файле `.env` под именем `TELEGRAM_TOKEN` (локальный .env вы в гит не пушите, проверяющий сделает свой файл со своим токеном)
8. Итоговый проект должен проходить тест и проверки flake8, black и MyPy


Полезные ссылки:
* https://core.telegram.org/bots/tutorial
* https://core.telegram.org/bots/features





Запуск тестов:

```
make lint
make test
```

Пример работы бота:

```
# запускаем бота
python -m main.py
```

```
# чат в телеграм
User:

Family Guy

Bot:

Name: Family Guy
Network Name: FOX
Network Country Name: United States
Summary: Family Guy follows Peter Griffin the endearingly ignorant dad, and his hilariously offbeat family of middle-class New Englanders in Quahog, RI. Lois is Peter's wife, a stay-at-home mom with no patience for her family's antics. Then there are their kids: 18-year-old Meg is an outcast at school and the Griffin family punching bag; 13-year-old Chris is a socially awkward teen who doesn't have a clue about the opposite sex; and one-year-old Stewie is a diabolically clever baby whose burgeoning sexuality is very much a work in progress. Rounding out the Griffin household is Brian the family dog and a ladies' man who is one step away from AA.
```

## Усложненный вариант 
* Сделать возможность сохранять шоу в избанное 
* Выводить список избранных шоу
* Сделать возможность удалять шоу из избанного

## Критерии оценивания 
1) Сделать клиент для API телеграма - 2 балла
2) Сделать бота, который реализует логику общения - 2 балла
3) Сделать скрипт, который запускает бота для обработки входящих сообщений - 2 балла
4) Использовать изученые методики ООП (создать логические классы, сделать релевантные методы для их работы) - 2 балла
5) Пройти проверку линтерами - 1 балл 
6) Покрыть тестами логику работы бота - 1 балл 
7) Реализовать логику избранного шоу - отдельные доп 3 балла
 
 