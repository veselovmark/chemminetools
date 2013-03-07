import os
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from runapp import launch
DATETIME_FORMAT = settings.DATETIME_FORMAT

class ApplicationCategories(models.Model):
	name = models.CharField(max_length=250, unique=True)

	def __unicode__(self):
		return self.name

class Application(models.Model):
	name = models.CharField(max_length=250, unique=True)
	category = models.ForeignKey(ApplicationCategories)
	script = models.CharField(max_length=250, unique=True)
	input_type = models.CharField(max_length=250)
	output_type = models.CharField(max_length=250)
	description = models.TextField()

	def __unicode__(self):
		return self.name

class ApplicationOptions(models.Model):
	name = models.CharField(max_length=255)
	realName = models.CharField(max_length=255)
	application = models.ForeignKey(Application)

	def __unicode__(self):
		return self.application.name + "_" + self.name

class ApplicationOptionsList(models.Model):
	category = models.ForeignKey(ApplicationOptions)
	name = models.CharField(max_length=255)
	realName = models.CharField(max_length=255)

	def __unicode__(self):
		return self.name

class Job(models.Model):
	RUNNING, FINISHED, FAILED = 0, 1, 2
	STATUS_CHOICES = (
		(RUNNING, 'Running'),
		(FINISHED, 'Finished'),
		(FAILED, 'Failed'),
	)
	user = models.ForeignKey(User, db_index=True)
	application = models.ForeignKey(Application)
	start_time = models.DateTimeField(auto_now_add=True)
	status = models.SmallIntegerField(default=RUNNING, choices=STATUS_CHOICES)
	options = models.CharField(max_length=1000)
	input = models.CharField(max_length=1000)
	output = models.CharField(max_length=1000)
	task_id = models.CharField(max_length=255)

	def delete(self, *args, **kwargs):
		if isinstance(self.output, unicode):
			if os.path.isfile(self.output):
				os.remove(self.output)
		try:
			result = launch.AsyncResult(self.task_id)
			result.forget()
		except:
			pass
		super(Job, self).delete()

	def __unicode__(self):
		return self.application.name + " " + self.start_time.strftime(DATETIME_FORMAT)

