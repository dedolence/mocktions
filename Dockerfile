# build image:
# docker build --tag <image_name> .

# run container from image:
# docker run --name <container_name> -p 8000:8000 --network=host <image_name> [-d --detach]

# to start shell in running container:
# docker exec -it <container_name> sh

FROM python:3

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt

RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "mocktions.wsgi"]