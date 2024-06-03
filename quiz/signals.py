from django.db.models.signals import post_save , pre_save
from django.dispatch import receiver
from .models import *
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

@receiver(post_save, sender=ScheduledEvent)
def event_created_notification_mail(sender, instance, created, **kwargs):
    if created:
        print("postsave signal")
        print("sender " ,sender)
        print("instance "   ,instance)
        print(f"kwargs {kwargs}")

        subject = f'Event scheduled'

        text_message = f'Hello {instance.doctor.first_name},\nThank you for Registering.\nThis mail is autogenerated. Do not reply to this mail.\nRegards,\nHealthquiz Team.'
        html_content = f"<p>Hello {instance.doctor.first_name},<br>Thank you for Registering Event {instance.uid}.<br>This mail is autogenerated. Do not reply to this mail.<br>Regards,<br>Healthquiz Team.</p>"
        from_email = settings.EMAIL_HOST_USER
        to = instance.doctor.email
        print("to email ",to)

        msg = EmailMultiAlternatives(subject, text_message, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        # msg.content_subtype = "text/plain"  # Main content is now text/html

        msg.send()
    
    else:
        print("signal : event not created")


@receiver(post_save, sender=QuizPerformance)
def event_created_notification_mail(sender, instance, created, **kwargs):
    if created:
        print("postsave signal")
        print("sender " ,sender)
        print("instance "   ,instance)
        print(f"kwargs {kwargs}")

        subject = f'Quiz performance test'

        text_message = f'Hello {instance.event.doctor.first_name},\nThank you for Registering.\nThis mail is autogenerated. Do not reply to this mail.\nRegards,\nHealthquiz Team.'
        html_content = f"<p>Hello {instance.event.doctor.first_name},<br>Thank you for Registering.<br>This mail is autogenerated. Do not reply to this mail.<br>Regards,<br>Healthquiz Team.</p>"
        from_email = settings.EMAIL_HOST_USER
        to = instance.event.doctor.email

        msg = EmailMultiAlternatives(subject, text_message, from_email, [to])
        msg.attach_alternative(html_content, "text/html")

        # msg.content_subtype = "text/plain"  # Main content is now text/html

        msg.send()
    
    else:
        print("signal : event not created")


