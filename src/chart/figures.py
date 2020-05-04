from utilities.utilities import Colors_list, Lock, trace
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
# pip install pillow
import geopandas as gpd
import numpy as np
import os
import io
import base64
from job.models import Job


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OCEANS_SHAPE_FILE = os.path.join(BASE_DIR, 'data/natural_earth/ne_50m_ocean.shp')
DEFAULT_EXTENSION_IMAGE = 'png'

COLOR_AREAS = {}


def _get_color_areas_list(areas):
    return [COLOR_AREAS[area] for area in areas]

def _get_colors(colors_column_name_and_column_tuple):
    print();print();print(f'****************************figures._get_colors({colors_column_name_and_column_tuple})')
    colors = []
    if colors_column_name_and_column_tuple[0] == 'area':
        colors =  [COLOR_AREAS[area] for area in colors_column_name_and_column_tuple[1]]
    return colors

def _get_label(aggregation_or_groupby):
    dlabel = {
        'area': 'Área',
        'province': 'Provincia',
        'mean_salary': 'Salario medio',
        'vacancies': 'Vacantes',
        'registered_people': 'Gente registrada',
        'company-category': 'Compañía (categoría)',
        'company': 'Compañía',
        'category': 'Categoría',
    }
    default_label = aggregation_or_groupby.capitalize() if aggregation_or_groupby else('_')
    return  dlabel.get(aggregation_or_groupby, default_label)

def _get_name_filtered(filter):
    filter_splitted = filter.split('-')
    filter_name =  filter_splitted[-1] if type(filter_splitted) == list else  filter_splitted
    dname = {
        'nacional': 'nacionales',
        'internacional': 'internacionales',
    }
    return dname.get(filter_name, filter_name)

def _get_operator_aggregation_tuples(operators, aggregations):
    zipped = zip(operators, aggregations)
    operation_aggregation_tuples = []
    for o, a in zipped:
        operation_aggregation_tuples.append(o + '-' + a)
    return operation_aggregation_tuples

def _get_title(q, groupby, operator, aggregation, compareby=None):
    operator_aggregation_tuples = _get_operator_aggregation_tuples(operator, aggregation)
    key = "__".join(q) + "__" + "__".join(groupby) + "__" + "__".join(operator_aggregation_tuples)
    if compareby:
        key += "__" + "__".join(compareby)
    dtitle = {
        '__area__sum-vacancies': "Vacantes de ofertas por área",
        '__area__nationality__sum-vacancies__nationality': "Vacantes de ofertas nacionales e internacionales por área",
        '__area__sum-registered_people': "Gente registrada en ofertas por área",
        '__area__nationality__sum-registered_people__nationality': "Gente registrada en ofertas nacionales e internacionales por área",
        '__area__avg-mean_salary': "Salario medio en ofertas nacionales e internacionales por área",
        'filter-nationality-national__area__sum-vacancies': "Vacantes de ofertas nacionales por área",
        'filter-nationality-national__area__sum-registered_people': "Gente registrada en ofertas nacionales por área",
        'filter-nationality-national__province__sum-vacancies': "Vacantes de ofertas nacionales por provincia",
        'filter-nationality-national__province__sum-registered_people': "Gente registrada en ofertas nacionales por provincia",
        'filter-nationality-national__area__avg-mean_salary': "Salario medio en ofertas nacionales por área",
        'filter-nationality-national__province__avg-mean_salary': "Salario medio en ofertas nacionales por provincia",
        'filter-nationality-international__area__sum-vacancies': "Vacantes de ofertas internacioneales por área",
        'filter-nationality-international__area__sum-registered_people': "Gente registrada en ofertas internacioneales por área",
        'filter-nationality-international__area__avg-mean_salary': "Salario medio en ofertas internacionales por área",
        'filter-nationality-national__area__sum-vacancies__sum-registered_people': "Vacantes y gente registrada en ofertas nacionales por área",
        'filter-nationality-international__area__sum-vacancies__sum-registered_people': "Vacantes y gente registrada en ofertas internacionales por área",
        'filter-nationality-national': '?',
        'filter-available-jobs-in-year': '?',
        'filter-publication-date-jobs-in-year': '?',
        'i-filter-available-jobs-in-years-ago': '?',
        'i-filter-publication-date-jobs-in-years-ago': '?',
    }
    try:
        default_title = (' y '.join([_get_label(agg) for agg in aggregation]).capitalize() +
                         " de ofertas " +
                         (_get_name_filtered(q[0]) if q else "") +
                        " por " +
                        _get_label(groupby[0]).lower())
    except:
        default_title = '_'
    return dtitle.get(key, default_title)

def _get_column_name_from_request_query(q):
    splitted = q.split('-')
    return splitted[-2] if type(q.split) == list else splitted

def _get_value_from_request_query(q):
    splitted = q.split('-')
    return splitted[-1] if type(q.split) == list else splitted

def _get_axis_x(df, groupby):
    return df[groupby].unique()

