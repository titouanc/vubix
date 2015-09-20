from django.db import models
from itertools import chain


class Course(models.Model):
    name = models.CharField(max_length=250)
    faculty = models.CharField(max_length=50)
    kind = models.CharField(max_length=50)
    err_count = models.IntegerField(default=0)
    original_html_table = models.TextField()

    def table_view(self):
        return self.original_html_table

    table_view.allow_tags = True

    @property
    def schedules(self):
        return self.schedule_set.all()

    def __unicode__(self):
        return self.name

    @property
    def next_schedule(self):
        try:
            return self.schedule_set.order_by('end_time')[0]
        except:
            return None


class Schedule(models.Model):
    course = models.ForeignKey(Course)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=250)
    professor = models.CharField(max_length=50, default='')

    ordering = ['start_time']

    @property
    def course_name(self):
        return self.course.name

    @property
    def duration(self):
        return self.end_time - self.start_time


class Selection(models.Model):
    name = models.CharField(max_length=200)
    courses = models.ManyToManyField(Course)

    @property
    def schedules(self):
        return list(chain(*map(lambda c: c.schedules, self.courses.all())))
