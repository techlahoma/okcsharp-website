"""
    AneMetro Hexo

    Provides post creation for Hexo static sites.
"""

import os

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
