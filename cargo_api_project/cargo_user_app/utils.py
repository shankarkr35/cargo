from django.core.mail import EmailMessage
import os
from django.conf  import settings
class Util:
  @staticmethod
  def send_email(data):
    print("uilss send fun call ....................................>>>>>>>>>>>>>>")
    email = EmailMessage(
      subject=data['subject'],
      body=data['body'],
      from_email=settings.EMAIL_HOST ,#os.environ.get('EMAIL_FROM'),
      to=[data['to_email']]
    )
    print("util email,,,,,,",email)
    email.send()