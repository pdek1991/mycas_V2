import datetime
import configparser
import mysql.connector.pooling
import time
import socket
import threading
import logging
import sys

config = configparser.ConfigParser()
config.read(r'stage_cycle.ini')

logging.basicConfig(
    level=logging.INFO,  # Set log level
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

db_config = {
    "host": "192.168.56.112",
    "user": "omi_user",
    "password": "omi_user",
    "database": "cas",
}

connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="my_pool", pool_size=30, **db_config)

# Create a cursor to interact with the database



cycle_osm = int(config.get(str(44), 'cycle'))
stage_osm = int(config.get(str(44), 'stage'))
cycle_adddevice = int(config.get(str(10), 'cycle'))
stage_adddevice = int(config.get(str(10), 'stage'))
cycle_entitlement = int(config.get(str(21), 'cycle'))
stage_entitlement = int(config.get(str(21), 'stage'))

def cycler(string, multicast_group, port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Set the time-to-live (TTL) for the socket
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    # Convert the string to bytes
    data = string.encode('utf-8')
    try:
        # Send the data to the multicast group and port
        sock.sendto(data, (multicast_group, port))
        #print(f"String '{string}' streamed over multicast IP {multicast_group}:{port}")
    except socket.error as e:
        logger.info(f"Error: {e}")
        #print(f"Error: {e}")
    finally:
        # Close the socket
        sock.close()

# Example usage
multicast_group = '224.1.1.1'  # Multicast IP address
port = 5000  # Port number
#string_to_stream = "Hello, multicast!"

def osm():
    connection = connection_pool.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT starttime, endtime, emmdata, emmtype FROM emmg where emmtype = 21 limit 1000")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    current_time = int(time.time())
    
    for row in rows:
        starttime, endtime, emmdata, emmtype = row
        stage_endtime = int(starttime + stage_osm)
    # Check if current time (in epoch) is less than end time for the emmtype
        if current_time < endtime and current_time < stage_endtime:
            cycler(emmdata, multicast_group, port)
            logger.info(f"EMM Data: {emmdata}")
            #print(emmdata)
    logger.info("Cycle OSM done")
    time.sleep(cycle_osm)

def adddevice():
    connection = connection_pool.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT starttime, endtime, emmdata, emmtype FROM emmg where emmtype = 10 limit 1000")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    current_time = int(time.time())
    
    for row in rows:
        starttime, endtime, emmdata, emmtype = row
        stage_endtime = int(starttime + stage_adddevice)
    # Check if current time (in epoch) is less than end time for the emmtype
        if current_time < endtime and current_time < stage_endtime:
            cycler(emmdata, multicast_group, port)
            #print(emmdata)
    logger.info('Cycle adddevice Done')
    
    time.sleep(cycle_adddevice)

def entitlement():
    connection = connection_pool.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT starttime, endtime, emmdata, emmtype FROM emmg where emmtype = 44 limit 1000")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    current_time = int(time.time())
    
    for row in rows:
        starttime, endtime, emmdata, emmtype = row
        stage_endtime = int(starttime + stage_entitlement)
        # Check if current time (in epoch) is less than end time for the emmtype
        if current_time < endtime and current_time < stage_endtime:
            cycler(emmdata, multicast_group, port)
            #print(emmdata)
   
    logger.info('Cycle entitlement Done')     
    time.sleep(cycle_entitlement)


while True:
    osm_thread = threading.Thread(target=osm)
    entitlement_thread = threading.Thread(target=entitlement)
    adddevice_thread = threading.Thread(target=adddevice)

    # Start the threads
    osm_thread.start()
    entitlement_thread.start()
    adddevice_thread.start()

    # Wait for all threads to complete
    osm_thread.join()
    entitlement_thread.join()
    adddevice_thread.join()


        
