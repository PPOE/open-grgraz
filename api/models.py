from django.db import models

# Create your models here.


class ParliamentaryGroup(models.Model):
    id = models.CharField(max_length=9, primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class ParliamentarySession(models.Model):
    session_date = models.DateField()

    def __str__(self):
        return str(self.session_date)


class CouncilPerson(models.Model):
    name = models.CharField(max_length=200)
    academic_degree = models.CharField(max_length=100)
    email = models.EmailField()
    parliamentary_group = models.ForeignKey(ParliamentaryGroup)

    def __str__(self):
        return '{} {}'.format(self.academic_degree, self.name)


class MotionType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class File(models.Model):
    long_filename = models.CharField(max_length=1000)
    short_filename = models.CharField(max_length=100)
    # full_text = models.TextField() maybe?
    path = models.CharField(max_length=2000)

    def __str__(self):
        return self.short_filename


class Motion(models.Model):
    id = models.IntegerField(primary_key=True)
    session = models.ForeignKey(ParliamentarySession)
    title = models.CharField(max_length=1000)
    motion_type = models.ForeignKey(MotionType)
    parliamentary_group = models.ForeignKey(ParliamentaryGroup)
    proposer = models.ForeignKey(CouncilPerson)
    files = models.ManyToManyField(File)
    answer = models.ForeignKey('self', null=True, blank=True)

    def __str__(self):
        return self.title
