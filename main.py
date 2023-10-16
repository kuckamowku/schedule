from flask import Flask
import calendar
from datetime import datetime
from tabulate import tabulate

app = Flask(__name__)

# Количество смен в каждый из дней недели
shifts_in_day = {0: 5, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 3}

# Время начала 1-ой и 2-ой смены
shifts = {
    1: "8:00 - 20:00",
    2: "10:00 - 22:00"
}

# Функция генерирующая расписание
def create_schedule(year, month):
    if month > 12:
        month = 1
        year += 1
    days_in_month = calendar.monthrange(year, month)[-1]
    workers = {
        "worker1": {'schedule': ['н'] * days_in_month, 'hours': 0},
        "worker2": {'schedule': ['н'] * days_in_month, 'hours': 0},
        "worker3": {'schedule': ['н'] * days_in_month, 'hours': 0},
        "worker4": {'schedule': ['н'] * days_in_month, 'hours': 0},
        "worker5": {'schedule': ['н'] * days_in_month, 'hours': 0},
        "worker6": {'schedule': ['н'] * days_in_month, 'hours': 0},
        "worker7": {'schedule': ['н'] * days_in_month, 'hours': 0},
        "worker8": {'schedule': ['н'] * days_in_month, 'hours': 0},
        "worker9": {'schedule': ['н'] * days_in_month, 'hours': 0},
        "worker10": {'schedule': ['н'] * days_in_month, 'hours': 0},
        "worker11": {'schedule': ['н'] * days_in_month, 'hours': 0}
    }  # Список работников, можно добавить новых, если требуется
    last_worker = 0
    for i in range(days_in_month):
        current_weekday = datetime(year, month, i + 1).weekday()
        for j in range(shifts_in_day[current_weekday]):
            if j % 2 == 0:
                workers['worker' + str((last_worker + j) % len(workers) + 1)]['schedule'][i] = 1  # 1 - смена с 8 до 20
            else:
                workers['worker' + str((last_worker + j) % len(workers) + 1)]['schedule'][i] = 2  # 2 - смена с 10 до 22
            workers['worker' + str((last_worker + j) % len(workers) + 1)]['hours'] += 12
        last_worker += shifts_in_day[current_weekday]
    delete_shifts = []
    for key in workers:
        if workers[key]['hours'] > 144:  # Удаление смен у работника, если превышена месечяная норма часов(144ч)
            for i, j in enumerate(workers[key]['schedule']):
                if j != 'н' and datetime(year, month, i + 1).weekday() not in [0, 6] and i not in delete_shifts:
                    workers[key]['hours'] -= 12
                    workers[key]['schedule'][i] = 'н'
                    delete_shifts.append(i)
                    break
    return days_in_month, workers, month, year


@app.route('/current')  # Генерация и вывод полного расписания на текущий месяц
def get_schedule():
    days, workers, month, year = create_schedule(datetime.now().year, datetime.now().month)
    table = [(key, *workers[key]['schedule']) for key in workers]
    start_month = datetime(year, month, 1).weekday()
    headers = [calendar.month_name[month]] + [f'{j}\n{i.rjust(2)}' for i, j in zip(list(map(str, range(1, days + 1))), [calendar.day_abbr[(start_month + i) % 7] for i in range(days)])]
    table = tabulate(table, headers, tablefmt='grid')  # Чтобы данные были в читаемом виде все выводы сделаны с помощью библиотеки tabulate
    return f'''<pre>{table}</pre><pre>н - выходной</pre><pre>1 - Смена с 8 до 20</pre><pre>2 - Смена с 10 до 22</pre>'''


@app.route('/current/worker/<name>', methods=['GET'])  # Генерация и вывод расписания указанного работника на текущий месяц
def get_schedule_worker(name):
    days, workers, month, year = create_schedule(datetime.now().year, datetime.now().month)
    if name not in workers:
        return 'Работник не найден'
    start_month = datetime(year, month, 1).weekday()
    headers = [calendar.month_name[month]] + [f'{j}\n{i}' for i, j in zip(list(map(str, range(1, days + 1))), [calendar.day_abbr[(start_month + i) % 7] for i in range(days)])]
    table = tabulate([(name, *workers[name]['schedule'])], headers, tablefmt='pretty')
    return f'<pre>{table}</pre>Total hours: {workers[name]["hours"]}<pre>н - выходной</pre><pre>1 - Смена с 8 до 20</pre><pre>2 - Смена с 10 до 22</pre>'


@app.route('/current/day/<date>', methods=['GET'])  # Генерация и вывод расписания в указанный день текущего месяца
def get_schedule_day(date):
    days, workers, month, year = create_schedule(datetime.now().year, datetime.now().month)
    try:
        date = int(date)
    except:
        return 'Некорректная дата'
    if not 0 < date <= days:
        return 'Некорректная дата'
    start_month = datetime(year, month, 1).weekday()
    headers = [calendar.month_name[month], f'{date} {calendar.day_name[(start_month + date - 1) % 7]}']
    table = []
    for key in workers:
        if workers[key]['schedule'][date - 1] != 'н':
            table.append((key, shifts[workers[key]['schedule'][date - 1]]))
    table = tabulate(table, headers, tablefmt='grid')
    return f'<pre>{table}</pre>'


@app.route('/next')  # Генерация и вывод полного расписания на следующий месяц
def get_next_schedule():
    days, workers, month, year = create_schedule(datetime.now().year, datetime.now().month + 1)
    table = [(key, *workers[key]['schedule']) for key in workers]
    start_month = datetime(year, month, 1).weekday()
    headers = [calendar.month_name[month]] + [f'{j}\n{i.rjust(2)}' for i, j in zip(list(map(str, range(1, days + 1))), [calendar.day_abbr[(start_month + i) % 7] for i in range(days)])]
    table = tabulate(table, headers, tablefmt='grid')
    return f'<pre>{table}</pre><pre>н - выходной</pre><pre>1 - Смена с 8 до 20</pre><pre>2 - Смена с 10 до 22</pre>'


@app.route('/')
def hello():
    return '''<pre>Здесь вы можете узнать расписание работников.</pre>
    <pre>/current - расписание на текyщий месяц</pre>
    <pre>/current/worker/*фио сотрудника* - расписание конкректного сотрудника на текущий месяц</pre>
    <pre>/current/day/*дата* - расписание на конкретную дату текущего месяца</pre>
    <pre>/next - расписание на следующий месяц</pre>'''


if __name__ == '__main__':
    app.run(debug=True)

