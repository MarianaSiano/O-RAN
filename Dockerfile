FROM python:3.9-slim
WORKDIR /app
COPY ric_mestre.py xapp_mock.py app_worker.py rapp_mock.app ./
CMD ["python", "-u", "ric_mestre.py"]