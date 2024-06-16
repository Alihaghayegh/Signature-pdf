from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# from signature_pdf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signature_pdf.settings')

app = Celery('signature_pdf')
print("celery")
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')