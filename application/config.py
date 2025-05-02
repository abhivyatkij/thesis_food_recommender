# Configuration file to store variables and constants that will be used globally across the application
# Import libraries
import os
import logging

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'}


# Create a logs/ folder if it does not already exist
os.makedirs(os.path.join(DIR_PATH, 'logs'), exist_ok=True)

# Create and configure logger
logging.basicConfig(filename=os.path.join(DIR_PATH, 'logs', 'recipe-ontology.log'),
                    format='%(asctime)s %(message)s',
                    filemode='w')

# Creating an object
LOGGER = logging.getLogger()

# Setting the threshold of logger to DEBUG
LOGGER.setLevel(logging.DEBUG)
