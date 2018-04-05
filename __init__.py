import yaml
import os
import tzlocal
from datetime import datetime, timedelta

class Config(object):
    def __init__(self, path=None):
        self.config = {}

        self.path = os.path.expanduser('~/.sensei.yaml')
        self.reload(path)

    def reload(self, path=None):
        if path:
            path = os.path.expanduser(path)
            if os.path.isfile(path):
                self.path = path

        with open(self.path, 'r') as strm:
            self.config = yaml.load(strm)

    def __getitem__(self, n):
        return self.config[n]

    def __contains__(self, k):
        return k in self.config

    def get(self, k, d=None):
        return self.config.get(k, d)

class ScheduleManager(object):
    def __init__(self, config):
        if 'schedule' in config:
            schedule = config['schedule']
        else:
            # Default schedule is 9-5 weekdays
            schedule = ['9-17']*5 + ['']*2
        def calc_sched(day_idx):
            days = "mon", "tue", "wed", "thu", "fri", "sat", "sun"
            # If day isn't defined, 9-5. If defined and empty, not on that day
            day_sched = schedule.get(days[day_idx], '9-17')
            if not day_sched:
                return None
            day_sched = [int(x) for x in day_sched.split('-')]
            return day_sched

        self.schedule = [calc_sched(d) for d in range(7)]
        self.timezone = tzlocal.get_localzone()

    def get_next_sleep(self):
        if self.schedule == [None]*7:
            return 0
        sleep_day = datetime.now().replace(tzinfo=self.timezone, hour=0, minute=0, second=0, microsecond=0)
        sched = None
        while True:
            sched = self.schedule[sleep_day.weekday()]
            if sched is None:
                sleep_day -= timedelta(1)
            else:
                break
        return sleep_day.replace(hour=sched[1])

    def get_next_wake(self):
        if self.schedule == [None]*7:
            return 0
        wake_day = datetime.now().replace(tzinfo=self.timezone, hour=0, minute=0, second=0, microsecond=0) + timedelta(1)
        sched = None
        while True:
            sched = self.schedule[wake_day.weekday()]
            if sched is None:
                wake_day += timedelta(1)
            else:
                break
        return wake_day.replace(hour=sched[0])
