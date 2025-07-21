from django.db import models

class ChannelChoices(models.TextChoices):
        IN_APP = 'IN_APP','0'
        EMAIL = 'EMAIL','1'

class StatusChoices(models.TextChoices):
    SUCCESS = 'SUCCESS','0'
    FAILED = 'FAILED','1'