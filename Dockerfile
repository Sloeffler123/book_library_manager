FROM debian:stable-slim

WORKDIR /app

RUN apt update
RUN apt upgrade -y

RUN apt-get install -y ca-certificates

RUN apt-get install libzbar0 -y

RUN apt install python3 python3-pip -y

RUN apt install python3.13-venv -y

RUN python3 -m venv .venv

COPY requirements.txt requirements.txt

RUN pip install --break-system-packages -r requirements.txt

COPY . . 

ENV PORT=8991

CMD ["fastapi", "run", "api_files/api_code.py"]