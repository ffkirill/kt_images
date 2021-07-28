FROM python:3

WORKDIR /usr/src/kt-images

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/kt_images /usr/src/kt-images/kt_images
EXPOSE $API_PORT

CMD python -m kt_images --port $API_PORT
