from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context_processors import csrf
from django.core.urlresolvers import reverse
from ics import Calendar, Event
from .models import Course, Selection, Schedule
from .forms import SelectionForm
from datetime import datetime, timedelta


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
            ('Edit', reverse('edit_selection', kwargs={
                'selection_id': selection.id}))
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
        return HttpResponseRedirect(reverse('selection_detail', kwargs={'selection_id': selection.id}))
    form.action = reverse('create_selection')
    ctx = {'form': form, 'title': "Create my selection"}
    ctx.update(csrf(request))
    return render_to_response('create_selection.haml', ctx)


def selection_planning(request, selection_id):
    selection = get_object_or_404(Selection, pk=selection_id)
    from_time = request.GET.get('from_time', datetime.now())
    to_time = request.GET.get('to_time', datetime.now() + timedelta(days=7))
    schedules = Schedule.objects.filter(
        course__in=selection.courses.all()
    ).order_by('start_time')
        #start_time__ge=from_time.strftime("%Y-%m-%d %H:%M:%S"),
        #end_time__lt=to_time.strftime("%Y-%m-%d %H:%M:%S")).order_by(
        #    'start_time')
    return render_to_response("planning.haml", {
        'schedules': schedules,
        'selection': selection,
        'extra_menu': [
            ('iCal URL', reverse('selection_ics', kwargs={
                'selection_id': selection.id})),
            ('Edit', reverse('edit_selection', kwargs={
                'selection_id': selection.id}))
        ]})


def edit_selection(request, selection_id):
    selection = get_object_or_404(Selection, pk=selection_id)
    form = SelectionForm(request.POST or None, instance=selection)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('selection_detail', kwargs={'selection_id': selection.id}))
    form.action = reverse('edit_selection', kwargs={'selection_id': selection.id})
    ctx = {'form': form, 'title': "Update my selection"}
    ctx.update(csrf(request))
    return render_to_response('create_selection.haml', ctx)

def all_selections(request):
    return render_to_response("view_selections.haml", {
        'selections': Selection.objects.all().order_by('name'),
        'title': "All selections"})