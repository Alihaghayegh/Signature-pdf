from celery import shared_task
import pdfkit
from django.core.files.base import ContentFile
from django.utils.timezone import now
from .models import UserInfo

@shared_task
def create_pdf(user_id):
    try:
        print("tasks")
        user = UserInfo.objects.get(id=user_id)
        pdf_content = f"<h1>{user.first_name} {user.last_name}</h1><p>Date: {now()}</p>"
        pdf_content += f"<img src='{user.signature.url}' alt='Signature'/>"
        
        pdf_file = pdfkit.from_string(pdf_content, False)
        user.pdf_file.save(f'{user.username}.pdf', ContentFile(pdf_file))
        return f"PDF created for {user.username}"
    except UserInfo.DoesNotExist:
        return "User not found"
