# -*- encoding: utf-8 -*-
import time
import random
import foursquare
import math
import logging
from BaseTask import BaseTask
from settings import settings
from helpers import normalize_hospital_name
from tasks import task_hospital_duplicate_detector


class FourSquareCrawler(BaseTask):
    def __init__(self, metadata):
        """Initializes a FourSquareWorker instance.

        Args:
            metadata -- Input dictionary, should contain the targeted square coordinates under key 'targetSquare'.
        """
        self.metadata = metadata

    def execute(self):
        """Executes a FourSquareWorker instance.
        """
        self._getHospitalDetails(self.metadata['targetSquare']['NE'], self.metadata['targetSquare']['SW'],
                                 self.metadata['step'])

    @staticmethod
    def _str2coor(coordinate_ne, coordinate_sw):
        """Convert the strings to coordinates.
        
        Args:
            coordinate_ne -- The north east point of the square.
            coordinate_sw -- The south west point of the square.
        
        Returns:
            coorData -- List containing the converted coordinates.
        """
        coorData = []

        coordinates = [coordinate_ne, coordinate_sw]
        for item in coordinates:
            tmptup = []
            for coor in item.split(','):
                tmptup.append(float(coor.strip()))

            coorData.append(tmptup)

        return coorData

    @staticmethod
    def _coor2str(coor):
        """Convert the coordinates to strings.

        Args:
            coor -- List containing the coordinates.
        
        Returns:
            List containing the converted strings.
        """
        return [str(coor[0]), str(coor[1])]

    @staticmethod
    def _extend_area(coor, step):
        """Calculates amount of subsquares.

        Args:
            coor -- List containing the coordinates.
            step -- Size of a subsquare

        Returns:
            List containing vdis and hdis.
            vdis -- Vertical length of a subsquare
            hdis -- Horizontal length of a subsquare 
        """
        vdis = int(math.ceil(math.fabs((coor[0][0] - coor[1][0]) / step)))
        hdis = int(math.ceil(math.fabs((coor[0][1] - coor[1][1]) / step)))
        return [vdis, hdis]

    def _getHospitalDetails(self, coordinate_ne, coordinate_sw, step=0.1):
        """Crawls for hospitals in the provided square. 

        Args:
            coordinate_ne -- The north east point of the square.
            coordinate_sw -- The south west point of the square.
            step -- Size of a subsquare
        """
        client = foursquare.Foursquare(client_id=settings['foursquare']['client_id'],
                                       client_secret=settings['foursquare']['client_secret'])
        coor = self._str2coor(coordinate_ne, coordinate_sw)

        #Calculate the amount of steps to be taken in two directions (vertical, horizontal).
        exstep = self._extend_area(coor, step)

        for i in range(exstep[0]):
            for j in range(exstep[1]):
                # Calculate the location of current subsquare
                nepoint = str([round(coor[0][0] - i * step, 2), round(coor[0][1] - j * step, 2)])[1:-1]
                swpoint = str([round(coor[0][0] - step * (i + 1), 2), round(coor[0][1] - step * (j + 1), 2)])[1:-1]

                logging.info([nepoint, swpoint])

                # Search the subsquare on Foursquare for hospitals.
                results = client.venues.search(params={'query': 'hospital', 'intent': 'browse',
                                                       'ne': nepoint,
                                                       'sw': swpoint})
                logging.info(str(len(results['venues'])) + " hospitals in this area")

                # Extract the data from all retrieved hospitals.
                for item in results['venues']:
                    result = {
                        "foursquare-id": item['id'],
                        "name": item['name'],
                        "normalized-name": normalize_hospital_name(item['name']),
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
        """Takes an extracted hospital and adds it to the queue.

        Args:
            hospital_data -- Dictionary containing the hospital data.
        """
        from queue_helper import q
        logging.info('Add hospital to task queue')
        q.enqueue(task_hospital_duplicate_detector, hospital_data)

    def _extract_contact_info(self, item_contact):
        """Extracts the contact info from an item.

        Args:
            item_contact -- Item containing the contact information.
        
        Returns:
            contact_info -- The extracted contact info.
        """
        contact_info = {
            "phone": item_contact.get('formattedPhone'),
            "facebook": item_contact.get('facebookName'),
            "twitter": item_contact.get('twitter'),
        }
        return contact_info

    def _extract_location_info(self, item_location):
        """Extracts the location details from an item.

        Args:
            item_location -- Item containing the location information.

        Returns:
            location_info -- The extracted location data.
        """
        location_info = {
            "address": item_location.get('formattedAddress'),
            "lat": item_location.get('lat'),
            "lng": item_location.get('lng'),
        }
        return location_info
