from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Election(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()

    @property
    def is_active(self):
        current_date = timezone.now().date()
        return self.start_date <= current_date <= self.end_date

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    profile_pic = models.ImageField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    voted_elections = models.ManyToManyField(Election, related_name='voted_students', blank=True)

    def __str__(self):
        return self.name
    
    @property
    def imageURL(self):
        try:
            url = self.profile_pic.url
        except:
            url = ''
        return url

class Position(models.Model):
    name = models.CharField(max_length=100, unique=True)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Contestant(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True)
    total_vote = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.student.name} for {self.position} in {self.election}"
