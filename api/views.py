from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.views import generic
from django.db.models import Count
from rest_framework import mixins, generics
from api.models import *
from api.serializers import *
from datetime import datetime, timedelta
import json

# Create your views here.


def index(request):
    new_motions = Motion.objects.order_by('-session__session_date', '-motion_id', '-id')[:6]
    new_answers = Motion.objects.filter(answers__gt=0).order_by('-answers__answered_date')[:6]  #todo
    old_no_answer = Motion.objects.filter(answers__isnull=True).order_by('session__session_date', 'motion_id', 'id')[:6]

    context = {'new_motions': new_motions, 'new_answers': new_answers, 'old_no_answer': old_no_answer}
    return render(request, 'index.html', context)


def faq(request):
    context = {}
    return render(request, 'faq.html', context)


def groups(request):
    groups = Motion.objects.values('parliamentary_group', 'parliamentary_group__id', 'parliamentary_group__seats')\
        .annotate(motion_count=Count('id', distinct=True),
                  answered_count=Count('answers__motion_id', distinct=True))

    for group in groups:
        group['motions_per_seat'] = float('{:.2f}'.format(group['motion_count'] / group['parliamentary_group__seats']))
        group['answered_percent'] = float('{:.2f}'.format((group['answered_count'] / group['motion_count']) * 100))

    groups = sorted(groups, key=lambda s: s['answered_percent'], reverse=True)

    context = {'groups': groups}
    return render(request, 'groups/index.html', context)


def council_persons(request):
    #todo: fix duplicates
    council_persons = Motion.objects.values('proposer', 'proposer__name', 'parliamentary_group')\
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
        queryset = Motion.objects.annotate(num_answered=Count('answers__motion_id', distinct=True))
        session = self.request.GET.get('session', '')
        type = self.request.GET.get('type', '')
        group = self.request.GET.get('group', '')
        proposer = self.request.GET.get('proposer', '')
        answered = self.request.GET.get('answered', '')
        search = self.request.GET.get('search', '')
        orderby = self.request.GET.get('orderby', '')
        if session is not '':
            queryset = queryset.filter(session__session_date=session)
        if type is not '':
            queryset = queryset.filter(motion_type=type)
        if group is not '':
            queryset = queryset.filter(parliamentary_group__id=group)
        if answered is not '':
            if answered == 'True':
                queryset = queryset.filter(num_answered__gt=0)
            elif answered == 'False':
                queryset = queryset.filter(num_answered__lt=1)
        if proposer is not '':
            queryset = queryset.filter(proposer__name=proposer)
        if search is not '':
            queryset = queryset.filter(title__icontains=search)
        if orderby is not '':
            queryset = queryset.order_by(orderby)
        else:
            queryset = queryset.order_by('-session__session_date', '-motion_id', '-id')

        paginator = Paginator(queryset, 100)
        page = self.request.GET.get('page')
        try:
            motions = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            motions = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            motions = paginator.page(paginator.num_pages)

        return motions


def motion_detail(request, id):
    motion = get_object_or_404(Motion, id=id)
    return render(request, 'motions/detail.html', {'motion': motion})


def motion_stats(request):
    answered_stats = Motion.objects.filter(answers__answered_date__isnull=False).values('parliamentary_group', 'session__session_date', 'answers__answered_date')

    time_sum = {'ÖVP': timedelta(), 'KPÖ': timedelta(), 'FPÖ': timedelta(), 'SPÖ': timedelta(), 'Grüne': timedelta(), 'Piraten': timedelta()}
    motions_count = {'ÖVP': 0, 'KPÖ': 0, 'FPÖ': 0, 'SPÖ': 0, 'Grüne': 0, 'Piraten': 0}

    for stat in answered_stats:
        stat['delta'] = stat['session__session_date'] - stat['answers__answered_date']
        time_sum[stat['parliamentary_group']] = time_sum[stat['parliamentary_group']] + stat['delta']
        motions_count[stat['parliamentary_group']] += 1

    return HttpResponse(str(time_sum))


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

