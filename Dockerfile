FROM python:3-alpine

LABEL "com.github.actions.name"="ChatGPT Reviewer"
LABEL "com.github.actions.description"="Automated pull requests reviewing and issues triaging with ChatGPT"

WORKDIR /app

COPY ./app /app

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

ENTRYPOINT [ "/app/main.py" ]
