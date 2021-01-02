FROM python:3.9.1-slim AS server
RUN mkdir /server
WORKDIR /server
COPY ./backend/requirements.txt /server
RUN pip install -r requirements.txt
COPY ./backend /server
