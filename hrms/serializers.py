from rest_framework import serializers
from .models import StaffProfile, LeaveRequest, StaffAttendance

class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = '__all__'

class LeaveRequestSerializer(serializers.ModelSerializer):
    days = serializers.ReadOnlyField()
    class Meta:
        model = LeaveRequest
        fields = '__all__'

class StaffAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffAttendance
        fields = '__all__'
