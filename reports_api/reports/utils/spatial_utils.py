import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from matplotlib.colors import LinearSegmentedColormap, rgb2hex
import matplotlib.image as mpimg
import matplotlib.patches as patches
from jenkspy import jenks_breaks
import pandas as pd
import numpy as np
from .utils import save_matPlot

def group_by_df(df: pd.DataFrame, column: str, useOther: bool = True) -> pd.DataFrame:
    grouped_df = df.groupby(column).count()
    other_values = 0
    rows = []
    
    for index, row in grouped_df.iterrows():
        if useOther and not (grouped_df.loc[index, "Play_Number"] / len(df)) >= .1:
            other_values = other_values + grouped_df.loc[index, "Play_Number"]
        else:
            rows.append(pd.Series({'Category': index, 'Value': grouped_df.loc[index, "Play_Number"]}))
    
    if other_values > 0 and useOther:
        rows.append(pd.Series({'Category': 'Other', 'Value': other_values}))
    return pd.DataFrame(rows)

class PassZone(object):
    def __init__(self, df: pd.DataFrame, value_column: str, label_column: str = 'Category', number_of_classes: int = 3, legend_labels: list = ['Low Attempts', 'Medium Attempts', 'High Attempts'], title: str = "Pass Zones"):
        fig, ax = plt.subplots()
        self.df = df
        self.value_column = value_column
        self.ax = ax
        self.fig = fig
        self.label_column = label_column
        self.legend_labels = legend_labels
        self.number_of_classes = number_of_classes
        self.title = title
        if self.number_of_classes > len(self.df[self.value_column].unique()):
            self.number_of_classes = len(self.df[self.value_column].unique())
        self.__prep_dataframe__()
        self.polish_graph()

    def add_label_to_pass_zone(self, label: str, label_x: float, label_y: float, text_color: str = 'white'):
        self.ax.annotate(label, (label_x, label_y), color=text_color, fontsize=10,
                ha='center')

    def __prep_dataframe__(self):
        breaks = jenks_breaks(self.df[self.value_column], n_classes=self.number_of_classes)
        cmap = LinearSegmentedColormap.from_list('test', ['#1283e2', '#805e7b', '#ed3a14'], self.number_of_classes)
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
        plt.title(self.title)
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
        return save_matPlot(plt)

