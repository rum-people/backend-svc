FROM python:3.10-bullseye

WORKDIR /app
COPY requirements.txt ./

RUN mkdir -p /root/.cache/huggingface/hub
RUN pip3 install --no-cache -r requirements.txt

COPY . ./

ENTRYPOINT [ "uvicorn", "main:app", "--reload" , "--host", "0.0.0.0" ]