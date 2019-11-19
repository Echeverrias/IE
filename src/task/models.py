from django.db import models

# Create your models here.
class Task(models.Model):
    STATE_RUNNING = 'Ejecutándose'
    STATE_FINISHED = 'Terminada'
    STATE_FINISHED_WITH_ERROR = 'Terminada debido a un error'
    STATE_CHOICES = (
        (STATE_RUNNING, STATE_RUNNING),
        (STATE_FINISHED, STATE_FINISHED),
        (STATE_FINISHED_WITH_ERROR, STATE_FINISHED_WITH_ERROR),
    )

    TYPE_CRAWLER = 'Crawler'
    TYPE_CHOICES = (
        (TYPE_CRAWLER, 'Crawler'),
    )

    name = models.CharField(max_length=200, null=True, default='', blank=True)
    user = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, default='', blank=True)
    result = models.IntegerField(null=True, default=0, blank=True)
    error = models.CharField(max_length=200)
    state = models.CharField(
        max_length=30,
        choices=STATE_CHOICES,
        default=STATE_RUNNING,
        null=True,
        blank=True,
    )

    type = models.CharField(
        max_length=23,
        choices=TYPE_CHOICES,
        default='',
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)  # models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True, default=None)  # models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-created_at', 'state']  # El - delante del nombre del atributo indica que se o
        # unique_together = (('id'),)



    def __str__(self):
        return "%s - %s - %s - (%s)" % (self.name, self.type, self.state, self.created_at)

