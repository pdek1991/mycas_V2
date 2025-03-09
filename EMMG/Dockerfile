FROM python
#comment
WORKDIR /root/mycas/EMMG

COPY requirements.txt .
RUN pip install --no-cache-dir -r /root/mycas/EMMG/requirements.txt

VOLUME ["/root/mycas/EMMG"]

COPY . .
CMD ["python", "emmg.py"]
