from django.db import models

# Create your models here.

class Candidate(models.Model):
    candidate_id = models.CharField(max_length=10, primary_key=True)
    candidate_name = models.CharField(max_length=100)

    def __str__(self):
        return self.candidate_name
