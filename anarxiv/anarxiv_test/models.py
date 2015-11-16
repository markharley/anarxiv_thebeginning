from django.db import models

# Create your models here.

class Client(models.Model):

	# Fields
	name      = models.CharField(max_length=20, unique=True)

