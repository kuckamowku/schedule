from flask import Flask
import calendar
from datetime import datetime
from tabulate import tabulate


current_month = datetime.now().month
current_year = datetime.now().year
start_month = datetime(current_year, current_month, 1).weekday()

app = Flask(__name__)

# Количество смен в каждый из дней недели
shifts_in_day = {0: 5, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 3}

# Время начала 1-ой и 2-ой смены
shifts = {
    1: "8:00 - 20:00",
    2: "10:00 - 22:00"
}


def create_schedule(year, month):
    if month == 12:
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
        "worker10": {'schedule': ['н'] * days_in_month, 'hours': 0}
    }
    last_worker = 0
    for i in range(days_in_month):
        current_weekday = datetime(year, month, i + 1).weekday()
        for j in range(shifts_in_day[current_weekday]):
            if j % 2 == 0:
                workers['worker' + str((last_worker + j) % 10 + 1)]['schedule'][i] = 1
            else:
                workers['worker' + str((last_worker + j) % 10 + 1)]['schedule'][i] = 2
            workers['worker' + str((last_worker + j) % 10 + 1)]['hours'] += 12
        last_worker += shifts_in_day[current_weekday]
    delete_shifts = []
    for key in workers:
        if workers[key]['hours'] > 144:
            for i, j in enumerate(workers[key]['schedule']):
                if j != 'н' and datetime(year, month, i + 1).weekday() not in [0, 6] and i not in delete_shifts:
                    workers[key]['hours'] -= 12
                    workers[key]['schedule'][i] = 'н'
                    delete_shifts.append(i)
                    break
    return days_in_month, workers


@app.route('/current')
def get_schedule():
    days, workers = create_schedule(current_year, current_month)
    table = [[''] + list(map(str, range(1, days + 1)))]
    for key in workers:
        table.append((key, *workers[key]['schedule']))
    headers = [calendar.month_name[current_month]] + [calendar.day_abbr[(start_month + i) % 7] for i in range(days)]
    table = tabulate(table, headers, tablefmt='grid')
    return f'<pre>{table}</pre>'


@app.route('/current/worker/<name>', methods=['GET'])
def get_schedule_worker(name):
    days, workers = create_schedule(current_year, current_month)
    if name not in workers:
        return 'Работник не найден'
    headers = [calendar.month_name[current_month]] + list(map(str, range(1, days + 1)))
    table = tabulate([(name, *workers[name]['schedule'])], headers, tablefmt='pretty')
    return f'<pre>{table}</pre>\nTotal hours: {workers[name]["hours"]}'


@app.route('/current/day/<date>', methods=['GET'])
def get_schedule_day(date):
    days, workers = create_schedule(current_year, current_month)
    date = int(date)
    if not 0 < date <= days:
        return 'Некорректная дата'
    headers = [calendar.month_name[current_month], f'{date} {calendar.day_name[(start_month + date - 1) % 7]}']
    table = []
    for key in workers:
        if workers[key]['schedule'][date - 1] != 'н':
            table.append((key, shifts[workers[key]['schedule'][date - 1]]))
    table = tabulate(table, headers, tablefmt='grid')
    return f'<pre>{table}</pre>'


@app.route('/next', methods=['GET'])
def get_next_schedule():
    days, workers = create_schedule(current_year, current_month + 1)
    table = [[''] + list(map(str, range(1, days + 1)))]
    for key in workers:
        table.append((key, *workers[key]['schedule']))
    headers = [calendar.month_name[(current_month + 1) % 12]] + [calendar.day_abbr[(start_month + i) % 7] for i in range(days)]
    table = tabulate(table, headers, tablefmt='grid')
    return f'<pre>{table}</pre>'


@app.route('/')
def hello():
    return '''<pre>Здесь вы можете узнать расписание работников.</pre>
    <pre>/current - расписание на теекцший месяц</pre>
    <pre>/current/worker/*фио сотрудника* - расписание конкректного сотрудника на текущий месяц</pre>
    <pre>/current/day/*дата* - расписание на конкретную дату текущего месяца</pre>
    <pre>/next - расписание на следующий месяц</pre>'''


if __name__ == '__main__':
    app.run(debug=True)
