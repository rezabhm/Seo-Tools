from django.db import models
from django.utils import timezone

from apps.core.models import CustomUser, BaseModel


# Create your models here.
class SubscriptionPlan(BaseModel):

    price = models.IntegerField(default=0)

    keyword_limit = models.IntegerField()
    labeling_status = models.BooleanField()
    chatGPT_status = models.BooleanField()
    free_status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.price)


class Features(BaseModel):

    description = models.TextField()
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)

    def __str__(self):
        return self.description


class Subscription(BaseModel):

    buy_time = models.DateTimeField(default=timezone.now)
    expire_time = models.DateTimeField(default=timezone.now)

    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, null=True)

    keyword_extracted = models.IntegerField(default=0)
    keyword_extracted_percent = models.FloatField(default=0.0)

    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.buy_time}'


class Transaction(BaseModel):

    """this class is for paypal online payment transaction for user after pay subscription on paypal will store transaction information and hanlde paypal payment transaction proccess"""