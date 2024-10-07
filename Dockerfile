FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt ${LAMBDA_TASK_ROOT}

COPY . ${LAMBDA_TASK_ROOT}

WORKDIR ${LAMBDA_TASK_ROOT}

RUN yum update -y && yum install -y git

RUN pip install -r requirements.txt

RUN python -c "import torch; print('Torch version:', torch.__version__)"

RUN pip install face-detection

CMD ["lambda_function.lambda_handler"]