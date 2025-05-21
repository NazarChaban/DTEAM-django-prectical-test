from rest_framework import serializers
from ..models import Skill, CV, Project


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'link']
        read_only_fields = ('cv',)


class CVSerializer(serializers.ModelSerializer):
    skills = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        many=True,
        required=False
    )
    projects = ProjectSerializer(many=True, required=False)

    class Meta:
        model = CV
        fields = [
            'id', 'firstname', 'lastname',
            'skills', 'bio', 'contacts', 'projects'
        ]

    def create(self, validated_data):
        skills_data = validated_data.pop('skills', [])
        projects_data = validated_data.pop('projects', [])

        cv = CV.objects.create(**validated_data)
        cv.skills.set(skills_data)

        for project_data in projects_data:
            Project.objects.create(cv=cv, **project_data)
        return cv

    def update(self, instance, validated_data):
        skills_data = validated_data.pop('skills', None)
        projects_data = validated_data.pop('projects', None)

        instance.firstname = validated_data.get(
            'firstname', instance.firstname
        )
        instance.lastname = validated_data.get('lastname', instance.lastname)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.contacts = validated_data.get('contacts', instance.contacts)
        instance.save()

        if skills_data is not None:
            instance.skills.set(skills_data)

        if projects_data is not None:
            instance.projects.all().delete()
            for project_data in projects_data:
                Project.objects.create(cv=instance, **project_data)

        return instance
