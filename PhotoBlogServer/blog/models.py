from django.conf import settings
from django.db import models
from django.utils import timezone

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

class CongestionData(models.Model):
    person_count = models.IntegerField()
    congestion_level = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    coordinates = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.timestamp}: {self.congestion_level} ({self.person_count}명)"