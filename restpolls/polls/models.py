from django.db import models
import datetime
from django.utils import timezone
# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=250)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return str(self.id)+': '+self.question_text[0:10]

class Choice(models.Model):
    rel_id = models.IntegerField()
    question = models.ForeignKey(Question, related_name='choices' ,on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=250)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)+': '+self.choice_text[0:10]

    def was_published_recently(self):
        return self.pub_date >= timezone.now()-datetime.timedelta(days=1)