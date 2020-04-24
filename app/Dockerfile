# base image
FROM python:3.8.0-alpine

# copy project from local to container and set workdir
RUN mkdir -p /src/static
COPY . /src
WORKDIR /src

# python env
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install linux dependencies
RUN apk update && apk add libpq postgresql-dev gcc python3-dev musl-dev

# upgrade pip and install packages
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "./entrypoint.sh" ]
