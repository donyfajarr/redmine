from django.db import models

# Create your models here.
class user(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=30)
    
    def __str__(self):
        return str(self.name)
class dept (models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return str(self.name)
class status (models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    def __str__(self):
        return str(self.name)
class priority(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    def __str__(self):
        return str(self.name)