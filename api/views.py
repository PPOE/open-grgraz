from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import generic
from django.db.models import Count
from rest_framework import mixins, generics
from api.models import *
from api.serializers import *

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'motions/index.html'
    context_object_name = 'motions'

    def get_queryset(self):
        queryset = Motion.objects.order_by('-session', '-motion_id', '-id')
        session = self.request.GET.get('session', None)
        type = self.request.GET.get('type', None)
        group = self.request.GET.get('group', None)
        proposer = self.request.GET.get('proposer', None)
        if session is not None:
            queryset = queryset.filter(session__session_date=session)
        if type is not None:
            queryset = queryset.filter(motion_type=type)
        if group is not None:
            queryset = queryset.filter(parliamentary_group__id=group)
        if proposer is not None:
            queryset = queryset.filter(proposer__name=proposer)
        return queryset


def motion_detail(request, id):
    motion = get_object_or_404(Motion, id=id)
    return render(request, 'motions/detail.html', {'motion': motion})


def motion_stats(request):
    stats = Motion.objects.values('parliamentary_group')\
        .annotate(num_total=Count('id', distinct=True),
                  num_answered=Count('answers__motion_id', distinct=True))\
        .order_by('-num_total')

    for stat in stats:
        stat['answered_percent'] = '{:.2f}'.format((stat['num_answered'] / stat['num_total']) * 100)

    stats = sorted(stats, key=lambda s: s['answered_percent'], reverse=True)

    return HttpResponse(stats)


def api_index(request):
    return HttpResponse('Hello API World!')


class ApiGroupList(generics.ListAPIView):
    serializer_class = ParliamentaryGroupSerializer
    queryset = ParliamentaryGroup.objects.all()


class ApiGroupDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    serializer_class = ParliamentaryGroupSerializer
    queryset = ParliamentaryGroup.objects.all()
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ApiSessionList(generics.ListAPIView):
    serializer_class = ParliamentarySessionSerializer
    queryset = ParliamentarySession.objects.all()


class ApiPersonList(generics.ListAPIView):
    serializer_class = CouncilPersonSerializer

    def get_queryset(self):
        queryset = CouncilPerson.objects.all()
        group = self.request.query_params.get('group', None)
        if group is not None:
            queryset = queryset.filter(parliamentary_group__id=group)
        return queryset


class ApiFileList(generics.ListAPIView):
    serializer_class = FileSerializer
    queryset = File.objects.all()


class ApiAnswerList(generics.ListAPIView):
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


class ApiMotionList(generics.ListAPIView):
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
            queryset = queryset.filter(motion_type=type)
        if group is not None:
            queryset = queryset.filter(parliamentary_group__id=group)
        if proposer is not None:
            queryset = queryset.filter(proposer__name=proposer)
        return queryset

