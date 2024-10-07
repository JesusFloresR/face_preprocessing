FROM python:3.11-slim

RUN mkdir -p /app

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

RUN pip3 install git+https://github.com/hukkelas/DSFD-Pytorch-Inference.git

CMD ["python3", "lambda_function.py"]