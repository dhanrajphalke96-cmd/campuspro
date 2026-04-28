from rest_framework import serializers
from .models import FeeStructure, FeePayment, Scholarship

class FeeStructureSerializer(serializers.ModelSerializer):
    total_fee = serializers.ReadOnlyField()
    class Meta:
        model = FeeStructure
        fields = '__all__'

class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePayment
        fields = '__all__'

class ScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholarship
        fields = '__all__'