def _get_axis_y(df, laggregation, lcompareby):
    """
    Example for 'if lcompareby:'
    data.append(df.loc[df['nationality'] == 'nacional', 'mean_salaries'])
    data.append(df.loc[df['nationality'] == 'internacional', 'mean_salaries'])
    """
    print();print(f'_get_axis-y(df, {laggregation}, {lcompareby})')
    data = []
    if lcompareby:
        compareby = lcompareby[0]
        types = df[compareby].unique()
        print(f'compareby: {compareby}')
        print(f'aggregation: {laggregation[0]}')
        print(f'types: {types}')
        for t in types:
            data.append(df.loc[df[compareby] == t, laggregation[0]])
    else:
        for aggregation in laggregation:
            data.append(df[aggregation])
    return data


def _get_legend(laggregation, lcompareby, df=None, location='upper right'):
    """
    #  legend = (['nacional', 'internacional'], 'upper right')
    """
    types = []
    if lcompareby:
        compareby = lcompareby[0]
        values = df[compareby].unique()
        for value in values:
            types.append(value)
    else:
        for aggregation in laggregation:
            types.append(_get_label(aggregation))
    return (types, location)

def _get_colors_configuration(df, lgroupby, lcompareby):
    lcol = lcompareby or lgroupby
    col = lcol[0]
    return (col, df[col].unique())

def get_buffer_value_from_figure(figure, format='png', dpi=600):
    print('get_buffer_value_from_figure')
    buffer = io.BytesIO()
    # ¡Tarda 8 veces más que utilizando canvas!
    # figure.savefig(buffer, format=format, dpi=dpi)
    canvas = FigureCanvasAgg(figure)
    canvas.print_png(buffer)
    print('canvas painted')
    buffer_value = buffer.getvalue()
    buffer.close()
    figure.clear()
    print('pppp')
    return  buffer_value

def get_spain_map_figure(map_gdf, data_column_name, title):
    # Control del tamaño de la figura del mapa
    fig, ax = plt.subplots(1, 1, figsize=(40, 40))

    # Control del encuadre (área geográfica) del mapa
    ax.axis([-12, 5, 32, 48])

    # Control del título y los ejes
    ax.set_title(title,
                 pad=40,
                 fontdict={'fontsize': 80, 'color': '#4873ab'})
    #ax.set_xlabel('Longitud')
    #ax.set_ylabel('Latitud')

    # Añadir la leyenda separada del mapa
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="7%", pad=0.5)
    cax.tick_params(axis="y", labelsize=40)
    # Generar y cargar el mapa
    map_gdf.plot(column=data_column_name, cmap='plasma', ax=ax,
                  legend=True, cax=cax, zorder=5)

    # Cargar un mapa base con contornos de países
    ocean_shape = OCEANS_SHAPE_FILE
    map_oceans = gpd.read_file(ocean_shape)
    map_oceans.plot(ax=ax, color='#89c0e8', zorder=0)
    return fig


@trace
def get_bars_figure(x, y, x_label, y_label, title, legend=([], 'upper right'), is_bar_horizontal=False, column_name_and_column_values_tuple_for_colors=('x', None)):
    print(f'********************figures.get_bar_figure')
    try:
        x = x.unique()  # !! unique
    except:
        pass
    # To make room for the labels (resize)
    plt.rcParams.update({'figure.autolayout': True}) # better than plt.tight_layout()
    """
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 6
    fig_size[1] = 12
    plt.rcParams["figure.figsize"] = fig_size
    """
    # Creamos los ejes
    # axes = f.add_axes([0.40, 0.15, 0.63, 0.65])  # [left, bottom, width, height]
    # https://stackoverflow.com/questions/43326680/what-are-the-differences-between-add-axes-and-add-subplot
    fig, axes = plt.subplots(figsize=(14,12)) # plt.subplots(figsize=(14,12))

    #fig = plt.figure(figsize=(16,12)) # plt.figure(figsize=(16,12))
    #axes = fig.subplots()  # [left, bottom, width, height]
    #fig.subplots_adjust(left=0.4)

    x_labels_position = np.arange(len(x))
    separation_between_x_labels_index = len(y) #9*len(y)^2#((len(y) + 1)^3)

    ind = x_labels_position * separation_between_x_labels_index
    coef = len(y) - 1
    size = 0.8 #len(y)*5
    print(f'len(y): {len(y)}')
    if len(y) > 1:
        colors = Colors_list[0:len(y)]
        offset = (size*coef)/2
        for i, y_ in enumerate(y):
            if is_bar_horizontal:
                axes.barh(ind + size*i, y_, height=size, color=colors[i])
            else:
                axes.bar(ind + size*i, y_, width=size, color=colors[i])
        axes.legend(legend[0], loc=legend[1]) # !! set axes after bars
    else:
        offset = 0
        colors = _get_colors(column_name_and_column_values_tuple_for_colors)
        if not colors:
            colors = Colors_list[0:len(x)]
        if is_bar_horizontal:
            axes.barh(ind, *y, color=colors, align='center')

        else:
            axes.bar(ind, *y, color=colors)

    if is_bar_horizontal:
        axes.set_yticks(ind + offset)
        axes.set_yticklabels(x)
        axes.set_xlabel(y_label, fontsize=18)
        axes.set_ylabel(x_label, fontsize=18)
        axes.invert_yaxis()
        #plt.xticks(rotation=45)
    else:
        axes.set_xticks(ind)
        axes.set_xticklabels(x)
        axes.set_xlabel(x_label, fontsize=18)
        axes.set_ylabel(y_label, fontsize=18)
        plt.xticks(rotation=90)

    axes.tick_params(axis="x", labelsize=18)
    axes.tick_params(axis="y", labelsize=18)
    axes.set_title(title, fontsize=18)

    fig.tight_layout()
    print('????????????????????????????¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿')
    return fig




