from rest_framework import serializers
from .models import Exam, MarksEntry, Result

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'

class MarksEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MarksEntry
        fields = '__all__'

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'
