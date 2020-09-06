FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
#RUN pip install pyyaml sqlalchemy mysql-connector-python python-jose[cryptography] passlib[bcrypt] python-multipart finnhub-python==1.1.7 fastapi uvicorn
# for python3.6, the following is necessary
#RUN pip install async-exit-stack async-generator
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY app /app/
EXPOSE 8000
WORKDIR /app
CMD ["./wait-for-db.sh"]
