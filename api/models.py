from django.db import models

# Create your models here.


class ParliamentaryGroup(models.Model):
    id = models.CharField(max_length=9, primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class ParliamentarySession(models.Model):
    session_date = models.DateField(unique=True)

    def __str__(self):
        return str(self.session_date)


class CouncilPerson(models.Model):
    name = models.CharField(max_length=200, unique=True)
    academic_degree = models.CharField(max_length=100)
    email = models.EmailField()
    parliamentary_group = models.ForeignKey(ParliamentaryGroup)

    def __str__(self):
        return '{} {}'.format(self.academic_degree, self.name)


class File(models.Model):
    long_filename = models.CharField(max_length=1000, unique=True)
    short_filename = models.CharField(max_length=100)
    # full_text = models.TextField() maybe?
    path = models.CharField(max_length=2000)

    def __str__(self):
        return self.short_filename


class Answer(models.Model):
    id = models.IntegerField(primary_key=True)
    motion_id = models.IntegerField(default=-1)
    session = models.ForeignKey(ParliamentarySession)
    title = models.CharField(max_length=1000)
    parliamentary_group = models.ForeignKey(ParliamentaryGroup)
    proposer = models.ForeignKey(CouncilPerson)
    files = models.ManyToManyField(File, blank=True)

    def __str__(self):
        return self.title


class Motion(models.Model):
    id = models.IntegerField(primary_key=True)
    motion_id = models.IntegerField(default=-1, unique=True)
    session = models.ForeignKey(ParliamentarySession)
    title = models.CharField(max_length=1000)
    motion_type = models.CharField(max_length=200, default='')
    parliamentary_group = models.ForeignKey(ParliamentaryGroup)
    proposer = models.ForeignKey(CouncilPerson)
    files = models.ManyToManyField(File)
    answers = models.ManyToManyField(Answer, blank=True)

    def answered(self):
        return self.answers.count() > 0

    def __str__(self):
        return self.title
