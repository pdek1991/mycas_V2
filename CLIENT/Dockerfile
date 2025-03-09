FROM python
#comment
WORKDIR /root/mycas/CLIENT

COPY requirements.txt .
RUN pip install --no-cache-dir -r /root/mycas/CLIENT/requirements.txt

VOLUME ["/root/mycas/CLIENT"]

COPY . .
CMD ["python", "stb_client.py"]

