from rest_framework import serializers
from .models import StudentProfile, ParentDetail, AcademicHistory

class StudentProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    class Meta:
        model = StudentProfile
        fields = '__all__'

class ParentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentDetail
        fields = '__all__'

class AcademicHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicHistory
        fields = '__all__'
