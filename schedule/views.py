from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context_processors import csrf
from django.core.urlresolvers import reverse
from ics import Calendar, Event
from .models import Course, Selection
from .forms import SelectionForm


def schedules_to_ics(func):
    def wrapper(*args, **kwargs):
        schedules = func(*args, **kwargs)
        cal = Calendar()
        for sched in schedules:
            cal.events.append(Event(
                name=sched.course_name,
                begin=sched.start_time,
                end=sched.end_time,
                location=sched.location))
        return HttpResponse(str(cal), content_type='text/calendar')
    return wrapper


def detail_all_courses(request):
    return render_to_response("view_courses.haml", {
        'courses': Course.objects.all(),
        'title': "All courses"})


def detail_for_selection(request, selection_id):
    selection = get_object_or_404(Selection, pk=selection_id)
    return render_to_response("view_courses.haml", {
        'courses': sorted(
            selection.courses.all(),
            key=lambda c: c.next_schedule.start_time),
        'title': "Selection: " + selection.name,
        'extra_menu': [
            ('iCal URL', reverse('selection_ics', kwargs={
                'selection_id': selection.id})),
        ]})


@schedules_to_ics
def ics_for_course(request, course_id):
    return get_object_or_404(Course, pk=course_id).schedules


@schedules_to_ics
def ics_for_selection(request, selection_id):
    return get_object_or_404(Selection, pk=selection_id).schedules


def create_selection(request):
    if request.method == 'GET':
        form = SelectionForm()
    else:
        form = SelectionForm(request.POST)
        if form.is_valid():
            selection = form.save()
            return HttpResponseRedirect("/schedule/selection/%d" % selection.id)
    ctx = {'form': form, 'title': "Create my selection"}
    ctx.update(csrf(request))
    return render_to_response('create_selection.haml', ctx)
