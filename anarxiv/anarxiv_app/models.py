from django.db import models
import datetime
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager

# This defines a sort of handler class for the 'User' Django model below
class AccountManager(BaseUserManager):

	# This creates either a 'public' registered user with standard privalages or an 'academic' user
	# with elevated privaleges.  Users are required to provide an email address, a username and a
	# password (we can do things like password checking elsewhere).
	def create_user(self, email, username, password, isAcademic=False):

		# Make the model
		account = self.model(email=self.normalize_email(email), username=username, isAcademic=isAcademic)

		# DON'T save the password plaintext, instead let django hash+salt the password
		account.set_password(password)

 		# Save the changes to the account
		account.save()

		# Return the instance
		return account

	# This creates 'proper' admins with top-level rights
	def create_superuser(self, email, username, password, isAcademic=True):

		# Create a regular user first
		account = self.create_user(email, username, password, isAcademic)

		# Then upgrade them to super user.
		account.is_admin = True

		# Save the changes to the account
		account.save()

		# Add all sites to the staff member
		self.addAllSites(account)

		# Return the instance
		return account

# This is the actual User Django model associated with registered users
class User(AbstractBaseUser):

	# Fields
	username   = models.CharField(max_length=30)		# Equivalent to a screen name, used in correspondance
	email      = models.EmailField(unique=True)		# Required to be unique, effectively our pk for Users
	is_admin   = models.BooleanField(default=False)		# Superuser?
	isAcademic = models.BooleanField(default=False)		# Academic privaleges?

	# Record when account is created and modified
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	# Optionally expiry date if they are using a temporary password
	passwordExpiry = models.DateTimeField(null=True)

	# Overload objects using Django's internal user management
	objects = AccountManager()

	# Internal Django stuff
	USERNAME_FIELD  = 'email'
	REQUIRED_FIELDS = ['username']

	@property
	def is_superuser(self): return self.is_admin

	# Provide a convenient output for 'print staffInstance'
	def __unicode__(self): return self.email

# Each subarxiv is a model
class subArxiv(models.Model):
	region = models.TextField(null = True)

class Paper(models.Model):

	title    = models.TextField(null = True)
	abstract = models.TextField(null = True)
	journal = models.TextField(null = True)

	Inspires_no = models.CharField(max_length=100, null = True)
	arxiv_no = models.CharField(max_length=50, null = True )

	Citation_count = models.IntegerField(null = True)



# Temporary table to store the daily papers as they appear on the arxiv, they will get transfered to Paper model and wiped from here.
class newPaper(models.Model):

	title    = models.TextField(null = True)
	abstract = models.TextField(null = True)
	journal = models.TextField(null = True)

	Inspires_no = models.CharField(max_length=100, null = True)
	arxiv_no = models.CharField(max_length=50, null = True )

	# Tracks the date the paper was added to the arxiv
	# added_at = models.DateTimeField(auto_now_add=True)

	added_at = models.CharField(max_length=50, null = True)


	area = models.ManyToManyField(subArxiv)



class Author(models.Model):
	
	firstName = models.TextField(null = True)
	secondName = models.TextField(null = True)
	BAI = models.CharField(max_length = 10, null = True) # Inspires unique author id

	articles = models.ManyToManyField(Paper)   # Papers assigned to this author

	newarticles = models.ManyToManyField(newPaper)   # New daily papers assigned to this author

class Post(models.Model):

	# Can a post have no message?  Surely we would reject that at the javascript level?
	# Inspires_no = models.CharField(max_length=100, default='0')
	message = models.TextField(default="")

	# What does te first arg. here do?  Should this be done with Django's auto_now instead...
	date = models.DateTimeField('date published', default=datetime.datetime.today)
	# ...like this?
	# created_at = models.DateTimeField(auto_now_add=True)
	# updated_at = models.DateTimeField(auto_now=True)

	# Posts should be one-to-one linked with a user
	# user  = models.OneToOneField(User)

	# Posts should be many-to-one linked with a paper.  This lets you get all the post
	# associated with a paper by doing stuff like...
	#      paper.post_set.all()
	# ...to get all posts for a paper or...
	#      paper.post_set.filter(isAcademic=True)
	# ...to get only the posts from acadmic users
	paper = models.ForeignKey(Paper)

	# Can each post be up-voted/down-voted?
	upVotes = models.IntegerField(default=0)
	dnVotes = models.IntegerField(default=0)

	# Syntactic sugar methods
	# What is the net 'scote'for this post?
	@property
	def votes(self): return self.upVotes - self.dnVotes

	# Was this post by an academic?
	@property
	def isAcademic(self): return self.user.isAcademic

	# What other methods should a post have?
	def delete(self): pass
	def reply (self): pass
	def censor(self): pass

















