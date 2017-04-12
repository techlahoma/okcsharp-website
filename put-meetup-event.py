"""
theCodePutter

Puts the code he findses on meetup.
"""

import os
import json
from datetime import datetime, timedelta
from shutil import copyfile
from subprocess import run
from subprocess import PIPE
from functools import reduce
from pytz import timezone
import pytz
import reyaml
import requests

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

def get_next_event(api_key, api_root, group_name):
    """Returns the next meetup event."""
    url = "{0}/{1}/events".format(api_root, group_name)
    params = {
        "scroll": "next_upcoming",
        "page": "1",
        "key": api_key
    }
    response = requests.get(url, params=params)
    data = response.json()[0]

    data["time"] = data["time"] / 1000 # MeetUp gives timestamp in milliseconds
    data["updated"] = data["updated"] / 1000 # MeetUp gives timestamp in milliseconds

    event = Event(venue_name=data["venue"]["name"], **data)
    return event

def generate_post_filename(event):
    """Generates the filename for the event's post"""
    return event.when.strftime("%B-%Y-meetup.md").lower()

def get_template_path(template_name):
    """Get the path to the template file that will be copied"""
    return os.path.join("./scaffolds", template_name + ".md")

def process_placeholders(filename, event):
    """Returns processing the placeholders in the filename with values from the event"""
    content = ""
    values = event.__dict__
    with open(filename, mode="r") as post_file:
        for line in post_file:
            content += line.format(**values)
    return content

def get_git_url(config_filename, path_to_git_setting):
    """Reads the git url from the given yaml config file"""
    config = reyaml.load_from_file(config_filename)
    return reduce((lambda cur, item: cur[item]), path_to_git_setting.split("/"), config)

def commit_post(filename, git_url, message="Auto commit by thePutter", branch_name="master"):
    """Stages, commits, and pushes the created post"""
    if did_post_change(filename):
        print "Post changed: %s, pushing it." % filename
        run(["git", "remote", "add", "putter", git_url])
        run(["git", "add", filename])
        run(["git", "commit", "-m", message])

        # The build runs in detached head state. This works, but, I'm not sure
        # what sideeffects this may have. Something I'll look into.
        run(["git", "push", "putter", "HEAD:" + branch_name])
    else:
        print "Post did NOT change: %s" % filename

def did_post_change(filename):
    """Checks if the post filename changed or was created due to the generation process"""
    status = run(["git", "status", "-s"], stdout=PIPE, universal_newlines=True).stdout
    lines = status.split("\n")
    if " M %s" % filename in lines or "?? %s" % filename in lines:
        return True
    else:
        return False

def generate_post(template, destination_folder, event):
    """Generates event post file"""

    # Create initial post from template
    file_name = generate_post_filename(event)
    full_filename = destination_folder + "/" + file_name
    copyfile(template, full_filename)

    content = process_placeholders(full_filename, event)

    # Saving processed content
    with open(full_filename, mode="w") as post_file:
        for line in content:
            post_file.write(line)

    return full_filename

def get_putter_config(filename="thecodeputter.yml"):
    """Gets the config to use for processing"""
    return reyaml.load_from_file(filename)

def putt():
    """Runs the processing"""
    config = get_putter_config()
    event = get_next_event(config["meetup_apikey"], config["meetup_root"], config["group_name"])
    event.set_timezone(timezone(config["group_timezone"]))
    template_path = get_template_path(config["template_name"])
    post_filename = generate_post(template_path, config["posts_path"], event)

    git_url = get_git_url(config["yaml_filename"], config["yaml_query"])
    commit_post(post_filename, git_url, branch_name=config["posts_branch"])

if __name__ == "__main__":
    putt() # FORE!
