FROM python:3.11-slim

RUN apt-get update && apt-get install -y git

RUN mkdir -p /app

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

RUN pip3 install git+https://github.com/hukkelas/DSFD-Pytorch-Inference.git

CMD ["lambda_function.lambda_handler"]