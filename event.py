"""
Meetup Event data object
"""

from datetime import datetime, timedelta
import json
import pytz

class Event(object):
    """Represents the MeetUp event"""
    def __init__(self, id, name, time, duration, description, updated, venue_name, **kwargs):
        self.id = id # Using id from the meetup api, thus the name override.
        self.name = name
        self.time = time
        self.duration = duration
        self.description = description
        self.updated = updated
        self.venue_name = venue_name
        self.length = timedelta(milliseconds=self.duration)
        self.set_timezone()

    def __repr__(self):
        return json.dumps(self.__dict__)

    def _localize(self, the_time, zone=None):
        if zone is None:
            zone = pytz.utc
        utc = datetime.fromtimestamp(the_time)
        return utc.astimezone(zone)

    def set_timezone(self, time_zone=None):
        """Applies the given timezone to the datetime values of the event"""
        self.when = self._localize(self.time, time_zone)
        self.modified = self._localize(self.updated, time_zone)
