# Booking_service
Используемые технологии: FastApi
### Техническое задание по проекту
Необходимо написать api приложение для функционирования отеля. Основные сущности
- Роли (администратор, управляющий)
- Комната (цена за ночь, количество мест, набор номеров брони)
- У комнаты может быть несколько номеров брони, каждый номер брони соответствует дате заезда и отъезда. 
Дата заезда и отъезда одного номера брони не могут быть равны, 
даты разных номеров брони одной комнаты не могут пересекаться (исключение дата отъезда и заезда ДВУХ номеров брони может быть равна)

Сценарии работы
Администратор
- Добавление менеджеров
- Задать номера в отеле (номер комнаты, количество мест, цена номера)
Менеджер и администратор
- Поиск номера (указываем даты и количество мест, возвращаем список (номер, вместительность, цена)
- Забронировать номер (указываем номер, дата заезда, дата отъезда, возвращаем номер брони)
- Получить информацию по брони (указываем номер брони, возвращаем дату заезда и дату отъезда)
- Снять бронь с номера (указываем номер брони, это действие можно совершить только за дату >3 дням до даты заезда, 
в случае успеха удаляем номер брони из системы)
- Показать даты на которые забронирована комната (указываем номер комнаты, 
