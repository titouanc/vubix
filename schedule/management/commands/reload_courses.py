from django.core.management.base import BaseCommand
from django.db import transaction
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
from tqdm import tqdm
import re

from schedule.models import Course, Schedule

mksoup = lambda markup: BeautifulSoup(markup, "html.parser")
nl_days = {
    'ma': 0,
    'di': 1,
    'wo': 2,
    'do': 3,
    'vr': 4,
    'za': 5,
    'zo': 6,
}

# First week start date

def first_week_date():
    calendar = requests.get('http://splus.cumulus.vub.ac.be:1183/reporting/individual?idtype=name&periods=3-27&days=1-6&template=Student+Set+Individual&objectclass=Student+Set&width=100&identifier=1+M+Computer+Science%2FArtificial+Intelligence&weeks=1-14&days0=1-6&periods=3-23&submit=check+your+timetable')
    span = BeautifulSoup(calendar.content, 'html.parser').find('span', { 'class': 'header-6-0-3' })
    d = datetime.strptime(span.text.capitalize(), '%d %b %Y')
    return d.year, d.month, d.day


Y1, M1, D1 = first_week_date()

def timetable_url():
    if Y1 % 2 == 0: # even
        return 'http://splus.cumulus.vub.ac.be:1184/2evenjr/opleidingsonderdelen_evenjr.html'
    else: # odd
        return 'http://splus.cumulus.vub.ac.be:1183/1onevenjr/opleidingsonderdelen_onevenjr.html'


def mkurl(url, params, **additional_params):
    p = dict(params)
    p.update(additional_params)
    res = url + '?' + "&".join("%s=%s" % (k, v) for k, v in p.iteritems())
    return res.replace("  ", '+').replace(' ', '+')


def parse_weeks(weekstring):
    for week in weekstring.split(', '):
        parts = week.split('-')
        if len(parts) == 2:
            first, last = map(int, parts)
            for i in range(first, last+1):
                yield int(i)
        elif parts[0]:
            yield int(parts[0])


def parse_time_table(course, table):
    for row in table.select("tr"):
        if row.get('class', None) == "columnTitles":
            raw_input('continue')
            continue
        values = [t.text.strip() for t in row.select('td')]
        name, day, start, end = values[0:4]
        is_night_course = name.endswith('BP')
        if is_night_course:
            continue

        if not start or not end or not day:
            course.err_count += 1
        else:
            start_time = datetime(Y1, M1, D1, *map(int, values[2].split(':'))) + timedelta(days=nl_days[values[1]])
            end_time = datetime(Y1, M1, D1, *map(int, values[3].split(':'))) + timedelta(days=nl_days[values[1]])

            tz = pytz.timezone('Europe/Brussels')
            for week in parse_weeks(values[5]):
                offset = timedelta(days=7*(week-1))
                try:
                    prof = values[6].title()
                    if len(prof.split()) == 2:
                        last, first = prof.split()
                        prof = "%s %s" % (first, last)
                    Schedule.objects.get_or_create(
                        course=course,
                        start_time=tz.localize(start_time + offset),
                        end_time=tz.localize(end_time + offset),
                        location=values[7],
                        professor=prof)
                except:
                    course.err_count += 1


def parse_course_header(table):
    title = table.select("span.label-1-0-0")[0].text.strip().replace('\n', ' ')
    match = re.match(r'(.*)[ ]+(\d+)[ ]+(credits|credtis)[ ]+(\d+\w+)', title)
    if match:
        name, credits, _, course_id = match.groups()
    else:
        match = re.match(r'(.*)[ ]+(\d+)[ ]+(credits|credtis)', title)
        if match:
            name, credits, _ = match.groups()
            course_id = ""
        else:
            name = title
            credits = -1
            course_id = ""

    course, created = Course.objects.get_or_create(
        name=name,
        credits=int(credits),
        vub_id=course_id,
        kind=table.select("span.label-1-0-1")[0].text.strip().strip('()'),
        faculty=table.select("span.label-1-0-4")[0].text.strip())
    return course


def parse_courses_page(page_content):
    soup = mksoup(page_content)
    courses = map(parse_course_header, soup.select('table.label-border-args'))
    for course, table in zip(courses, soup.select('table.spreadsheet')):
        course.original_html_table = str(table)
        parse_time_table(course, table)
        course.save()


class Command(BaseCommand):
    help = "Populate database with "

    requires_system_checks = True

    def main(self):
        url = timetable_url()
        form = mksoup(requests.get(url).content).find('form')

        action = form.attrs['action']
        inputs = {
            i.attrs['name']: i.attrs['value']
            for i in form.select('input')}

        # Truncate previous schedules
        Schedule.objects.all().delete()

        for option in tqdm(form.select('select[name=identifier] option')):
            page = requests.get(
                mkurl(action, inputs, identifier=option.text.strip()))
            parse_courses_page(page.content)
            # self.stdout.write(option.text.strip())

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            self.main()
