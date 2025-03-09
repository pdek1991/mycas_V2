FROM python
#comment
WORKDIR /root/mycas/CYCLER

COPY requirements.txt .
RUN pip install --no-cache-dir -r /root/mycas/CYCLER/requirements.txt

VOLUME ["/root/mycas/CYCLER"]

COPY . .
CMD ["python", "cycler.py"]
