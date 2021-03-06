import json
from project import db
from project.models.event import Event, add_event
from project.models.user import User, add_user
from project.test.test_base import TestBase
from project.models.availability import Availability, create_availability
from project.test.event_handler_test import seed_event
from unittest.mock import Mock, patch


class CalendarTestCase(TestBase):
    def test_getting_calendar(self):
        mock_response = {
            "kind": "calendar#freeBusy",
            "timeMin": "2020-02-21T25:34:33.000Z",
            "timeMax": "2020-03-22T23:34:33.000Z",
            "calendars": {
                "test@email.com": {
                    "busy": [  #=> Busy 12am-9am and 5pm-12am
                        {
                            "start": "2020-02-25T10:30:00Z",
                            "end": "2020-02-25T12:00:00Z"
                        },
                        {
                            "start": "2020-02-26T10:00:00Z",
                            "end": "2020-02-26T12:00:00Z"
                        },
                        {
                            "start": "2020-02-27T10:00:00Z",
                            "end": "2020-02-27T12:00:00Z"
                        },
                        {
                            "start": "2020-02-28T10:00:00Z",
                            "end": "2020-02-21T12:00:00Z"
                        },
                        {
                            "start": "2020-02-28T10:00:00Z",
                            "end": "2020-02-21T12:00:00Z"
                        },
                        {
                            "start": "2020-02-29T10:00:00Z",
                            "end": "2020-02-29T12:00:00Z"
                        },
                    ]
                }
            }
        }
        with patch('project.services.google_calendar.build') as mock_method:
            mock_method.return_value.freebusy.return_value.query.\
            return_value.execute.return_value = mock_response
            result = seed_event()
            user = result['user']
            event = result['event']
            db.session.commit()

            response = self.api.get(
                f'/users/{user.public_id}/events/{event.url}/calendar?timezone=America/Los_Angeles'
            )

            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 200)