class FieldZone(object):
    def __init__(self, df: pd.DataFrame, value_column: str, label_column: str = 'Category', number_of_classes: int = 3, legend_labels: list = ['Low Attempts', 'Medium Attempts', 'High Attempts'], title: str = "Field Map"):
        fig, ax = plt.subplots()
        self.df = df
        self.value_column = value_column
        self.ax = ax
        self.fig = fig
        self.label_column = label_column
        self.legend_labels = legend_labels
        self.number_of_classes = number_of_classes
        self.title = title
        if self.number_of_classes > len(self.df[self.value_column].unique()):
            self.number_of_classes = len(self.df[self.value_column].unique())
        self.__prep_dataframe__()
        self.polish_graph()

    def add_label(self, label: str, label_x: float, label_y: float, text_color: str = 'white'):
        self.ax.annotate(label, (label_x, label_y), color=text_color, fontsize=10,
                ha='center')

    def add_pie_charts():
        return

    def _set_endzone_box_(self, x_centroid, y_centroid, title: str, rotation: int = 0):
        self.ax.annotate(title, (x_centroid, y_centroid), color='black', fontsize=10,
                ha='center', rotation = rotation)

    def __prep_dataframe__(self):
        breaks = jenks_breaks(self.df[self.value_column], n_classes=self.number_of_classes)
        cmap = LinearSegmentedColormap.from_list('test', ['#1283e2', '#ed3a14'], self.number_of_classes)
        self.colors = [rgb2hex(cmap(x)) for x in range(self.number_of_classes + 1)]
        self.df['Color'] = np.searchsorted(breaks, self.df[self.value_column])
        self.df['Color'] = self.df['Color'].apply(lambda x: self.colors[x])

    def __get_color__(self, pass_zone: str):
        try:
            value = self.df.loc[self.df[self.label_column] == pass_zone, 'Color'].iloc[0]
            if(value): return (value)
            return ;'#ffffff'
        except IndexError:
            return'#ffffff'

    def __get_value__(self, field_zone: str):
        try:
            value = self.df.loc[self.df[self.label_column] == field_zone, self.value_column].iloc[0]
            if(value): return value
            return 0
        except IndexError:
            return 0
        
    def add_label_to_pass_zone(self, label: str, label_x: float, label_y: float, text_color: str = 'white'):
        self.ax.annotate(label, (label_x, label_y), color=text_color, fontsize=10,
                ha='center')

    def __set_box_details__(self, field_zone, x_centroid, y_centroid):
        color = self.__get_color__(field_zone)
        text_color = 'white'
        if color == '#ffffff':
            text_color = 'black'
        self.ax.annotate(self.__get_value__(field_zone), (x_centroid, y_centroid), color=text_color, fontsize=24, ha='center')
        return color
    
    def plot_field_zones(self):
        self._set_endzone_box_(-.25, 1, 'Own Endzone', 90)
        self._set_endzone_box_(4.75, .75, 'Opponent Endzone', 270)
        back_left = Polygon([(0, 0), (0, 1), (1.5, 1), (1.5, 0)], closed=True, facecolor = self.__set_box_details__('Backed Up-Right', .75, .5), edgecolor = 'black')
        back_middle = Polygon([(1.5, 0), (1.5, 1), (3, 1), (3, 0)], closed=True, facecolor = self.__set_box_details__('Midfield-Right', 2.25, .5), edgecolor = 'black')
        back_right = Polygon([(3, 0), (3, 1), (4.5, 1), (4.5, 0)], closed=True, facecolor = self.__set_box_details__('Scoring Position-Right', 3.75, .5), edgecolor = 'black')
        
        
        middle_left = Polygon([(0, 1), (0, 2), (1.5, 2), (3, 1)], closed=True, facecolor = self.__set_box_details__('Backed Up-Middle', .75, 1.5), edgecolor = 'black')
        middle_middle = Polygon([(1.5, 1), (1.5, 2), (3, 2), (3, 1)], closed=True, facecolor =  self.__set_box_details__('Midfield-Middle', 2.25, 1.5), edgecolor = 'black')
        middle_right = Polygon([(3, 1), (3, 2), (4.5, 2), (4.5, 1)], closed=True, facecolor= self.__set_box_details__('Scoring Position-Middle', 3.75, 1.5), edgecolor = 'black')

        forward_left = Polygon([(0, 2), (0, 3), (1.5, 3), (3, 2)], facecolor= self.__set_box_details__('Backed Up-Left', .75, 2.5), edgecolor = 'black')
        forward_middle = Polygon([(1.5, 2), (1.5, 3), (3, 3), (3, 2)], facecolor= self.__set_box_details__('Midfield-Left', 2.25, 2.5), edgecolor = 'black')
        forward_right = Polygon([(3, 2), (3, 3), (4.5, 3), (4.5, 2)], facecolor= self.__set_box_details__('Scoring Position-Left', 3.75, 2.5), edgecolor = 'black')

        self.ax.add_patch(back_left)
        self.ax.add_patch(back_middle)
        self.ax.add_patch(back_right)
        self.ax.add_patch(middle_left)
        self.ax.add_patch(middle_middle)
        self.ax.add_patch(middle_right)
        self.ax.add_patch(forward_left)
        self.ax.add_patch(forward_middle)
        self.ax.add_patch(forward_right)

    def polish_graph(self):
        self.ax.set_aspect('equal')
        self.ax.set_xlim([0, 4])
        self.ax.set_ylim([0, 4])
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10) for color in self.colors]
        plt.legend(legend_elements, self.legend_labels, loc='lower center')
        plt.title(self.title)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.xticks([])
        plt.yticks([])
        plt.autoscale()

    def create_graph(self):
        self.__prep_dataframe__()
        self.plot_field_zones()
        self.polish_graph()
        img = mpimg.imread('dependencies/other/FootballField.png')
        self.ax.imshow(img, extent=[-.56, 5.06, 0, 3], zorder = 1, alpha=0.33)
        return save_matPlot(plt)


