
# MyCAS V2

## Database Configuration

### Primary Database
- **User:** `root`
- **Password:** `mycas`

### Replica Database
- **User:** `read_replica`
- **Password:** `read_replica`

### Replication Setup
#### On Primary Database:
```sql
CREATE USER 'read_replica'@'%' IDENTIFIED WITH mysql_native_password BY 'read_replica';
GRANT REPLICATION SLAVE ON *.* TO 'read_replica'@'%';
FLUSH PRIVILEGES;
```

#### On Replica Database:
```sql
CHANGE MASTER TO
  MASTER_HOST='mycas-mysql-0.mysql',
  MASTER_USER='read_replica',
  MASTER_PASSWORD='read_replica',
  MASTER_LOG_FILE='mysql-bin.000011',  -- Update with Primary's File
  MASTER_LOG_POS=157;  -- Update with Primary's Position
START SLAVE;
```

#### On Primary Database:
```sql
CREATE DATABASE cas;
CREATE USER 'omi_user'@'%' IDENTIFIED BY 'omi_user';
GRANT ALL PRIVILEGES ON cas.* TO 'omi_user'@'%';
FLUSH PRIVILEGES;
```

## Docker Setup
### MySQL Container
```sh
docker run --name mycas_db -e MYSQL_ROOT_PASSWORD=mycas -d -p 3306:3306 pdek1991/mycas_mysql
sudo docker exec -it mycas_db mysql -h 127.0.0.1 -P 3306 -u root -p
```

### Kafka Container
```sh
docker run -d --name mycas_kafka -p 9092:9092 -p 2181:2181 pdek1991/mycas_kafka
```

## Kafka Configuration
```sh
bin/zookeeper-server-start.sh config/zookeeper.properties &
bin/kafka-server-start.sh config/server.properties &
```

### Create and Validate Topic
```sh
bin/kafka-topics.sh --create --topic topic_mycas --bootstrap-server 192.168.56.112:9092
bin/kafka-topics.sh --describe --topic topic_mycas --bootstrap-server 192.168.56.112:9092
```

### Send and Read Messages
```sh
bin/kafka-console-producer.sh --topic topic_mycas --bootstrap-server 192.168.56.112:9092
bin/kafka-console-consumer.sh --topic topic_mycas --bootstrap-server 192.168.56.112:9092
```

## Environment Variables

### **Client**
```sh
MULTICAST=224.1.1.1
PORT=5000
```

### **Cycler**
```sh
DB_USER=omi_user
DB_PASS= #SECRET
HOST=mycas-mysql-0.mysql.mycas
DB_NAME=cas
DB_PORT=3306
MULTICAST=224.1.1.1
PORT=5000
```

### **EMMG**
```sh
DB_USER=omi_user
DB_PASS= #SECRET
HOST=mycas-mysql-0.mysql.mycas
DB_NAME=cas
DB_PORT=3306
KAFKA_SERVER=kafka-0.kafka.mycas:9092
KAFKA_GROUP_ID=emmg
KAFKA_TOPIC=topic_mycas
```

### **Scheduler**
```sh
DB_USER=omi_user
DB_PASS= #SECRET
HOST=mycas-mysql-0.mysql.mycas
DB_NAME=cas
DB_PORT=3306
```

### **WebApp**
```sh
DB_USER=omi_user
DB_PASS= #SECRET
HOST=mycas-mysql-0.mysql.mycas
DB_NAME=cas
DB_PORT=3306
KAFKA_SERVER=kafka-0.kafka.mycas:9092
KAFKA_GROUP_ID=emmg
KAFKA_TOPIC=topic_mycas
```

## Kubernetes Deployment
### Start All Pods
```sh
docker ps -a | grep -vi up | awk -F " " '{print $1}' | xargs docker start
```

### Update MySQL Connector
- Ensure `mysql_native_password` is used.

## Elasticsearch Setup
### Token
```sh
eyJ2ZXIiOiI4LjEzLjAiLCJhZHIiOiIuLi4iLCJrZXkiOiJwNl90MVk0QkVPQko5YkdqR...
```

### Create User
```sh
elasticsearch-users useradd root -p root1991 -r superuser
```

### Kibana Access
[http://192.168.56.114:5601/](http://192.168.56.114:5601/)

## ETCD Backup
```sh
ETCDCTL_API=3 etcdctl --endpoints 127.0.0.1:2379 \  
--cert=/etc/kubernetes/pki/etcd/server.crt \  
--key=/etc/kubernetes/pki/etcd/server.key \  
--cacert=/etc/kubernetes/pki/etcd/ca.crt \  
snapshot save 15Mar2025.db
```

## Security Scan with Trivy
```sh
wget https://github.com/aquasecurity/trivy/releases/latest/download/trivy_Linux-64bit.tar.gz
tar zxvf trivy_Linux-64bit.tar.gz
sudo mv trivy /usr/local/bin/

trivy image pdek1991/mycas_emmg:v1
trivy image --exit-code 1 --severity CRITICAL pdek1991/mycas_emmg:v1
```

## Kubernetes Enhancements
- Create **Network Policy**
- Deploy **Ingress Resource**
- Configure **Horizontal Pod Autoscaler (HPA)**

## Istio Service Mesh Installation
```sh
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH
istioctl install --set profile=demo -y
```

### Deploy Istio Addons
```sh
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.18/samples/addons/kiali.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.18/samples/addons/grafana.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.18/samples/addons/prometheus.yaml
```

## Additional Notes
- Elasticsearch and Kibana are running on **swarm03**
- Python app is running in a container to send data
- Ensure replication status:
```sql
SHOW SLAVE STATUS \G;
SHOW MASTER STATUS;
```



