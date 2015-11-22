from django.db import models

# Create your models here.

class Paper(models.Model):
    author = models.CharField(max_length = 30)
    title = models.CharField(max_length = 100)
    abstract = models.TextField()
    # journal_ref = models.CharField(max_length=200)
    recordID = models.CharField(max_length = 100, default = '0')
  

class Post(models.Model):
	paperID = models.CharField(max_length = 100, default = '0')
	message = models.TextField(default = "")


