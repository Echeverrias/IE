from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .managers import TaskManager

class Task(models.Model):
    STATE_PENDING = 'Pendiente'
    STATE_RUNNING = 'Ejecutándose'
    STATE_INCOMPLETE = 'Incompleta'
    STATE_FINISHED = 'Terminada'
    STATE_FINISHED_WITH_ERROR = 'Terminada debido a un error'
    STATE_CHOICES = (
        (STATE_PENDING, STATE_PENDING),
        (STATE_INCOMPLETE, STATE_INCOMPLETE),
        (STATE_RUNNING, STATE_RUNNING),
        (STATE_FINISHED, STATE_FINISHED),
        (STATE_FINISHED_WITH_ERROR, STATE_FINISHED_WITH_ERROR),
    )
    TYPE_CRAWLER = 'Crawler'
    TYPE_CHOICES = (
        (TYPE_CRAWLER, 'Crawler'),
    )
    pid = models.PositiveIntegerField(null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='usuario')
    name = models.CharField(max_length=200, null=True, default='', blank=True, verbose_name='nombre')
    state = models.CharField(
        max_length=30,
        choices=STATE_CHOICES,
        default=STATE_PENDING,
        null=True,
        blank=True, verbose_name='estado',
    )
    type = models.CharField(
        null=True,
        max_length=23,
        choices=TYPE_CHOICES,
        default='', verbose_name='tipo',
    )
    description = models.CharField(max_length=200, null=True, default='', blank=True, verbose_name='descripción')
    result = models.IntegerField(null=True, default=0, blank=True, verbose_name='resultado')
    error = models.CharField(null=True, default=0, blank=True, max_length=200, verbose_name='error')
    started_at = models.DateTimeField(null=True, blank=True, default=None, verbose_name="fecha de comienzo de la tarea")
    finished_at = models.DateTimeField(null=True, blank=True, default=None, verbose_name="fecha de finalización de la tarea")
    created_at = models.DateTimeField(editable=False, null=True, verbose_name="fecha de creación del registro")  # models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True, verbose_name="fecha de actualización del registro") # models.DateTimeField(auto_now=True)
    objects = TaskManager()

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-created_at', 'state']
        # unique_together = (('id'),)

    def __str__(self):
        return f'Task {self.type} {self.name} ({self.pid}) - {self.state} - creada el: {self.created_at} - actualizada el: {self.updated_at}'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.localtime(timezone.now())
        else:
            self.updated_at = timezone.localtime(timezone.now())
        return super(Task, self).save(*args, **kwargs)

    @property
    def is_running(self):
        return self.state == Task.STATE_RUNNING

    @property
    def is_completed(self):
        return self.state == Task.STATE_FINISHED

