import csv

from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render
import json
from django.db.models import Value, F
from django.utils.safestring import mark_safe

from .models import *
from .utils import get_changes
from .forms import *
from .consts import *


def index_view_html(request):
    return render(request, 'django_change_list/changes.html', {
        'is_vue': False,
        'changes_form': ChangesForm(),
    })


def index_view_vuejs(request):
    changes_form = ChangesVueForm()
    init_data = changes_form.vue_init_data
    return render(request, 'django_change_list/changes_vuejs.html', {
        'is_vue': True,
        'list_of_change_types': mark_safe(json.dumps(all_change_names())),
        'changes_form': changes_form,
        'init_values': mark_safe(json.dumps(init_data)),
    })


def get_changes_from_request(request):
    if request.content_type == 'application/json':
        params = json.loads(request.body)
    else:
        params = request.POST

    from_version = params.get('from_version', None)
    to_version = params.get('to_version', None)

    change_types = params.get('change_types', [])
    if change_types:
        change_types = [CHANGE_TYPES[chg].value for chg in change_types]
    else:
        for change_type in CHANGE_TYPES:
            change_val = params.get(change_type_to_field_name(change_type), None)
            if change_val:
                change_types.append(change_type.value)

    changes = get_changes(from_version, to_version, change_types)

    return changes


def get_changes_as_list(request, fields=None):
    # Get Queryset
    queryset = get_changes_from_request(request)
    fields = fields or ChangeModel.get_vue_fields()
    changes = [{f: getattr(o, f) for f in fields} for o in queryset]

    return  changes


def changes_view_html(request):
    if request.is_ajax() and request.method == 'POST':
        changes = get_changes_from_request(request)
        return render(request, 'django_change_list/changes_list.html', {
                'changes': changes,
        })
    return HttpResponse('Invalid access')


def changes_view_json(request):
    if request.is_ajax() and request.method == 'POST':
        resp = {}
        data = get_changes_as_list(request)
        resp['data'] = data
        resp['columns'] = ChangeModel.get_vue_table_columns()
        return JsonResponse(resp, safe=False)

    return JsonResponse({'data': 'Invalid access'})


def get_jira_fields(queryset):
    jira_columns = ChangeModel.get_jira_columns()
    jira_fields = [f['field'] for f in jira_columns]
    jira_titles = [f['title'] for f in jira_columns]
    jira_changes = [[getattr(o, f) for f in jira_fields] for o in queryset]

    return jira_changes, jira_titles


def export_to_jira_csv(request):
    if request.is_ajax() and request.method == 'POST':
        # Get Data
        ids_to_get = json.loads(request.body).get('ids_to_get', None)
        if ids_to_get:
            queryset = ChangeModel.objects.filter(id__in=ids_to_get).select_related('release')
        else:
            queryset = get_changes_from_request(request)

        if not queryset or not queryset.exists():
            raise Http404("No results")

        jira_changes, jira_titles = get_jira_fields(queryset)

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="change_list_jira.csv"'

        writer = csv.writer(response)
        writer.writerow(jira_titles)
        for row in jira_changes:
            writer.writerow(row)

        return response
