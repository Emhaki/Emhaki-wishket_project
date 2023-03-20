from .models import UsageDate, BillDate
from rest_framework import serializers

class UsageDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageDate
        fields = '__all__'

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillDate
        fields = (
            'user_id',
            'year',
            'month',
        )