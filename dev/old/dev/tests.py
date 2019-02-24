def test_scheduling():
    test_dates = [
        "05.01.2019 20:30",  # datetime.datetime.now(),
        '06 Jan 2019 13:00',
        '09 Jan 2019 17:00',
        '10 Jan 2019 09:00',
        '10 Jan 2019 12:00',
        '11 Jan 2019 09:00',
    ]
test_dates = [cast_datetime(d) for d in test_dates]
    # test_dates

    test_schedules = ['every month', 'every week', 'Every thu at 10:02', 'every sat', 'every tue, wed, thu, fri, sat',
                      'every! 1 hour', 'every sun at 10:30', 'Every wed, thu, fri, sat 12:30',
                      'every Mon, Tue, Wed, Thu, Fri at 9:40', 'every! 2 hours']
    res = dict()
    for date_string in test_schedules:
        schedule = parse_repeat_schedule(date_string)
        res[date_string] = dict(schedule=schedule)
        # print('"', date_string, '"', schedule)
        res[date_string]['appied_schedule'] = dict()
        for date in test_dates:
            date_format = "%d.%m.%Y at %H:%M"
            next_date = simple_follow_schedule(schedule, date)
            res[date_string]['appied_schedule'][date.strftime(date_format)] = next_date.strftime(date_format)
            # print(date.strftime(date_format), " next: ", next_date.strftime(date_format))

    # print(res)
    true_res = {'every month': {'schedule': {'relative': False, 'specific_time': None, 'days_of_week': None,
                                             'period': {'unit': 'months', 'value': 1}},
                                'appied_schedule': {'01.05.2019 at 20:30': '01.06.2019 at 20:30',
                                                    '06.01.2019 at 13:00': '06.02.2019 at 13:00',
                                                    '09.01.2019 at 17:00': '09.02.2019 at 17:00',
                                                    '10.01.2019 at 09:00': '10.02.2019 at 09:00',
                                                    '10.01.2019 at 12:00': '10.02.2019 at 12:00',
                                                    '11.01.2019 at 09:00': '11.02.2019 at 09:00'}}, 'every week': {
        'schedule': {'relative': False, 'specific_time': None, 'days_of_week': None,
                     'period': {'unit': 'weeks', 'value': 1}},
        'appied_schedule': {'01.05.2019 at 20:30': '08.05.2019 at 20:30', '06.01.2019 at 13:00': '13.01.2019 at 13:00',
                            '09.01.2019 at 17:00': '16.01.2019 at 17:00', '10.01.2019 at 09:00': '17.01.2019 at 09:00',
                            '10.01.2019 at 12:00': '17.01.2019 at 12:00', '11.01.2019 at 09:00': '18.01.2019 at 09:00'}},
                'Every thu at 10:02': {
                    'schedule': {'relative': False, 'specific_time': [datetime.time(10, 2)], 'days_of_week': ['thu'],
                                 'period': None}, 'appied_schedule': {'01.05.2019 at 20:30': '02.05.2019 at 10:02',
                                                                      '06.01.2019 at 13:00': '10.01.2019 at 10:02',
                                                                      '09.01.2019 at 17:00': '10.01.2019 at 10:02',
                                                                      '10.01.2019 at 09:00': '10.01.2019 at 10:02',
                                                                      '10.01.2019 at 12:00': '17.01.2019 at 10:02',
                                                                      '11.01.2019 at 09:00': '17.01.2019 at 10:02'}},
                'every sat': {
                    'schedule': {'relative': False, 'specific_time': None, 'days_of_week': ['sat'], 'period': None},
                    'appied_schedule': {'01.05.2019 at 20:30': '04.05.2019 at 20:30',
                                        '06.01.2019 at 13:00': '12.01.2019 at 13:00',
                                        '09.01.2019 at 17:00': '12.01.2019 at 17:00',
                                        '10.01.2019 at 09:00': '12.01.2019 at 09:00',
                                        '10.01.2019 at 12:00': '12.01.2019 at 12:00',
                                        '11.01.2019 at 09:00': '12.01.2019 at 09:00'}}, 'every tue, wed, thu, fri, sat': {
            'schedule': {'relative': False, 'specific_time': None, 'days_of_week': ['tue', 'wed', 'thu', 'fri', 'sat'],
                         'period': None},
            'appied_schedule': {'01.05.2019 at 20:30': '02.05.2019 at 20:30', '06.01.2019 at 13:00': '08.01.2019 at 13:00',
                                '09.01.2019 at 17:00': '10.01.2019 at 17:00', '10.01.2019 at 09:00': '11.01.2019 at 09:00',
                                '10.01.2019 at 12:00': '11.01.2019 at 12:00',
                                '11.01.2019 at 09:00': '12.01.2019 at 09:00'}}, 'every! 1 hour': {
            'schedule': {'relative': True, 'specific_time': None, 'days_of_week': None,
                         'period': {'unit': 'hours', 'value': 1}},
            'appied_schedule': {'01.05.2019 at 20:30': '01.05.2019 at 21:30', '06.01.2019 at 13:00': '06.01.2019 at 14:00',
                                '09.01.2019 at 17:00': '09.01.2019 at 18:00', '10.01.2019 at 09:00': '10.01.2019 at 10:00',
                                '10.01.2019 at 12:00': '10.01.2019 at 13:00',
                                '11.01.2019 at 09:00': '11.01.2019 at 10:00'}}, 'every sun at 10:30': {
            'schedule': {'relative': False, 'specific_time': [datetime.time(10, 30)], 'days_of_week': ['sun'],
                         'period': None},
            'appied_schedule': {'01.05.2019 at 20:30': '05.05.2019 at 10:30', '06.01.2019 at 13:00': '13.01.2019 at 10:30',
                                '09.01.2019 at 17:00': '13.01.2019 at 10:30', '10.01.2019 at 09:00': '13.01.2019 at 10:30',
                                '10.01.2019 at 12:00': '13.01.2019 at 10:30',
                                '11.01.2019 at 09:00': '13.01.2019 at 10:30'}}, 'Every wed, thu, fri, sat 12:30': {
            'schedule': {'relative': False, 'specific_time': [datetime.time(12, 30)],
                         'days_of_week': ['wed', 'thu', 'fri', 'sat'], 'period': None},
            'appied_schedule': {'01.05.2019 at 20:30': '02.05.2019 at 12:30', '06.01.2019 at 13:00': '09.01.2019 at 12:30',
                                '09.01.2019 at 17:00': '10.01.2019 at 12:30', '10.01.2019 at 09:00': '10.01.2019 at 12:30',
                                '10.01.2019 at 12:00': '10.01.2019 at 12:30',
                                '11.01.2019 at 09:00': '11.01.2019 at 12:30'}}, 'every Mon, Tue, Wed, Thu, Fri at 9:40': {
            'schedule': {'relative': False, 'specific_time': [datetime.time(9, 40)],
                         'days_of_week': ['mon', 'tue', 'wed', 'thu', 'fri'], 'period': None},
            'appied_schedule': {'01.05.2019 at 20:30': '02.05.2019 at 09:40', '06.01.2019 at 13:00': '07.01.2019 at 09:40',
                                '09.01.2019 at 17:00': '10.01.2019 at 09:40', '10.01.2019 at 09:00': '10.01.2019 at 09:40',
                                '10.01.2019 at 12:00': '11.01.2019 at 09:40',
                                '11.01.2019 at 09:00': '11.01.2019 at 09:40'}}, 'every! 2 hours': {
            'schedule': {'relative': True, 'specific_time': None, 'days_of_week': None,
                         'period': {'unit': 'hours', 'value': 2}},
            'appied_schedule': {'01.05.2019 at 20:30': '01.05.2019 at 22:30', '06.01.2019 at 13:00': '06.01.2019 at 15:00',
                                '09.01.2019 at 17:00': '09.01.2019 at 19:00', '10.01.2019 at 09:00': '10.01.2019 at 11:00',
                                '10.01.2019 at 12:00': '10.01.2019 at 14:00',
                                '11.01.2019 at 09:00': '11.01.2019 at 11:00'}}}
    if res == true_res:
        print("Scheduling functionality is ok")
    else:
        print("Failed: Scheduling functionality test")