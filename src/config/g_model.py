from django.db import models


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.IntegerField(primary_key=True, editable=False)

    class Meta:
        abstract = True

