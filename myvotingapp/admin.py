from django.contrib import admin
from .models import Student, Election, Contestant, Position#, Vote

# Register your models here.
admin.site.register(Student)
admin.site.register(Election)
admin.site.register(Position)
admin.site.register(Contestant)