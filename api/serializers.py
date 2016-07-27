from rest_framework import serializers
from api.models import *

class ParliamentaryGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParliamentaryGroup
        fields = ('id', 'name')
