from .models import UsageDate
from rest_framework import serializers

class UsageDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageDate
        fields = '__all__'