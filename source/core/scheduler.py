import pandas as pd


class Schedule(object):
    def __init__(self):
        pass
        self.schedule = pd.Series()  # timestamp ->

    def now(self):
        return pd.timestamp.now() # todo: how to get pd.now

    def next_event_ts(self):

        return

