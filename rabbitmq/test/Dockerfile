FROM python:3.6

# install additional packages specific to this microservice
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /src
COPY ./src/test.py /src/

ENTRYPOINT [ "python3", "test.py" ]