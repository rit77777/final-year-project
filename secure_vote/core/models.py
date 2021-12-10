from django.db import models
from django.contrib.auth.models import AbstractUser



class UniqueID(models.Model):
    unique_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=200,)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10, unique=True)
    age = models.IntegerField()
    address = models.CharField(max_length = 100)
    pincode = models.CharField(max_length = 6)
    country = models.CharField(max_length = 100)
    city = models.CharField(max_length = 100)
    state = models.CharField(max_length = 100)
    
    def __str__(self):
        return self.unique_id


class Candidate(models.Model):
    candidate_id = models.CharField(max_length=10, primary_key=True)
    candidate_name = models.CharField(max_length=100, null=True)
    party_name = models.CharField(max_length=100, null=True)
    party_logo = models.CharField(max_length=500, blank=True)
    candidate_pic = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.candidate_name


class RegisteredVoters(AbstractUser):
    username = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    phone = models.CharField(max_length=10, unique=True, null=True)
    age = models.IntegerField(default=0)
    vote_done = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELD = []

    def __str__(self):
        return self.username
    

