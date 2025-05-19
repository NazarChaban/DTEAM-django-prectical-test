from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class CV(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    skills = models.ManyToManyField(Skill, blank=True)
    bio = models.TextField(blank=True)
    contacts = models.JSONField(blank=True, null=True) # Stores contact information like email, phone, LinkedIn, etc.

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

    class Meta:
        verbose_name_plural = "CVs"


class Project(models.Model):
    cv = models.ForeignKey(
        CV, on_delete=models.CASCADE, related_name='projects'
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
