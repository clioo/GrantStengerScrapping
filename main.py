# Import Dependencies
import requests
import json
import csv
import sys
import os
from datetime import datetime


class GrantStenger:
    """This class contains all the methods(private and public) necessary to 
    scrape the data from the omsweb page"""

    # Private methods
    def _get_formatted_date(self):
        """Gets a string of the date as the client requested: MM-DD-YY"""
        today = datetime.now()
        return today.strftime('%m-%d-%y')

    def _get_jailtrack_url(self, token, start_from=0, limit=100000):
        """Parse the url with the token and its boundaries"""
        url =  f"""https://omsweb.public-safety-cloud.com/jtclientweb//(S({token}))/JailTracker/GetInmates?start={start_from}&limit={limit}&sort=LastName&dir=ASC"""
        return url

    def _get_token(self):
        """Getting the token from the url"""
        with requests.Session() as session:
            # This first request is to get redirected and get the token
            url = 'https://omsweb.public-safety-cloud.com/jtclientweb/jailtracker/index/Greene_County_MO'
            response = session.get(url, allow_redirects=True)
            url_split = response.url.split('/')
            token = url_split[4]
            # Cleaning your token
            token = token[3:-2]
            return token

    def _export_to_csv(self, data, file_name='data'):
        """Data must be an array of dictionaries so it can be exported"""
        if data:
            # If file exists, creates another
            relative_path = f'./results/{file_name}.csv'
            if os.path.exists(relative_path):
                import uuid
                relative_path = f'./results/{file_name}_{uuid.uuid1()}.csv'
            # ******************************
            with open(relative_path, 'w') as output_file:
                keys = data[0].keys()
                dict_writer = csv.DictWriter(
                    output_file,
                    fieldnames=keys,
                    lineterminator='\n'
                )
                dict_writer.writeheader()
                dict_writer.writerows(data)
                full_path = os.path.abspath(output_file.name)
                return True, f'Data exported successfully to {full_path}'
            # Returns false if an error happens
            return False, 'An error occurred exporting your data.'
        # Returns False if there's no data to parse
        return False, 'No data was given'

    def get_data(self, start_from=0, limit=100000):
        """Main and public method to get the data"""
        # Create session
        date = self._get_formatted_date()
        print('Getting token...')
        token = self._get_token()
        print('Getting final endpoint...')
        url = self._get_jailtrack_url(token, start_from, limit)
        file_name = f'Greene-County-{date}'
        print('Scrapping data...')
        with requests.Session() as session:
            response = session.get(url)
            body = json.loads(response.content)
            data = body['data']
            print('Exporting data...')
            wasExported, exportedMessage = self._export_to_csv(
                data=data,
                file_name=file_name
            )
            print(exportedMessage)
            return wasExported, exportedMessage


if __name__ == "__main__":
    grant_stenger = GrantStenger()
    try:
        start = int(str(sys.argv[1]))
        limit = int(str(sys.argv[2]))
    except:
        print('No args given, getting from 0 to 100000')
        start = 0
        limit = 100000
    grant_stenger.get_data(start, limit)