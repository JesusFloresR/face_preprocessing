FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt ${LAMBDA_TASK_ROOT}

COPY . ${LAMBDA_TASK_ROOT}

RUN apt-get update && apt-get install -y git

RUN pip3 install -r requirements.txt

RUN pip3 install git+https://github.com/hukkelas/DSFD-Pytorch-Inference.git

CMD ["lambda_function.lambda_handler"]