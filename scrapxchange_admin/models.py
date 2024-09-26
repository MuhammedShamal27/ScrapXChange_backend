from django.db import models
from user.models import CustomUser

# Create your models here.

class Report(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reports_sent')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.TextField()
    is_checked = models.BooleanField(default=False,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Report from {self.sender.username} to {self.receiver.username} on {self.timestamp}"