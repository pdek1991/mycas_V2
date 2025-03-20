import datetime
import configparser
import mysql.connector.pooling
from mysql.connector import pooling, Error 
import time
import socket
import threading
import logging
import sys
import os

config = configparser.ConfigParser()
config.read(r'stage_cycle.ini')

logging.basicConfig(
    level=logging.INFO,  # Set log level
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

##Get ENV from CM and SECRETS
db_user = os.getenv("DB_USER", "omi_user").strip()
db_pass = os.getenv("DB_PASS").strip()
db_host = os.getenv("HOST", "mycas-mysql-0.mysql.mycas").strip()
db_name = os.getenv("DB_NAME").strip()
db_port = int(os.getenv("DB_PORT", 3306))

multicast_group = os.getenv("MULTICAST", "224.1.1.1").strip()  
multicast_port = int(os.getenv("PORT", 5000))


db_config = {
    "host": db_host,
    "user": db_user,
    "password": db_pass,
    "database": db_name,
    "port": db_port,
}


if not db_host or not db_name or not db_pass:
    raise ValueError("Database credentials (DB_HOST, DB_NAME, DB_PASS) are required!")


try:
    connection_pool = pooling.MySQLConnectionPool(pool_name="my_pool", pool_size=10, **db_config)
    logger.info("Database connection pool created successfully.")
except Error as e:
    logger.info(f"Error while creating MySQL connection pool: {e}")
    exit(1)
# Create a cursor to interact with the database



cycle_osm = int(config.get(str(44), 'cycle'))
stage_osm = int(config.get(str(44), 'stage'))
cycle_adddevice = int(config.get(str(10), 'cycle'))
stage_adddevice = int(config.get(str(10), 'stage'))
cycle_entitlement = int(config.get(str(21), 'cycle'))
stage_entitlement = int(config.get(str(21), 'stage'))

def cycler(string, multicast_group, multicast_port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Set the time-to-live (TTL) for the socket
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    # Convert the string to bytes
    data = string.encode('utf-8')
    try:
        # Send the data to the multicast group and port
        sock.sendto(data, (multicast_group, multicast_port))
        logger.info(f"String '{string}' streamed over multicast IP {multicast_group}:{multicast_port}")
    except socket.error as e:
        logger.info(f"Error: {e}")
        #print(f"Error: {e}")
    finally:
        # Close the socket
        sock.close()



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
            cycler(emmdata, multicast_group, multicast_port)
            logger.info(f"EMM Data: {emmdata}")
            logger.info(emmdata)
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
            cycler(emmdata, multicast_group, multicast_port)
            logger.info(emmdata)
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
            cycler(emmdata, multicast_group, multicast_port)
            logger.info(emmdata)
   
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


        
