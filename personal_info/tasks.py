#! coding: utf-8

from celery import shared_task
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from django.core.files.base import ContentFile
from django.utils.timezone import now
import khayyam
from rtl import rtl
from .models import UserInfo, PDFFile
from io import BytesIO
import os

@shared_task
def create_pdf(user_id):
    try:
        user_info = UserInfo.objects.get(id=user_id)
        pdf_file, created = PDFFile.objects.get_or_create(user=user_info)

        # Set the status to in_progress
        pdf_file.status = 'in_progress'
        pdf_file.save()

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Add Persian font
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Yekan.ttf')
        print(font_path)
        pdfmetrics.registerFont(TTFont('Yekan', font_path))
        c.setFont('Yekan', 12)

        # Convert date to Jalali
        now_date = now().date()
        jalali_date = khayyam.JalaliDate.today()
        print(jalali_date)
        
        # Write user info and date
        c.drawString(100, 750, rtl(f"نام: {user_info.first_name} {user_info.last_name})"))
        c.drawString(100, 730, rtl(f"تاریخ: {str(jalali_date)}"))

        # Draw signature image
        c.drawImage(user_info.signature.path, 100, 600, width=200, height=100)

        c.showPage()
        c.save()
        buffer.seek(0)

        pdf_file.file.save(f'{user_info.username}.pdf', ContentFile(buffer.read()))
        buffer.close()

        # Update the status to done
        pdf_file.status = 'done'
        pdf_file.save()

        return f"PDF created for {user_info.username}"
    except UserInfo.DoesNotExist:
        # Update the status to failed with error message
        if pdf_file:
            pdf_file.status = 'failed'
            pdf_file.error_message = 'User not found'
            pdf_file.save()
        return 'User not found'

    except Exception as e:
        if pdf_file:
            pdf_file.status = 'failed'
            pdf_file.error_message = str(e)
            pdf_file.save()
        return str(e)
