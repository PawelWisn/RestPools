from django.db.models import F
from django.shortcuts import render, get_object_or_404
from .models import *
from .serializers import *
from django.http import JsonResponse, HttpResponse
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ParseError

# Create your views here.
def homepage(request):
    return render(request, 'polls/homepage.html')


@csrf_exempt
def question_list(request):
    if request.method == "GET":
        q_list = Question.objects.all()
        serializer = QuestionChoiceSerializer(q_list, many=1).data
        return JsonResponse(serializer, safe=0)

    elif request.method == "POST":
        parsed = JSONParser().parse(request)
        serializer = QuestionChoiceSerializer(data=parsed)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def question_detail(request, q_pk):
    question = get_object_or_404(Question, pk=q_pk)

    if request.method == "GET":
        serializer = QuestionChoiceSerializer(question, many=0)
        return JsonResponse(serializer.data, safe=0)

    elif request.method == "POST":
        data = JSONParser().parse(request)

        if Choice.objects.filter(question=question, rel_id=data.get('rel_id')).first():
            return JsonResponse({'message': 'rel_id is taken. Use different one or use PUT to update'}, status=400)

        data['question'] = question.id
        serializer = ChoiceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = QuestionChoiceSerializer(question, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == "DELETE":
        question.delete()
        return HttpResponse(status=204)


@csrf_exempt
def choice_detail(request, q_pk, ch_pk):
    choice = Choice.objects.filter(question=q_pk, rel_id=ch_pk).first()
    if not choice:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = ChoiceSerializer(choice, many=0)
        return JsonResponse(serializer.data, safe=0)

    elif request.method == "PUT":
        try:
            data = JSONParser().parse(request)
        except ParseError:
            return JsonResponse({'message':'Request contains malformed data '},status=400)

        serializer = ChoiceSerializer(choice, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == "DELETE":
        choice.delete()
        return HttpResponse(status=204)


@csrf_exempt
def vote(request, q_pk, ch_pk):
    choice = Choice.objects.filter(question=q_pk, rel_id=ch_pk).first()

    if not choice:
        return HttpResponse(status=404)

    if request.method == "PUT":
        choice.votes = F('votes')+1
        choice.save()
        choice.refresh_from_db()
        return JsonResponse(ChoiceSerializer(choice).data)
