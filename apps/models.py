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
class settings(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    gannt_start_column = models.IntegerField(default='9')
    week_number_row = models.IntegerField(default='4')
    start_row = models.IntegerField(default='5')
    start_column = models.IntegerField(default='2')
    end_column = models.IntegerField(default='6')
    pic_column = models.IntegerField(default='8')
    email_column = models.IntegerField(default='61')

    def __str__(self):
        return str(self.user)