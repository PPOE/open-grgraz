from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from api.models import ParliamentaryGroup
from api.serializers import ParliamentaryGroupSerializer

# Create your views here.


class JsonResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JsonResponse, self).__init__(content, **kwargs)


def index(request):
    return HttpResponse('Hello API World!')


@csrf_exempt
def groups(request):
    parl_groups = ParliamentaryGroup.objects.all()
    serializer = ParliamentaryGroupSerializer(parl_groups, many=True)
    return JsonResponse(serializer.data)


@csrf_exempt
def group_detail(request, id):
    try:
        parl_group = ParliamentaryGroup.objects.get(id=id)
    except ParliamentaryGroup.DoesNotExist:
        return HttpResponse(status=404)
    serializer = ParliamentaryGroupSerializer(parl_group)
    return JsonResponse(serializer.data)
