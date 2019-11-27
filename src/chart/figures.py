from utilities import Colors_list, Lock, trace
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


@trace
def get_bar_figure(x, y, x_label, y_label, title, legend=([], 'upper right'), bar_horizontal=False, colors_column_name_and_column_tuple=('x', None)):
    print(f'********************figures.get_bar_figure')
    fgr = plt.figure(figsize=(16,12))
    try:
        x = x.unique()  # !! unique
    except:
        pass
    # Creamos los ejes
    # axes = f.add_axes([0.40, 0.15, 0.63, 0.65])  # [left, bottom, width, height]
    # https://stackoverflow.com/questions/43326680/what-are-the-differences-between-add-axes-and-add-subplot
    axes = fgr.subplots()  # [left, bottom, width, height]
    #fgr.subplots_adjust(left=0.4)
    ind = np.arange(len(x))
    size = 0.4

    if len(y) > 1:
        colors = Colors_list[0:len(y)]
        offset = size/len(y)
        for i, y_ in enumerate(y):
            if bar_horizontal:
                axes.barh(ind + size*i, y_, height=size, color=colors[i])
            else:
                axes.bar(ind + size*i, y_, width=size, color=colors[i])
        axes.legend(legend[0], loc=legend[1]) # !! set axes after bars
    else:
        offset = 0
        colors = _get_colors(colors_column_name_and_column_tuple)
        if not colors:
            colors = Colors_list[0:len(x)]
        if bar_horizontal:
            axes.barh(ind, *y, color=colors, align='center')

        else:
            axes.bar(ind, *y, color=colors)

    if bar_horizontal:
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
    plt.tight_layout() # resize
    return fgr


def get_buffer_value_from_figure(figure, format='png', dpi=600):
    buffer = io.BytesIO()

    # ¡Tarda 8 veces más que utilizando canvas!
    #figure.savefig(buffer, format=format, dpi=dpi)

    canvas = FigureCanvasAgg(figure)
    canvas.print_png(buffer)

    buffer_value = buffer.getvalue()
    buffer.close()
    figure.clear()
    return  buffer_value

@Lock()
@trace
def get_buffer_of_plot(x, y, x_label, y_label, title, legend = [], bar_horizontal=False, colors_column_name_and_column_tuple=('x', None)):
    figure = get_bar_figure(x, y, x_label, y_label, title, legend, bar_horizontal, colors_column_name_and_column_tuple)
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
