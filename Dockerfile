FROM python:3.10-alpine

WORKDIR /app
COPY requirements.txt ./

RUN pip3 install --no-cache -r requirements.txt

COPY . ./

ENTRYPOINT [ "uvicorn" ]
CMD [ "main:app", "--reload" , "--host", "0.0.0.0"]