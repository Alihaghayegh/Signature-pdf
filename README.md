# Signature-pdf

* To Run Project:

At first install requirements:

```sh
pip install -r requirements.txt
```
Then run the Main Django app:

```sh
python manage.py run server
```

Then run Redis (On WSL):

```sh
redis-server
```
Then run Redis ClI (On WSL):

```sh
redis-cli
```

Finally run Celery worker:
```sh
celery -A signature_pdf worker --loglevel=info -P solo
```