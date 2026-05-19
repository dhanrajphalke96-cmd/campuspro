from rest_framework import serializers
from .models import AdmissionApplication, AdmissionDocument, MeritList, AdmissionFeePayment

class AdmissionApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionApplication
        fields = '__all__'

class AdmissionDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionDocument
        fields = '__all__'

class MeritListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeritList
        fields = '__all__'

class AdmissionFeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionFeePayment
        fields = '__all__'
