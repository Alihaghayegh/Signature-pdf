<<<<<<< HEAD
#! coding: utf-8

=======
# #! coding: utf-8

import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.timezone import now
>>>>>>> dev
from celery import shared_task
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
<<<<<<< HEAD
from django.core.files.base import ContentFile
from django.utils.timezone import now
import khayyam
from rtl import rtl
from .models import UserInfo, PDFFile
from io import BytesIO
import os
=======
from rtl import rtl
import khayyam
import pdfplumber
from .models import UserInfo, PDFFile
import redis

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
>>>>>>> dev

@shared_task
def create_pdf(user_id):
    try:
        user_info = UserInfo.objects.get(id=user_id)
        pdf_file, created = PDFFile.objects.get_or_create(user=user_info)

        # Set the status to in_progress
        pdf_file.status = 'in_progress'
        pdf_file.save()
<<<<<<< HEAD
=======
        redis_client.set(f'pdf_status_{user_id}', 'in_progress')

>>>>>>> dev

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Add Persian font
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Yekan.ttf')
<<<<<<< HEAD
        print(font_path)
=======
>>>>>>> dev
        pdfmetrics.registerFont(TTFont('Yekan', font_path))
        c.setFont('Yekan', 12)

        # Convert date to Jalali
<<<<<<< HEAD
        now_date = now().date()
        jalali_date = khayyam.JalaliDate.today()
        print(jalali_date)
=======
        jalali_date = khayyam.JalaliDate.today()
>>>>>>> dev
        
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

<<<<<<< HEAD
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
=======
        # Call validation task
        validate_pdf.delay(user_info.id)
    except UserInfo.DoesNotExist:
        redis_client.set(f'pdf_status_{user_id}', 'failed')
    except Exception as e:
        redis_client.set(f'pdf_status_{user_id}', 'failed')

@shared_task
def validate_pdf(user_id):
    count_of_fails = 0
    user_info = UserInfo.objects.get(id=user_id)
    pdf_file = PDFFile.objects.get(user=user_info)
    try:
        user_info = UserInfo.objects.get(id=user_id)
        pdf_file = PDFFile.objects.get(user=user_info)
        pdf_file.file.open('rb')

        with pdfplumber.open(pdf_file.file) as pdf:
            content = ""
            for page in pdf.pages:
                content += page.extract_text()
 
        jalali_date = khayyam.JalaliDate.today()
        expected_name = rtl(f"نام: {user_info.first_name} {user_info.last_name}")
        expected_date = rtl(f"تاریخ: {str(jalali_date)}")
        images = page.images
        if images:
            content += "image_found"

        if expected_name in content and expected_date in content and "image_found" in content:
            pdf_file.status = 'verified'
            redis_client.set(f'pdf_status_{user_id}', 'verified')
            redis_client.set('count_of_fails', f'{count_of_fails}')
            pdf_file.save()
        else:
            fails = redis_client.get('count_of_fails')
            while fails < 5 :
                count_of_fails += 1
                redis_client.set('count_of_fails', f'{count_of_fails}')
                create_pdf.delay(user_info.id)
            pdf_file.status = 'failed'
            pdf_file.error_message = 'Content verification failed'
            pdf_file.save()
            redis_client.set(f'pdf_status_{user_id}', 'failed')

    except Exception as e:
        pdf_file.status = 'failed'
        pdf_file.error_message = str(e)
        pdf_file.save()
        redis_client.set(f'pdf_status_{user_id}', 'failed')
>>>>>>> dev
