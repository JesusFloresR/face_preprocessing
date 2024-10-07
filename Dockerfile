FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt ${LAMBDA_TASK_ROOT}

COPY . ${LAMBDA_TASK_ROOT}

RUN yum update -y && yum install -y git && yum clean all

RUN pip install -r requirements.txt

RUN pip install git+https://github.com/hukkelas/DSFD-Pytorch-Inference.git

CMD ["lambda_function.lambda_handler"]