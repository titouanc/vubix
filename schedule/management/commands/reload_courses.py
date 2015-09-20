from django.core.management.base import BaseCommand
from django.db import transaction
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

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
Y1, M1, D1 = 2015, 9, 14

url = "http://splus.cumulus.vub.ac.be:1183/1onevenjr/studsetWE_onevenjr.html"
form = BeautifulSoup(requests.get(url).content, "html.parser").find('form')
weeks = [
    (c.text.strip(), c.attrs['value'])
    for c in form.select('select[name=weeks] option')]


def mkurl(url, params, **additional_params):
    p = dict(params)
    p.update(additional_params)
    res = url + '?' + "&".join("%s=%s" % (k, v) for k, v in p.iteritems())
    return res.replace(' ', '+')


def parse_weeks(weekstring):
    for week in weekstring.split(', '):
        parts = week.split('-')
        if len(parts) == 2:
            first, last = map(int, parts)
            for i in range(first, last+1):
                yield int(i)
        else:
            yield int(parts[0])


def parse_time_table(course, table):
    for row in table.select("tr"):
        if row.get('class', None) == "columnTitles":
            raw_input('continue')
            continue
        values = [t.text.strip() for t in row.select('td')]
        day, start, end = values[1], values[2], values[3]
        if not start or not end or not day:
            course.err_count += 1
        else:
            start_time = datetime(Y1, M1, D1, *map(int, values[2].split(':')))
            start_time += timedelta(days=nl_days[values[1]])

            end_time = datetime(Y1, M1, D1, *map(int, values[3].split(':')))
            end_time += timedelta(days=nl_days[values[1]])
            for week in parse_weeks(values[5]):
                offset = timedelta(days=7*(week-1))
                try:
                    Schedule.objects.create(
                        course=course,
                        start_time=start_time + offset,
                        end_time=end_time + offset,
                        location=values[7],
                        professor=values[6])
                except:
                    course.err_count += 1


def parse_course_header(table):
    course, created = Course.objects.get_or_create(
        name=table.select("span.label-1-0-0")[0].text.strip(),
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
        url = "http://splus.cumulus.vub.ac.be:1183/1onevenjr/opleidingsonderdelen_onevenjr.html"
        form = mksoup(requests.get(url).content).find('form')

        action = form.attrs['action']
        inputs = {
            i.attrs['name']: i.attrs['value']
            for i in form.select('input')}

        # Truncate previous schedules
        Schedule.objects.all().delete()

        for option in form.select('select[name=identifier] option'):
            page = requests.get(
                mkurl(action, inputs, identifier=option.text.strip()))
            parse_courses_page(page.content)
            self.stdout.write(option.text.strip())

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            self.main()
