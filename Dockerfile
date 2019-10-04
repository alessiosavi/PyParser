FROM python:latest

ADD requirements.txt /app/
WORKDIR /app
RUN python3 -m pip install -r requirements.txt

ADD . /app
ENV FLASK_APP=server/__init__.py
EXPOSE 3000
CMD ["python", "manage.py", "start"]