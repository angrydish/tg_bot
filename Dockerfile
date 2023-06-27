FROM python:3.10
#
WORKDIR /code
#
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
COPY ./app /code/app
COPY ./db /code/db
COPY ./handlers /code/handlers
COPY ./keyboards /code/keyboards
COPY ./models /code/models
COPY ./queries /code/queries
COPY ./states /code/states
COPY ./.env /code/.env
COPY ./main.py /code/main.py
#

CMD ["python3", "-u", "main.py"]
