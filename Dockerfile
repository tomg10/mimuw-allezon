FROM python:3.10.5-bullseye


EXPOSE 8000

# to invalidate docker cache
ADD http://worldclockapi.com/api/json/utc/now /etc/builddate

RUN git init

RUN git clone https://github.com/tomg10/mimuw-allezon.git

WORKDIR /mimuw-allezon

RUN pip install -r requirements.txt

WORKDIR /mimuw-allezon

ENV ALLEZON_REDIS_HOST=st123@st123vm102.rtb-lab.pl

CMD  uvicorn main_app:app --workers 2 --host 0.0.0.0 --port 8080