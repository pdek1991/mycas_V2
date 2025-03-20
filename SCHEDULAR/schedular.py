import datetime
import mysql.connector
import schedule
import time
import os
import logging
import sys

logging.basicConfig(
    level=logging.INFO,  # Set log level
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

db_user = os.getenv("DB_USER", "omi_user").strip()
db_pass = os.getenv("DB_PASS").strip()		##SECRET
db_host = os.getenv("HOST", "mycas-mysql-0.mysql.mycas").strip()
db_name = os.getenv("DB_NAME").strip()
db_port = int(os.getenv("DB_PORT", 3306))


def delete_expired_rows():
    # Connect to the database
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=db_name,
    )
    cursor = conn.cursor()

    # Get the current date
    today = datetime.date.today()
    epoch = int(time.time())
    
    # Define the tables to check and delete from
    tables = ['generate_osm', 'entitlements', 'emmg']
    deleted_rows_count = {}

    for table in tables:
        if table == 'generate_osm' or table == 'entitlements':
            # Delete rows where expiry is less than or equal to today's date
            query = f"DELETE FROM {table} WHERE expiry <= %s"
            cursor.execute(query, (today,))
            conn.commit()
            deleted_rows = cursor.rowcount
        elif table == 'emmg':
            # Delete rows where endtime is less than or equal to the current epoch timestamp
            query = f"DELETE FROM {table} WHERE endtime <= %s"
            cursor.execute(query, (epoch,))
            conn.commit()
            deleted_rows = cursor.rowcount

        # Store the count in the dictionary
        deleted_rows_count[table] = deleted_rows
        logger.info(f"Deleted {deleted_rows} rows from table {table}")

    # Close the database connection
    cursor.close()
    conn.close()

    # Return the deleted rows count
    return deleted_rows_count

# Schedule the delete_expired_rows() function to run every day at 00:00 hours
schedule.every().day.at("00:00").do(delete_expired_rows)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
