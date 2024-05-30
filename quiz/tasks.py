from time import sleep
from celery import shared_task
from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from django.conf import settings
import os
from .models import QuizPerformance, Options
from pathlib import Path
import datetime

@shared_task
def generate_pdf_file(pk):
    buffer = generate_pdf(pk)
    d = datetime.datetime.now()

    path2 = Path.cwd()
    output_path = f'{path2}/pdoc/{d}_{pk}.pdf'
    pdf = buffer.getvalue()
    # FileResponse(buffer, as_attachment=True, filename=output_path)
    buffer.close()
    print(output_path)
    with open(output_path, 'wb') as f:
        f.write(pdf)
    # buffer.close()
    f.close()

def generate_pdf(pk):

    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = f'attachment; filename="{pk}.pdf'
    sleep(2)
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    quiz_performance = QuizPerformance.objects.get(uid=pk)
    print(quiz_performance)
    y = 750
    p.drawString(100, y, "Quiz Performance of User")

    user = quiz_performance.event.user
    p.drawString(100, y-40, f"User --> {user}")
    p.drawString(100, y-50, f"Question --> {quiz_performance.question}")
    
    options = Options.objects.filter(question=quiz_performance.question.uid)
    correct_option = None
    yvar = 70
    i = 1
    for option in options:
        p.drawString(100, y-yvar, f"{i}. {option}")
        if option.is_correct:
            correct_option = option
        i += 1
        yvar += 10

    p.drawString(100, y-120, f"Your answer: {quiz_performance.user_answer}")
    p.drawString(100, y-130, f"Correct answer: {correct_option}")
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer



# def generate_pdf(request):
#     response = FileResponse(generate_pdf_file(), 
#                             as_attachment=True, 
#                             filename='book_catalog.pdf')
#     return response
 
 
# def generate_pdf_file():
#     from io import BytesIO
 
#     buffer = BytesIO()
#     p = canvas.Canvas(buffer)
 
#     # Create a PDF document
#     books = Book.objects.all()
#     p.drawString(100, 750, "Book Catalog")
 
#     y = 700
#     for book in books:
#         p.drawString(100, y, f"Title: {book.title}")
#         p.drawString(100, y - 20, f"Author: {book.author}")
#         p.drawString(100, y - 40, f"Year: {book.publication_year}")
#         y -= 60
 
#     p.showPage()
#     p.save()
 
#     buffer.seek(0)
#     return buffer


### Command for starting a celery
#  celery -A chime_games worker --loglevel=INFO
### Command for windows 
#  celery -A chime_games worker --loglevel=INFO -P eventlet