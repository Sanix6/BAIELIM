MANAGER = 'manager'
ADMINISTRATOR = 'administrator'
AGENT = 'agent'
STORE = 'store'
DRIVER = 'driver'

USER_TYPE = ((MANAGER, 'Менеджер'), (ADMINISTRATOR, 'Администратор'), (AGENT, 'Агент'), (STORE, 'Магазин'),
             (DRIVER, 'Водитель'))


MONDAY = 'monday'
TUESDAY = 'tuesday'
WEDNESDAY = 'wednesday'
THURSDAY = 'thursday'
FRIDAY = 'friday'
SATURDAY = 'saturday'
SUNDAY = 'sunday'
DAYS_OF_WEEK = ((MONDAY, 'Понедельник'), (TUESDAY, 'Вторник'), (WEDNESDAY, 'Среда'), (THURSDAY, 'Четверг'),
                (FRIDAY, 'Пятница'), (SATURDAY, 'Суббота'), (SUNDAY, 'Воскресенье'))


NEW = 'new'
ARCHIVE = 'archive'
STATUS = ((NEW, 'Новый'), (ARCHIVE, 'Архив'))

VISITED = 'visited'
STORE_STATUS = ((NEW, 'Новый'), (VISITED, 'Посещено'))
