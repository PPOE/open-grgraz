from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework import mixins, generics
from api.models import *
from api.serializers import *

# Create your views here.


class JsonResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JsonResponse, self).__init__(content, **kwargs)


def index(request):
    return HttpResponse('Hello API World!')


class GroupList(generics.ListAPIView):
    serializer_class = ParliamentaryGroupSerializer
    queryset = ParliamentaryGroup.objects.all()


class GroupDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    serializer_class = ParliamentaryGroupSerializer
    queryset = ParliamentaryGroup.objects.all()
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class SessionList(generics.ListAPIView):
    serializer_class = ParliamentarySessionSerializer
    queryset = ParliamentarySession.objects.all()


class PersonList(generics.ListAPIView):
    serializer_class = CouncilPersonSerializer

    def get_queryset(self):
        queryset = CouncilPerson.objects.all()
        group = self.request.query_params.get('group', None)
        if group is not None:
            queryset = queryset.filter(parliamentary_group__id=group)
        return queryset


class FileList(generics.ListAPIView):
    serializer_class = FileSerializer
    queryset = File.objects.all()


class AnswerList(generics.ListAPIView):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        queryset = Motion.objects.all()
        session = self.request.query_params.get('session', None)
        group = self.request.query_params.get('group', None)
        proposer = self.request.query_params.get('proposer', None)
        if session is not None:
            queryset = queryset.filter(session__session_date=session)
        if group is not None:
            queryset = queryset.filter(parliamentary_group__id=group)
        if proposer is not None:
            queryset = queryset.filter(proposer__name=proposer)
        return queryset


class MotionList(generics.ListAPIView):
    serializer_class = MotionSerializer

    def get_queryset(self):
        queryset = Motion.objects.all()
        session = self.request.query_params.get('session', None)
        type = self.request.query_params.get('type', None)
        group = self.request.query_params.get('group', None)
        proposer = self.request.query_params.get('proposer', None)
        if session is not None:
            queryset = queryset.filter(session__session_date=session)
        if type is not None:
            queryset = queryset.filter(motion_type__name=type)
        if group is not None:
            queryset = queryset.filter(parliamentary_group__id=group)
        if proposer is not None:
            queryset = queryset.filter(proposer__name=proposer)
        return queryset

