# buin/models.py
from django.db import models

class MentalHealthAssessmentFact(models.Model):
    survey_id = models.IntegerField()
    student_id = models.IntegerField()
    mental_health_id = models.IntegerField()
    study_satisfaction = models.IntegerField()
    academic_workload = models.IntegerField()
    academic_pressure = models.IntegerField()
    financial_concerns = models.IntegerField()

    def __str__(self):
        return f"Survey {self.survey_id} - Student {self.student_id}"

class MentalHealthDimension(models.Model):
    mental_health_id = models.IntegerField(primary_key=True)
    depression_level = models.IntegerField()
    anxiety_level = models.IntegerField()
    isolation_level = models.IntegerField()
    social_relationships_level = models.IntegerField()

    def __str__(self):
        return f"Mental Health ID {self.mental_health_id}"

class DemographicsDimension(models.Model):
    student_id = models.IntegerField(primary_key=True)
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    university = models.CharField(max_length=100)
    degree_level = models.CharField(max_length=100)

    def __str__(self):
        return f"Student ID {self.student_id}"

class PositiveEngagementDimension(models.Model):
    positive_engagement_id = models.IntegerField(primary_key=True)
    sports_engagement = models.TextField()
    study_satisfaction = models.IntegerField()

    def __str__(self):
        return f"Positive Engagement ID {self.positive_engagement_id}"

class NegativeEngagementDimension(models.Model):
    negative_engagement_id = models.IntegerField(primary_key=True)
    academic_pressure = models.IntegerField()
    academic_workload = models.IntegerField()
    financial_concerns = models.IntegerField()

    def __str__(self):
        return f"Negative Engagement ID {self.negative_engagement_id}"
