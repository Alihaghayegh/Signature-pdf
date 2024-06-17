from .models import  PDFFile
from django.http import HttpResponse



def show_pdf(request):
    user = request.user
    pdf_file = PDFFile.objects.get(user=user)
    print("show pdf 1")
    if pdf_file.status == 'done':
        pdf_file.file.open('rb')
        response = HttpResponse(pdf_file.file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{pdf_file.file.name}"'
        pdf_file.file.close()
        print("show pdf 2")
        return response
