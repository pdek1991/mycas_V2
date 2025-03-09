# mycas_V2





primary DB user root pwd mycas
replica user read_replica pwd read_replica


#For Replication run:
CREATE USER 'read_replica'@'%' IDENTIFIED WITH mysql_native_password BY 'read_replica';
GRANT REPLICATION SLAVE ON *.* TO 'read_replica'@'%';

GRANT REPLICATION SLAVE ON *.* TO 'read_replica'@'%';

FLUSH PRIVILEGES;


On replica

CHANGE MASTER TO 
  MASTER_HOST='mycas-mysql-0.mysql',
  MASTER_USER='read_replica',
  MASTER_PASSWORD='read_replica',
  MASTER_LOG_FILE='mysql-bin.000005',  -- Update with Primary's File
  MASTER_LOG_POS=35254;  -- Update with Primary's Position
START SLAVE;


On Master:

CREATE DATABASE cas;
CREATE USER 'omi_user'@'%' IDENTIFIED BY 'omi_user';

#create user 'test'@'%' IDENTIFIED with mysql_native_password by 'test';
GRANT ALL PRIVILEGES ON cas.* TO 'omi_user'@'%';

FLUSH PRIVILEGES;

USE cas;

CREATE TABLE entitlements (
    device_id VARCHAR(255),
    package_id VARCHAR(255),
    expiry DATE
);

CREATE TABLE devices (
    device_id VARCHAR(255),
    bskeys VARCHAR(255)
);

CREATE TABLE generate_osm (
    message_id INT,
    message_text TEXT,  
    device_id VARCHAR(255),
    expiry DATE
);


CREATE TABLE emmg (
    id INT AUTO_INCREMENT PRIMARY KEY,
    starttime INT,  
    endtime INT,    
    emmdata TEXT,   
    emmtype VARCHAR(255)
);


SET GLOBAL wait_timeout = 60;
SET SESSION wait_timeout = 60;
SET GLOBAL interactive_timeout = 600;


show slave status;
show master status;

