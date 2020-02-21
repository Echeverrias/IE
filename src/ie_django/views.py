
from django.shortcuts import render, redirect
from django.http import HttpResponse
from task.tasks import bg_run_crawler, prueba2
from background_task.models import Task
from background_task.models_completed import CompletedTask
import subprocess
import datetime
import time
from utilities import write_in_a_file
import threading
from background_task import background




def init_view(request):
    print('init_view')
    print(f'request.user.is_authenticated: {request.user.is_authenticated}')
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        template_name = "index.html"
        return render(request, template_name)




if __name__ != "__main__":
    print(f'EXECUTING DJANGO by {__name__}')


    def init_subprocess_process_tasks():
        print('init_subprocess_process_tasks')
        write_in_a_file(f'init_subprocess_process_tasks at {str(datetime.datetime.now())}', {}, 'bg-task.txt')
        @background(schedule=1)
        def inited_subprocess_process_tasks():
            pass


        def run_subprocess_process_tasks():
            write_in_a_file(f'init_subprocess_process_tasks at {str(datetime.datetime.now())} -- thread', {}, 'bg-task.txt')
            # Retard added to guarantee that background function is added to the Background Tasks Queue before run process_tasks
            time.sleep(5)
            today = datetime.date.today()
            try:
                last_bg_task = Task.objects.filter(task_name="ie_django.views.inited_subprocess_process_tasks").latest('run_at')
            except:
                last_bg_task = None
            try:
                last_bg_ctask = CompletedTask.objects.filter(task_name="ie_django.views.inited_subprocess_process_tasks").latest('run_at')
            except:
                last_bg_ctask = None

            task = last_bg_task if last_bg_task else last_bg_ctask
            try:
                task_date = datetime.datetime.date(task.run_at)
            except:
                task_date = None
            print(today)
            print(task_date)
            if (not task_date) or (task_date != today):
                inited_subprocess_process_tasks(repeat=None)  # function added to the Background Tasks Queue
                write_in_a_file(f'init_subprocess_process_tasks at {str(datetime.datetime.now())} NO ha sido ejecutado por lo que se va a ejecutar', {}, 'bg-task.txt')
                print('init_subprocess_process_tasks --- no se ha ejecutado')
                print('- - - - Se va a ejecutar subprocess.popen')
                command = ['python', 'manage.py', 'process_tasks']
                sp = subprocess.Popen(command)
                write_in_a_file(f'init_subprocess_process_tasks at {str(datetime.datetime.now())} se van a ejecutar las tareas de la cola', {}, 'bg-task.txt')
            else:
                write_in_a_file(f'init_subprocess_process_tasks at {str(datetime.datetime.now())} ya ha sido ejecutado', {}, 'bg-task.txt')
                print('init_subprocess_process_tasks --- ha sido ejecutado')

        thread = threading.Thread(target=run_subprocess_process_tasks)
        thread.start()


    def execute_background_task():
        print('execute_background_task')
        write_in_a_file(f'execute_background_task at {str(datetime.datetime.now())}', {}, 'bg-task.txt')
        #if not Task.objects.filter(task_name="task.tasks.bg_run_crawler"):
        if not Task.objects.filter(task_name="task.tasks.prueba2"):
            bg_run_crawler(repeat=300, repeat_until=None)  # function added to the Background Tasks Queue
            #prueba2(repeat=20)
            print('execute_background_task - - - - tarea añadida a la cola')
            write_in_a_file(f'execute_background_task at {str(datetime.datetime.now())} tarea añadida a la cola', {}, 'bg-task.txt')
        else:
            print('execute_background_task ---ya existe la tarea en la cola')
            write_in_a_file(f'execute_background_task at {str(datetime.datetime.now())} la tarea ya ha sido añadida a la cola', {}, 'bg-task.txt')


    init_subprocess_process_tasks()
    execute_background_task()

