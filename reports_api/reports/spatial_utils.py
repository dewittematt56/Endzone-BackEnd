import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from matplotlib.colors import LinearSegmentedColormap, rgb2hex
from jenkspy import jenks_breaks
import pandas as pd
import numpy as np
from .utils import __save_matPlot__

class PassZone(object):
    def __init__(self, df: pd.DataFrame, value_column: str, label_column: str = 'Category', number_of_classes: int = 3, legend_labels: list = ['Low Attempts', 'Medium Attempts', 'High Attempts']):
        fig, ax = plt.subplots()
        self.df = df
        self.value_column = value_column
        self.ax = ax
        self.fig = fig
        self.label_column = label_column
        self.legend_labels = legend_labels
        self.number_of_classes = number_of_classes
        if self.number_of_classes > len(self.df[self.value_column].unique()):
            self.number_of_classes = len(self.df[self.value_column].unique())
        self.__prep_dataframe__()
        self.polish_graph()

    def add_label_to_pass_zone(self, label: str, label_x: float, label_y: float, text_color: str = 'white'):
        self.ax.annotate(label, (label_x, label_y), color=text_color, fontsize=10,
                ha='center')

    def __prep_dataframe__(self):
        breaks = jenks_breaks(self.df[self.value_column], n_classes=self.number_of_classes)
        cmap = LinearSegmentedColormap.from_list('test', ['#0000FF', '#FF0000'], self.number_of_classes)
        self.colors = [rgb2hex(cmap(x)) for x in range(self.number_of_classes + 1)]
        self.df['Color'] = np.searchsorted(breaks, self.df[self.value_column])
        self.df['Color'] = self.df['Color'].apply(lambda x: self.colors[x])

    def __get_pass_zone_color__(self, pass_zone: str):
        try:
            value = self.df.loc[self.df[self.label_column] == pass_zone, 'Color'].iloc[0]
            if(value): return (value)
            return ;'#ffffff'
        except IndexError:
            return'#ffffff'

    def __get_value__(self, pass_zone: str):
        try:
            value = self.df.loc[self.df[self.label_column] == pass_zone, self.value_column].iloc[0]
            if(value): return value
            return 0
        except IndexError:
            return 0
        
    def __set_box_details__(self, pass_zone, x_centroid, y_centroid):
        color = self.__get_pass_zone_color__(pass_zone)
        text_color = 'white'
        if color == '#ffffff':
            text_color = 'black'
        self.ax.annotate(self.__get_value__(pass_zone), (x_centroid, y_centroid), color=text_color, fontsize=24, ha='center')
        self.add_label_to_pass_zone(pass_zone.replace("-", " "), x_centroid, y_centroid - .25, text_color)
        return color
    
    def plot_pass_zones(self):
        flats_left_polygon = Polygon([(0, 0), (0, 1), (1.5, 1), (1.5, 0)], closed=True, facecolor = self.__set_box_details__('Flats-Left', .75, .5), edgecolor = 'black')
        flats_right_polygon = Polygon([(1.5, 0), (1.5, 1), (3, 1), (3, 0)], closed=True, facecolor = self.__set_box_details__('Flats-Right', 2.25, .5), edgecolor = 'black')
        deep_left_polygon = Polygon([(0, 2), (0, 3), (1.5, 3), (1.5, 2)], closed=True, facecolor = self.__set_box_details__('Deep-Left', .75, 2.5), edgecolor = 'black')
        deep_right_polygon = Polygon([(1.5, 2), (1.5, 3), (3, 3), (3, 2)], closed=True, facecolor = self.__set_box_details__('Deep-Right', 2.25, 2.5), edgecolor = 'black')
        middle_left_polygon = Rectangle((0, 1), 1, 1, facecolor =  self.__set_box_details__('Middle-Left', .5, 1.5), edgecolor = 'black')
        middle_middle_polygon = Rectangle((1, 1), 1, 1, facecolor= self.__set_box_details__('Middle-Right', 2.5, 1.5), edgecolor = 'black')
        middle_right_polygon = Rectangle((2, 1), 1, 1, facecolor= self.__set_box_details__('Middle-Middle', 1.5, 1.5), edgecolor = 'black')

        self.ax.add_patch(flats_left_polygon)
        self.ax.add_patch(flats_right_polygon)
        self.ax.add_patch(middle_left_polygon)
        self.ax.add_patch(middle_middle_polygon)
        self.ax.add_patch(middle_right_polygon)
        self.ax.add_patch(deep_left_polygon)
        self.ax.add_patch(deep_right_polygon)

    def polish_graph(self):
        self.ax.set_aspect('equal')
        self.ax.set_xlim([0, 4])
        self.ax.set_ylim([0, 4])
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10) for color in self.colors]
        plt.legend(legend_elements, self.legend_labels)
        plt.title('Pass Zones')
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.xticks([])
        plt.yticks([])
        plt.autoscale()

    def create_graph(self):
        self.__prep_dataframe__()
        self.plot_pass_zones()
        self.polish_graph()
        return __save_matPlot__(plt)

if __name__ == '__main__':
    labels = [
    'Flats-Left',
    'Flats-Right',
    'Middle-Left',
    'Middle-Right',
    'Middle-Middle',
    'Deep-Left',
    'Deep-Right'
    ]
    numeric_values = np.random.randint(low=0, high=100, size=7)
    df = pd.DataFrame({'Label': labels, 'Value': numeric_values})
    pz_obj = PassZone(df, 'Value')


