FROM python:3.11
WORKDIR /usr/src/app

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:api", "--host", "0.0.0.0", "--port", "8000" ,"--reload"]
