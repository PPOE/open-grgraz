from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import generic
from django.db.models import Count
from rest_framework import mixins, generics
from api.models import *
from api.serializers import *

# Create your views here.


def index(request):
    new_motions = Motion.objects.order_by('-session', '-motion_id', '-id')[:3]
    new_answers = Motion.objects.filter(answers__gt=0).order_by('-session', '-motion_id', '-id')[:3]  #todo
    old_no_answer = Motion.objects.filter(answers__isnull=True).order_by('session', 'motion_id', 'id')[:3]

    context = {'new_motions': new_motions, 'new_answers': new_answers, 'old_no_answer': old_no_answer}
    return render(request, 'index.html', context)


def groups(request):
    groups = Motion.objects.values('parliamentary_group')\
        .annotate(motion_count=Count('id', distinct=True),
                  answered_count=Count('answers__motion_id', distinct=True))

    for group in groups:
        group['answered_percent'] = float('{:.2f}'.format((group['answered_count'] / group['motion_count']) * 100))

    groups = sorted(groups, key=lambda s: s['answered_percent'], reverse=True)

    context = {'groups': groups}
    return render(request, 'groups/index.html', context)


def council_persons(request):
    #todo: fix duplicates
    council_persons = Motion.objects.values('proposer', 'parliamentary_group')\
        .annotate(motion_count=Count('id', distinct=True),
                  answered_count=Count('answers__motion_id', distinct=True))

    for person in council_persons:
        person['answered_percent'] = float('{:.2f}'.format((person['answered_count'] / person['motion_count']) * 100))

    council_persons = sorted(council_persons, key=lambda s: s['answered_percent'], reverse=True)

    return render(request, 'council_persons/index.html', {'council_persons': council_persons})


class MotionsList(generic.ListView):
    template_name = 'motions/list.html'
    context_object_name = 'motions'

    def get_queryset(self):
        queryset = Motion.objects.order_by('-session', '-motion_id', '-id')
        # todo: order_by, filter answered, pagination, search
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
    answered_stats = Motion.objects.values('parliamentary_group')\
        .annotate(num_total=Count('id', distinct=True),
                  num_answered=Count('answers__motion_id', distinct=True))\
        .order_by('-num_total')

    for stat in answered_stats:
        stat['answered_percent'] = float('{:.2f}'.format((stat['num_answered'] / stat['num_total']) * 100))

    answered_stats = sorted(answered_stats, key=lambda s: s['answered_percent'], reverse=True)

    return HttpResponse(answered_stats)


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

