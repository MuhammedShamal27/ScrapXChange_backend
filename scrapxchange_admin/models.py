from django.db import models
from user.models import CustomUser

# Create your models here.

class Report(models.Model):
    REASONS = [
        ('fraud', 'Fraud'),
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('other', 'Other'),
    ]
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reports_sent')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.CharField(max_length=20,choices=REASONS)
    description = models.TextField(blank=True)
    is_checked = models.BooleanField(default=False,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Report from {self.sender.username} to {self.receiver.username} on {self.timestamp}"