def get_buffer_of_bars_from_df(df, **kwargs):
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print('get_buffer_of_plot_from_df')
    x = _get_axis_x(df, kwargs.get('groupby')[0])
    print(f'x: {x}')
    y = _get_axis_y(df, kwargs.get('aggregation'), kwargs.get('compareby'))
    print(f'y: {y}')
    x_label = _get_label(kwargs.get('groupby')[0])
    print(f'x_label: {x_label}')
    y_label = _get_label(kwargs.get('aggregation')[0])
    print(f'y_label: {y_label}')
    title = _get_title(**kwargs)
    print(f'title: {title}')
    legend = _get_legend(kwargs.get('aggregation'), kwargs.get('compareby'), df)
    print('legend')
    colors_column_name_and_column_tuple = _get_colors_configuration(df, kwargs.get('groupby'), kwargs.get('compareby'))
    print('colors')
    figure = get_bars_figure(x, y, x_label, y_label, title, legend, True, colors_column_name_and_column_tuple)

    return get_buffer_value_from_figure(figure)


def get_buffer_of_spain_map(df, **kwargs):
    title = _get_title(**kwargs)
    data_column_name = kwargs.get('aggregation')
    figure = get_spain_map_figure(df, data_column_name, title)
    return get_buffer_value_from_figure(figure)
####################################################################################################################


#get_buffer_of_plot(df['area'].unique(), [df['vacancies'], df['registered_people']], 'Áreas', 'Nº', title, legend, True)
#get_buffer_of_plot(df['area'].unique(), [df['vacancies'], df['registered_people']], 'Áreas', 'Nº', title, legend, True)
def get_buffer_of_plot(x, y, x_label, y_label, title, legend = [], is_bar_horizontal=False, colors_column_name_and_column_tuple=('x', None)):
    figure = get_bars_figure(x, y, x_label, y_label, title, legend, is_bar_horizontal, colors_column_name_and_column_tuple)
    return get_buffer_value_from_figure(figure)





@Lock()
@trace
def save_figure_as_image(figure, img_name, images_dir=None, format=DEFAULT_EXTENSION_IMAGE, dpi=600):
    if not os.path.isdir(images_dir):
        os.makedirs(images_dir, exist_ok=True)
    img_path = os.path.join(images_dir, f'{img_name}.{format}')
    print(f'save_figure_as_image at: {img_path}')
    figure.savefig(img_path, format=format, dpi=dpi)
    #canvas = FigureCanvasAgg(figure)
    #canvas.print_png(img_path)
    return img_path

def get_spain_map_figure(map_gdf, column, title):
    # Control del tamaño de la figura del mapa
    fig, ax = plt.subplots(1, 1, figsize=(40, 40))

    # Control del encuadre (área geográfica) del mapa
    ax.axis([-12, 5, 32, 48])

    # Control del título y los ejes
    ax.set_title(title,
                 pad=40,
                 fontdict={'fontsize': 80, 'color': '#4873ab'})
    #ax.set_xlabel('Longitud')
    #ax.set_ylabel('Latitud')

    # Añadir la leyenda separada del mapa
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="7%", pad=0.5)
    cax.tick_params(axis="y", labelsize=40)
    # Generar y cargar el mapa
    map_gdf.plot(column=column, cmap='plasma', ax=ax,
                  legend=True, cax=cax, zorder=5)

    # Cargar un mapa base con contornos de países
    ocean_shape = OCEANS_SHAPE_FILE
    map_oceans = gpd.read_file(ocean_shape)
    map_oceans.plot(ax=ax, color='#89c0e8', zorder=0)
    return fig



def get_spain_map_buffer(map_gdf, column, title):
    figure = get_spain_map_figure(map_gdf, column, title)
    return get_buffer_value_from_figure(figure)

if __name__ != '__main__':

    def load_color_areas():
        for i, v in enumerate(Job.AREA_CHOICES):
            COLOR_AREAS[v[0]] = Colors_list[i]
        print(COLOR_AREAS)

    load_color_areas()
