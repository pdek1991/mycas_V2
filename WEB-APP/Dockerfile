FROM python
#comment
WORKDIR /root/mycas/WEB-APP

COPY requirements.txt .

RUN pip install --no-cache-dir -r /root/mycas/WEB-APP/requirements.txt

VOLUME ["/root/mycas/WEB-APP"]

COPY . .

EXPOSE 5005
EXPOSE 8080
CMD ["python", "webpage.py"]
