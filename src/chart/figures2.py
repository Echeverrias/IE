from utilities import Colors_list, Lock, trace
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
# pip install pillow
import geopandas as gpd
import os
import io
import base64
from job.models import Job


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OCEANS_SHAPE_FILE = os.path.join(BASE_DIR, 'data/natural_earth/ne_50m_ocean.shp')
DEFAULT_EXTENSION_IMAGE = 'png'

COLOR_AREAS = {}

class Drawer:

    COLOR_AREAS = {}

    def __ini__(self, x_size=10, y_size=12):
        self.x_size = x_size
        self.y_size = y_size
        self.fgr = plt.figure(figsize=(self.x_size, self.y_size))
        self.axes = self.fgr.subplots()

    def _get_colors(self, colors_column_name_and_column_tuple):
        colors = []
        if colors_column_name_and_column_tuple[0] == 'area':
            colors = [self.COLOR_AREAS[area] for area in colors_column_name_and_column_tuple[1]]
        return colors

    def get_bar_figure(self, x, y, x_label, y_label, title, bar_horizontal=False,
                       colors_column_name_and_column_tuple=('x', None)):

        colors = _get_colors(colors_column_name_and_column_tuple)
        if not colors:
            color = Colors_list[0:len(x)]

        if bar_horizontal:
            self.axes.barh(x, y, color=colors)
            plt.xticks(rotation=45)
        else:
            self.axes.barh(x, y, color=colors)
        self.axes.set_xlabel(x_label)
        self.axes.set_ylabel(y_label)
        self.axes.set_title(title)
        plt.tight_layout()  # resize
        return self.fgr


    @trace
    def get_buffer_value_from_figure(self, format='png', dpi=600):
        buffer = io.BytesIO()

        # ¡Tarda 8 veces más que utilizando canvas!
        #self.fgr.savefig(buffer, format=format, dpi=dpi)

        canvas = FigureCanvasAgg(self.fgr)
        canvas.print_png(buffer)

        buffer_value = buffer.getvalue()
        buffer.close()
        #self.fgr.clear()
        return buffer_value



def _get_color_areas_list(areas):
    return [COLOR_AREAS[area] for area in areas]

def _get_colors(colors_column_name_and_column_tuple):
    colors = []
    if colors_column_name_and_column_tuple[0] == 'area':
        colors =  [COLOR_AREAS[area] for area in colors_column_name_and_column_tuple[1]]
    return colors

@Lock()
@trace
def get_bar_figure(x, y, x_label, y_label, title, bar_horizontal=False, colors_column_name_and_column_tuple=('x', None)):
    fgr = plt.figure(figsize=(10,12))
    # Creamos los ejes
    # axes = f.add_axes([0.40, 0.15, 0.63, 0.65])  # [left, bottom, width, height]
    # https://stackoverflow.com/questions/43326680/what-are-the-differences-between-add-axes-and-add-subplot
    axes = fgr.subplots()  # [left, bottom, width, height]
    #fgr.subplots_adjust(left=0.4)

    colors = _get_colors(colors_column_name_and_column_tuple)
    if not colors:
        color = Colors_list[0:len(x)]

    if bar_horizontal:
        axes.barh(x, y, color=colors)
        plt.xticks(rotation=45)
    else:
        axes.barh(x, y, color=colors)
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)
    axes.set_title(title)
    plt.tight_layout() # resize
    return fgr

def get_spain_map_figure(map_gdf, column, title):
    # Control del tamaño de la figura del mapa
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    # Control del encuadre (área geográfica) del mapa
    ax.axis([-12, 5, 32, 48])

    # Control del título y los ejes
    ax.set_title(title,
                 pad=20,
                 fontdict={'fontsize': 20, 'color': '#4873ab'})
    #ax.set_xlabel('Longitud')
    #ax.set_ylabel('Latitud')

    # Añadir la leyenda separada del mapa
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.2)

    # Generar y cargar el mapa
    map_gdf.plot(column=column, cmap='plasma', ax=ax,
                  legend=True, cax=cax, zorder=5)

    # Cargar un mapa base con contornos de países
    ocean_shape = OCEANS_SHAPE_FILE
    map_oceans = gpd.read_file(ocean_shape)
    map_oceans.plot(ax=ax, color='#89c0e8', zorder=0)
    return fig


# http://deeplearning.lipingyang.org/2018/07/21/django-sending-matplotlib-generated-figure-to-django-web-app/
def get_image_base64(buffer):
   return  base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')

def get_image_base64_from_figure(figure, format=DEFAULT_EXTENSION_IMAGE, dpi=600):
    buffer = io.BytesIO()
    figure.savefig(buffer, format=format, dpi=dpi)
    #f.savefig('my_chart.png', format='png', dpi=600)
    """
    canvas = FigureCanvasAgg(f)
    canvas.print_png(buf)
    """
    image_base64 = get_image_base64(buffer)
    buffer.close()
    figure.clear()
    return image_base64

@Lock()
@trace
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
def save_figure_as_image(figure, img_name, images_dir=None, format=DEFAULT_EXTENSION_IMAGE, dpi=600):
    if not os.path.isdir(images_dir):
        os.makedirs(images_dir, exist_ok=True)
    img_path = os.path.join(images_dir, f'{img_name}.{format}')
    print(f'save_figure_as_image at: {img_path}')
    figure.savefig(img_path, format=format, dpi=dpi)
    #canvas = FigureCanvasAgg(figure)
    #canvas.print_png(img_path)
    return img_path

if __name__ != '__main__':

    def load_color_areas():
        for i, v in enumerate(Job.AREA_CHOICES):
            COLOR_AREAS[v[0]] = Colors_list[i]
        print(COLOR_AREAS)

    load_color_areas()
