from rest_framework import serializers

from .models import Job, Company


class CompanySerializer(serializers.ModelSerializer):
    #job = serializers.StringRelatedField(many=True)
    jobs = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Job.objects.all())


    class Meta:
        model = Company
        fields ="__all__"


class JobSerializer(serializers.ModelSerializer):
    #company = CompanySerializer(many=False, read_only=True)
    #company_name = serializers.StringRelatedField()
    class Meta:
        model = Job
        fields = "__all__" #('name', 'country', 'city')