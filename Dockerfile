FROM python:3.11-slim

RUN mkdir -p /app

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

RUN pip install git+https://github.com/hukkelas/DSFD-Pytorch-Inference.git

CMD ["python3", "lambda_function.py"]