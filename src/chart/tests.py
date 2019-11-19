from django.test import TestCase
from  job.models import Job
from django.db.models import When, Sum, Case, F, Q
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_agg import FigureCanvasAgg
from utilities import trace
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def save_figure_as_image(figure, img_name, images_dir=BASE_DIR, format='png', dpi=600):
    if not os.path.isdir(images_dir):
        os.makedirs(images_dir, exist_ok=True)
    img_path = os.path.join(images_dir, f'{img_name}.{format}')
    print(f'save_figure_as_image at: {img_path}')
    figure.savefig(img_path, format=format, dpi=dpi)
    #canvas = FigureCanvasAgg(figure)
    #canvas.print_png(img_path)
    return img_path

def save_in_csv(df, name):
    df.to_csv(name, index=False)


@trace
def get_qs():
    jobs = Job.objects.all().values('nationality', 'area').order_by('nationality', 'area').annotate(vacancies_=Sum('vacancies'))
    return jobs

@trace
def get_qs2():

    annotation1 = Case(
        When(country_name='España', then=F('vacancies')),
        default=0,
    )
    annotation2 = Case(
        When(country__name='España', then=0),
        default=F('vacancies'),
    )
    annotations = {
        'national_vacancies': annotation1,
        'international_vacancies': annotation2,
    }

    jobs = Job.objects.exclude_first_job().annotate(**annotations)

    annotations = {
        'national_vacancies_': Sum('national_vacancies'),
        'international_vacancies_': Sum('international_vacancies'),
    }

    jobs = jobs.values('area').order_by('area').annotate(**annotations)
    return jobs

@trace
def get_qs3():

    jobs = Job.objects.exclude_first_job().values('nationality', 'area', 'vacancies')
    return jobs

@trace
def get_df(qs):

    df = pd.DataFrame.from_records(qs)
    return df

@trace
def get_fgr(df):
    x = df['area']
    y1= df['national_vacancies_']
    y2= df['international_vacancies_']
    x_label = 'area'
    y_label1 = 'Vacantes nacionales'
    y_label2 = 'Vacantes internacionales'
    title = 'Vacantes'

    fgr = plt.figure(figsize=(10, 12))
    # Creamos los ejes
    # axes = f.add_axes([0.40, 0.15, 0.63, 0.65])  # [left, bottom, width, height]
    # https://stackoverflow.com/questions/43326680/what-are-the-differences-between-add-axes-and-add-subplot
    axes = fgr.subplots()  # [left, bottom, width, height]
    # fgr.subplots_adjust(left=0.4)

    colors = ['red', 'blue']

    axes.barh(x, y1)
    axes.barh(x, y2)

    plt.xticks(rotation=45)
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label1)
    axes.set_title(title)
    plt.tight_layout()  # resize
    return fgr

@trace
def get_fgr2(df):
    x = df['area']
    y1= df['national_vacancies_']
    y2= df['international_vacancies_']
    x_label = 'area'
    y_label1 = 'Vacantes nacionales'
    y_label2 = 'Vacantes internacionales'
    title = 'Vacantes'

    fgr = plt.figure(figsize=(10, 12))
    # Creamos los ejes
    # axes = f.add_axes([0.40, 0.15, 0.63, 0.65])  # [left, bottom, width, height]
    # https://stackoverflow.com/questions/43326680/what-are-the-differences-between-add-axes-and-add-subplot
    axes = fgr.subplots()  # [left, bottom, width, height]
    # fgr.subplots_adjust(left=0.4)

    colors = ['red', 'blue']

    plt.barh(x, y1, label='Vacantes nacionales',  color='lightblue')
    plt.barh(x, y2, label='Vacantes internacionales',  color='orange')

    plt.xticks(rotation=45)
    # Definir título y nombres de ejes
    plt.ylabel('Vacantes')
    plt.xlabel('Áreas')
    # Mostrar leyenda y figura
    plt.legend()
    plt.show()
    plt.title('Vacantes por área')
    plt.tight_layout()  # resize
    return fgr

@trace
def get_fgr3(df):
    axes  = df.pivot('area', 'nationality', 'vacancies_').plot(kind='barh')#
    #axes.set_xlabel(x_label)
    #axes.set_ylabel(y_label1)
    #axes.set_title(title)
    return axes.figure

def get_fgr4(df):
    fig, ax = plt.subplots(figsize=(12, 8))
    x = np.arange(len(df.area.unique()))
    bar_width = 0.4
    b1 = ax.bar(x, df.loc[df['nationality'] == 'national', 'vacancies_'],
                width=bar_width)
    b2 = ax.bar(x + bar_width, df.loc[df['nationality'] == 'international', 'vacancies_'],
                width=bar_width)

    # Fix the x-axes.
    ax.set_xticks(x + bar_width / 2)
    ax.set_xticklabels(df.area.unique())
    return fig


def test1():
    qs = get_qs()
    df = get_df(qs)
    fgr = get_fgr4(df)
    save_figure_as_image(fgr, 'test_bar')

def get_axes():
    qs = get_qs()
    df = get_df(qs)
    axes = df.pivot('area', 'nationality', 'vacancies_').plot(kind='barh')  #
    return axes