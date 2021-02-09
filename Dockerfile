FROM python:3.8

WORKDIR /eTechStore
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .

#WORKDIR /app
#RUN chmod 777 -R /home
#RUN python ./eTechStore/main.py
CMD ["python", "./eTechStore/main.py"]