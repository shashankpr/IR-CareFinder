# -*- encoding: utf-8 -*-
import time
import random
import foursquare
import math
import logging
from BaseTask import BaseTask
from settings import settings
from tasks import task_hospital_duplicate_detector


class FourSquareCrawler(BaseTask):
    def __init__(self, metadata):
        self.metadata = metadata

    def execute(self):
        self._getHospitalDetails(self.metadata['targetSquare']['NE'], self.metadata['targetSquare']['SW'],
                                 self.metadata['step'])

    # order: northeast, southwest.

    # convert string to coordinate
    @staticmethod
    def _str2coor(coordinate_ne, coordinate_sw):
        coorData = []

        coordinates = [coordinate_ne, coordinate_sw]
        for item in coordinates:
            tmptup = []
            for coor in item.split(','):
                tmptup.append(float(coor.strip()))

            coorData.append(tmptup)

        return coorData

    # convert coordinate to string
    @staticmethod
    def _coor2str(coor):
        return [str(coor[0]), str(coor[1])]

    @staticmethod
    def _extend_area(coor, step):
        vdis = int(math.ceil(math.fabs((coor[0][0] - coor[1][0]) / step)))
        hdis = int(math.ceil(math.fabs((coor[0][1] - coor[1][1]) / step)))
        return [vdis, hdis]

    def _getHospitalDetails(self, coordinate_ne, coordinate_sw, step=0.1):
        client = foursquare.Foursquare(client_id=settings['foursquare']['client_id'],
                                       client_secret=settings['foursquare']['client_secret'])
        coor = self._str2coor(coordinate_ne, coordinate_sw)

        exstep = self._extend_area(coor, step)  # number of steps in two direction (vertical, horizontal)

        for i in range(exstep[0]):
            for j in range(exstep[1]):
                nepoint = str([round(coor[0][0] - i * step, 2), round(coor[0][1] - j * step, 2)])[1:-1]
                swpoint = str([round(coor[0][0] - step * (i + 1), 2), round(coor[0][1] - step * (j + 1), 2)])[1:-1]

                logging.info([nepoint, swpoint])

                results = client.venues.search(params={'query': 'hospital', 'intent': 'browse',
                                                       'ne': nepoint,
                                                       'sw': swpoint})
                logging.info(str(len(results['venues'])) + " hospitals in this area")

                for item in results['venues']:
                    result = {
                        "id": item['id'],
                        "name": item['name'],
                        "url": item.get('url', ''),
                        "contact": self._extract_contact_info(item['contact']),
                        "location": self._extract_location_info(item['location']),
                        "log": []
                    }

                    logging.info("Found hospital \"{}\"".format(result['name']))
                    self._output_hospital(result)
                    logging.info(result)

                time.sleep(random.randint(2, 3))

    def _output_hospital(self, hospital_data):
        queue = self.queue
        logging.info('Add hospital to task queue')
        queue.enqueue(task_hospital_duplicate_detector, hospital_data)

    def _extract_contact_info(self, item_contact):
        contact_info = {
            "phone": item_contact.get('formattedPhone', ''),
            "facebook": item_contact.get('facebookName', ''),
            "twitter": item_contact.get('twitter'),
        }
        return contact_info

    def _extract_location_info(self, item_location):
        location_info = {
            "address": item_location.get('formattedAddress', ''),
            "lat": item_location.get('lat'),
            "lng": item_location.get('lng'),
        }
        return location_info
