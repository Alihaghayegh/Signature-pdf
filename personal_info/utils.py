from django.http import HttpResponse
from .models import PDFFile

def show_pdf(user):
    try:
        pdf_file = PDFFile.objects.get(user=user)
        if pdf_file.status == 'verified':
            pdf_file.file.open('rb')
            response = HttpResponse(pdf_file.file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{pdf_file.file.name}"'
            pdf_file.file.close()
            return response
        else:
            return None
    except PDFFile.DoesNotExist:
        return None
