FROM python:alpine

# Install Build dependencies
RUN apk --no-cache add python3-dev gcc musl-dev linux-headers bluez

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app
RUN pip3 install -r requirements.txt

COPY . /app

CMD [ "python3", "main.py" ]