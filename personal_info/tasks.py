#! coding: utf-8

import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.timezone import now

from celery import shared_task
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from rtl import rtl
import khayyam

from .models import UserInfo, PDFFile

@shared_task
def create_pdf(user_id):
    try:
        user_info = UserInfo.objects.get(id=user_id)
        pdf_file, _ = PDFFile.objects.get_or_create(user=user_info)

        # Set the status to in_progress
        pdf_file.status = 'in_progress'
        pdf_file.save()

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Add Persian font
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Yekan.ttf')
        pdfmetrics.registerFont(TTFont('Yekan', font_path))
        c.setFont('Yekan', 12)

        # Convert date to Jalali
        jalali_date = khayyam.JalaliDate.today()
        
        # Write user info and date
        c.drawString(100, 750, rtl(f"نام: {user_info.first_name} {user_info.last_name}"))
        c.drawString(100, 730, rtl(f"تاریخ: {str(jalali_date)}"))

        # Draw signature image
        c.drawImage(user_info.signature.path, 100, 600, width=200, height=100)

        c.showPage()
        c.save()
        buffer.seek(0)

        pdf_file.file.save(f'{user_info.username}.pdf', ContentFile(buffer.read()))
        buffer.close()

        # Update the status to done
        return validate_pdf(user_id)
    except UserInfo.DoesNotExist:
        if pdf_file:
            pdf_file.status = 'failed'
            pdf_file.error_message = 'User not found'
            pdf_file.save()
    except Exception as e:
        if pdf_file:
            pdf_file.status = 'failed'
            pdf_file.error_message = str(e)
            pdf_file.save()

@shared_task
def validate_pdf(user_id):
    from .models import PDFFile  # Import inside the function to avoid circular import
    import pdfplumber
    from rtl import rtl
    import khayyam

    try:
        user_info = UserInfo.objects.get(id=user_id)
        pdf_file = PDFFile.objects.get(user=user_info)
        pdf_file.file.open('rb')
        with pdfplumber.open(pdf_file.file) as pdf:
            content = ""
            for page in pdf.pages:
                content += page.extract_text()
                # Checking image in pdf
                images = page.images
                if images:
                    content += "image_found"
        
        jalali_date = khayyam.JalaliDate.today()
        expected_name = rtl(f"نام: {user_info.first_name} {user_info.last_name}")
        expected_date = rtl(f"تاریخ: {str(jalali_date)}")
        
        if expected_name in content and expected_date in content and "image_found" in content:
            pdf_file.status = 'done'
            pdf_file.save()
            return True
        else:
            pdf_file.status = 'failed'
            pdf_file.error_message = 'Content verification failed'
            pdf_file.save()
            return False
    except UserInfo.DoesNotExist:
        if pdf_file:
            pdf_file.status = 'failed'
            pdf_file.error_message = 'User not found'
            pdf_file.save()
        return False
    except Exception as e:
        if pdf_file:
            pdf_file.status = 'failed'
            pdf_file.error_message = str(e)
            pdf_file.save()
        return False
    finally:
        pdf_file.file.close()
