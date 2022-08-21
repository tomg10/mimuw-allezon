FROM python:3.10.5-bullseye

WORKDIR /app

EXPOSE 8000

copy . .