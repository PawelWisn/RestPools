from rest_framework import serializers
from .models import *
from django.utils import timezone


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['rel_id', 'question', 'choice_text', 'votes']
        extra_kwargs = {'question': {'required': False}, 'rel_id': {
            'required': False}, 'votes': {'required': False}}

    def create(self, validated_data):
        choices = Choice.objects.filter(
            question=validated_data.get('question'))
        if len(choices) == 0:
            rel_id_candidate = 0
        else:
            rel_id_candidate = sorted(
                choices, key=lambda x: x.rel_id)[-1].rel_id+1

        question = validated_data.get('question')
        choice_text = validated_data.get('choice_text')
        rel_id = validated_data.get('rel_id', rel_id_candidate)
        choice = Choice(question=question,
                        choice_text=choice_text, rel_id=rel_id)
        choice.save()
        return choice


class QuestionChoiceSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=1)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'pub_date', 'choices']
        extra_kwargs = {'pub_date': {'required': False}}

    def create(self, validated_data):
        choice_list = validated_data.pop('choices')

        pub_date = validated_data.get('pub_date', timezone.now())
        q = Question.objects.create(pub_date=pub_date, **validated_data)

        for idx, choice in enumerate(choice_list):
            Choice.objects.create(question=q, rel_id=idx, **choice)

        return q

    def update(self, instance, validated_data):
        choice_list = validated_data.pop('choices')

        instance.pub_date = validated_data.get('pub_date', instance.pub_date)
        instance.question_text = validated_data.get(
            'question_text', instance.question_text)

        instance.save()

        for choice in choice_list:
            ch = Choice.objects.filter(
                question=instance, rel_id=choice.get('rel_id')).first()
            
            if ch:
                ch.choice_text = choice.get('choice_text', ch.choice_text)
            else:
                choices = Choice.objects.filter(question=instance)
                if len(choices) == 0:
                    rel_id = 0
                else:
                    rel_id = sorted(
                        choices, key=lambda x: x.rel_id)[-1].rel_id+1
                ch = Choice(
                    choice_text=choice['choice_text'], question=instance, rel_id=rel_id)
            
            ch.save()

        return instance