class FieldZone_PieChart(object):
    def __init__(self, df: pd.DataFrame, value_column: str, title: str = "Field Map", isBooleanGraph: bool = False, useOther: bool = False):
        fig, ax = plt.subplots()
        self.df = df
        self.value_column = value_column
        self.ax = ax
        self.fig = fig
        self.title = title
        self.color_dict = {}
        self.colors = ["#1283e2", "#ed3a14", "#34f199", "#c7dd91", "#4be8f9", "#c5d5f0", "#6c9999", "#997cfb", "#3f5562", "#da8b57"]
        self.polish_graph()
        self.isBooleanGraph = isBooleanGraph
        self.useOther = useOther
        self.df["Field_Zone"] = self.df["Field_Group"] + "-" + self.df["Hash"]

    def add_label(self, label: str, label_x: float, label_y: float, text_color: str = 'white'):
        self.ax.annotate(label, (label_x, label_y), color=text_color, fontsize=10,
                ha='center')

    def _set_endzone_box_(self, x_centroid, y_centroid, title: str, rotation: int = 0):
        self.ax.annotate(title, (x_centroid, y_centroid), color='black', fontsize=10,
                ha='center', rotation = rotation)
        
    def add_label_to_pass_zone(self, label: str, label_x: float, label_y: float, text_color: str = 'white'):
        self.ax.annotate(label, (label_x, label_y), color=text_color, fontsize=10,
                ha='center')

    def __set_box_details__(self, field_zone: str, x_centroid, y_centroid):
        df_trim = self.df[self.df["Field_Zone"] == field_zone]
        df_grouped = group_by_df(df_trim, self.value_column, self.useOther)
        if len(df_grouped) > 0:
            colors = [self.get_color(zone) for zone in df_grouped["Category"]]
            patches, _, _ = self.ax.pie(df_grouped["Value"], autopct='', radius=0.4, center=(x_centroid, y_centroid), colors=colors, wedgeprops={'edgecolor': 'white'})
            for patch in patches:
                patch.set_zorder(10)  # Move the pie chart to the front
                if self.isBooleanGraph:
                    if patch.get_label() == 'True':
                        patch.set_facecolor("#0984E3")
                    elif patch.get_label() == 'False':
                        patch.set_facecolor("#EC3813")

        return '#ffffff'
    
    def plot_field_zones(self):
        self._set_endzone_box_(-.25, 1, 'Own Endzone', 90)
        self._set_endzone_box_(4.75, .75, 'Opponent Endzone', 270)
        back_left = Polygon([(0, 0), (0, 1), (1.5, 1), (1.5, 0)], closed=True, facecolor = self.__set_box_details__('Backed Up-Right', .75, .5), edgecolor = 'black')
        back_middle = Polygon([(1.5, 0), (1.5, 1), (3, 1), (3, 0)], closed=True, facecolor = self.__set_box_details__('Midfield-Right', 2.25, .5), edgecolor = 'black')
        back_right = Polygon([(3, 0), (3, 1), (4.5, 1), (4.5, 0)], closed=True, facecolor = self.__set_box_details__('Scoring Position-Right', 3.75, .5), edgecolor = 'black')
        
        
        middle_left = Polygon([(0, 1), (0, 2), (1.5, 2), (3, 1)], closed=True, facecolor = self.__set_box_details__('Backed Up-Middle', .75, 1.5), edgecolor = 'black')
        middle_middle = Polygon([(1.5, 1), (1.5, 2), (3, 2), (3, 1)], closed=True, facecolor =  self.__set_box_details__('Midfield-Middle', 2.25, 1.5), edgecolor = 'black')
        middle_right = Polygon([(3, 1), (3, 2), (4.5, 2), (4.5, 1)], closed=True, facecolor= self.__set_box_details__('Scoring Position-Middle', 3.75, 1.5), edgecolor = 'black')

        forward_left = Polygon([(0, 2), (0, 3), (1.5, 3), (3, 2)], facecolor= self.__set_box_details__('Backed Up-Left', .75, 2.5), edgecolor = 'black')
        forward_middle = Polygon([(1.5, 2), (1.5, 3), (3, 3), (3, 2)], facecolor= self.__set_box_details__('Midfield-Left', 2.25, 2.5), edgecolor = 'black')
        forward_right = Polygon([(3, 2), (3, 3), (4.5, 3), (4.5, 2)], facecolor= self.__set_box_details__('Scoring Position-Left', 3.75, 2.5), edgecolor = 'black')

        self.ax.add_patch(back_left)
        self.ax.add_patch(back_middle)
        self.ax.add_patch(back_right)
        self.ax.add_patch(middle_left)
        self.ax.add_patch(middle_middle)
        self.ax.add_patch(middle_right)
        self.ax.add_patch(forward_left)
        self.ax.add_patch(forward_middle)
        self.ax.add_patch(forward_right)

    def polish_graph(self):
        self.ax.set_aspect('equal')
        self.ax.set_xlim([0, 4])
        self.ax.set_ylim([0, 4])
        plt.title(self.title)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.xticks([])
        plt.yticks([])
        plt.autoscale()
        # Create legend based on the color dictionary
        legend_patches = []
        for field_zone, color in self.color_dict.items():
            patch = patches.Patch(color=color, label=field_zone)
            legend_patches.append(patch)

        legend = self.ax.legend(handles=legend_patches, loc='upper right')
        legend.set_zorder(10)
        
    def get_color(self, field_zone: str):
        color = self.color_dict.get(field_zone)
        if not color:
            color = self.colors.pop()
            self.color_dict[field_zone] = color
        return color

    def create_graph(self):
        self.plot_field_zones()
        self.polish_graph()
        img = mpimg.imread('dependencies/other/FootballField.png')
        self.ax.imshow(img, extent=[-.56, 5.06, 0, 3], zorder = 1, alpha=0.33)
        return save_matPlot(plt)

if __name__ == '__main__':
    labels = [
        'Backed Up-Right',
        'Midfield-Right',
        'Scoring Position-Right',
        'Backed Up-Middle',
        'Midfield-Middle',
        'Scoring Position-Middle',
        'Backed Up-Left',
        'Midfield-Left',
        'Scoring Position-Left'
    ]
    numeric_values = np.random.randint(low=0, high=100, size=9)
    df = pd.DataFrame({'Label': labels, 'Value': numeric_values})
    pz_obj = FieldZone(df, 'Value', "Label").create_graph()


