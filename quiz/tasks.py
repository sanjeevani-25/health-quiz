# from time import sleep
# from django.http import FileResponse, HttpResponse
# from reportlab.pdfgen import canvas
# from io import BytesIO

from __future__ import absolute_import

from celery import shared_task
from django.conf import settings
import os
from .models import *
from roles.models import *
from pathlib import Path
import datetime
from fpdf import FPDF


@shared_task
def generate_pdf2(pk):
    path = Path.cwd()
    d = datetime.datetime.now()
    output_path = f'{path}/pdoc/{d}_{pk}.txt'
    f = open(output_path, 'w')

    quiz_performance = QuizPerformance.objects.get(uid=pk)
    f.write("Quiz Details: \nQuiz Performance id : " + str(quiz_performance.uid))

    user = quiz_performance.event.user
    f.write("\nAttempted by : "+ str(user.first_name) + " "+ str(user.last_name)+ "\tUID: " +str(user.uid))

    f.write(f"\nQuestion: {quiz_performance.question}")

    options = Options.objects.filter(question=quiz_performance.question.uid)
    i=1
    correct_option=None
    for option in options:
        f.write(f"\n{i}. {option}")
        if option.is_correct:
            correct_option = option
        i+=1
    f.write(f"\nYour Answer: {quiz_performance.user_answer}")
    f.write(f"\nCorrect Answer: {correct_option}")
    f.close()

    pdf = FPDF()

    # Open the text file and read its contents
    with open(output_path, 'r') as f:
        text = f.read()

    # Add a new page to the PDF
    pdf.add_page()

    # Set the font and font size
    pdf.set_font('Arial', size=12)

    # Write the text to the PDF
    pdf.write(5, text)

    # Save the PDF
    pdf.output(f'{path}/pdoc/{d}_{pk}.pdf')
    os.remove(output_path)



@shared_task(name='create_event_task')
def create_event(doc_id, user_id, quiz_id, is_cancelled=False):
    user = User.objects.get(uid=user_id)
    doctor = User.objects.get(uid=doc_id)
    quiz = Quiz.objects.get(uid=quiz_id)
    ScheduledEvent.objects.create(doctor=doctor, user=user, quiz=quiz, is_cancelled = is_cancelled)
    print("created event")


# from django_celery_beat.models import PeriodicTask, IntervalSchedule , CrontabSchedule
# import json

# schedule , created = IntervalSchedule.objects.get_or_create( every = 20, period=IntervalSchedule.SECONDS)

# schedule1, created = CrontabSchedule.objects.get_or_create(minute='26',hour='*',day_of_week='*',day_of_month='*',month_of_year='*')
# PeriodicTask.objects.get_or_create(
#     name='sched task 5',
#     task = 'create_event_task',
#     interval = schedule,
#     args=json.dumps(["f3a8d7b25d894bfabf02463a0051cba2", 'f83384ccf2764b34b8c91ac19ea3eb3d','f1953f3519ab47548e8e6ed98fef7568', False])
# )

# PeriodicTask.objects.get_or_create(
#     name='sched task 6',
#     task = 'create_event_task',
#     crontab = schedule1,
#     args=json.dumps(["f3a8d7b25d894bfabf02463a0051cba2", 'f83384ccf2764b34b8c91ac19ea3eb3d','f1953f3519ab47548e8e6ed98fef7568', False])
# )










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

# @shared_task
# def generate_pdf_file(pk):
#     buffer = generate_pdf(pk)
#     d = datetime.datetime.now()

#     path2 = Path.cwd()
#     output_path = f'{path2}/pdoc/{d}_{pk}.pdf'
#     pdf = buffer.getvalue()
#     # FileResponse(buffer, as_attachment=True, filename=output_path)
#     buffer.close()
#     print(output_path)
#     with open(output_path, 'wb') as f:
#         f.write(pdf)
#     # buffer.close()
#     f.close()

# def generate_pdf(pk):

#     # response = HttpResponse(content_type='application/pdf')
#     # response['Content-Disposition'] = f'attachment; filename="{pk}.pdf'
#     sleep(2)
#     buffer = BytesIO()
#     p = canvas.Canvas(buffer)

#     quiz_performance = QuizPerformance.objects.get(uid=pk)
#     print(quiz_performance)
#     y = 750
#     p.drawString(100, y, "Quiz Performance of User")

#     user = quiz_performance.event.user
#     p.drawString(100, y-40, f"User --> {user}")
#     p.drawString(100, y-50, f"Question --> {quiz_performance.question}")
    
#     options = Options.objects.filter(question=quiz_performance.question.uid)
#     correct_option = None
#     yvar = 70
#     i = 1
#     for option in options:
#         p.drawString(100, y-yvar, f"{i}. {option}")
#         if option.is_correct:
#             correct_option = option
#         i += 1
#         yvar += 10

#     p.drawString(100, y-120, f"Your answer: {quiz_performance.user_answer}")
#     p.drawString(100, y-130, f"Correct answer: {correct_option}")
#     p.showPage()
#     p.save()
    
#     buffer.seek(0)
#     return buffer