
__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

from . import BaseModel, Act


class Story(BaseModel):
    def __init__(self, xml_data):
        self.name = xml_data.get('name')
        self.owner = xml_data.get('owner')
        self.act = Act(xml_data.find('Act'))

    @property
    def to_json(self):
        return {
            "name": self.name,
            "owner": self.owner,
            "act": self.act.to_json
        }
