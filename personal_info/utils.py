from .models import PDFFile
from django.http import HttpResponse


def show_pdf(user):
    '''
    This function will call if pdf file exists
    Basically it gets pdf file and sets Content-Disposition to that pdf to show in browser
    '''
    try:
        pdf_file = PDFFile.objects.get(user=user)
        if pdf_file.status == 'done':
            pdf_file.file.open('rb')
            response = HttpResponse(
                pdf_file.file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{
                pdf_file.file.name}"'
            pdf_file.file.close()
            return response
        else:
            return HttpResponse(status=404)
    except PDFFile.DoesNotExist:
        return HttpResponse(status=404)
