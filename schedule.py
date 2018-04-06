from functools import lru_cache
import tzlocal
from datetime import datetime, timedelta

class ScheduleManager(object):
    def __init__(self, config):
        self.config = config
        self.timezone = tzlocal.get_localzone()

    @staticmethod
    @lru_cache(maxsize=8, typed=True)
    def _calc_sched(day_sched):
        # If day isn't defined, 9-5. If defined and empty, not on that day
        if not day_sched:
            return None
        day_sched = [int(x) for x in day_sched.split('-')]
        return day_sched

    def _getsched(self):
        if 'schedule' in self.config:
            # Missing days have no active hours
            schedule = self.config['schedule'] or {}
            schedule = [schedule.get(("mon", "tue", "wed", "thu", "fri", "sat", "sun")[x]) for x in range(7)]
        else:
            # Default schedule is 9-5 weekdays
            schedule = ['9-17']*5 + ['']*2

        return [self._calc_sched(d) for d in schedule]

    def get_next_sleep(self):
        # If schedule key exists and is empty, then there is no schedule
        schedule = self._getsched()
        if schedule == [None]*7:
            return 0
        sleep_day = datetime.now().replace(tzinfo=self.timezone, hour=0, minute=0, second=0, microsecond=0)
        sched = None
        while True:
            sched = schedule[sleep_day.weekday()]
            if sched is None:
                sleep_day -= timedelta(1)
            else:
                break
        return sleep_day.replace(hour=sched[1])

    def get_next_wake(self):
        # If schedule key exists and is empty, then there is no schedule
        schedule = self._getsched()
        if schedule == [None]*7:
            return 0
        wake_day = datetime.now().replace(tzinfo=self.timezone, hour=0, minute=0, second=0, microsecond=0) + timedelta(1)
        sched = None
        while True:
            sched = schedule[wake_day.weekday()]
            if sched is None:
                wake_day += timedelta(1)
            else:
                break
        return wake_day.replace(hour=sched[0])
