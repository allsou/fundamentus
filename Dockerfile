FROM python:3.8
LABEL maintainer="allansouzatk@gmail.com"
WORKDIR /app
COPY Pipfile ./
RUN pipenv install --skip-lock --system
COPY . .
EXPOSE 5000/tcp
ENTRYPOINT python server.py
