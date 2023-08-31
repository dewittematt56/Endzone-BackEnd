import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import pandas as pd
import numpy as np
from io import BytesIO
from .utils import save_matPlot
from matplotlib.font_manager import fontManager, FontProperties

font_path = "dependencies//branding//Audiowide-Regular.ttf"
fontManager.addfont(font_path)
prop = FontProperties(fname=font_path)
plt.rcParams['font.family'] = 'Audiowide'
sns.set(font=prop.get_name())

def endzone_diverging_colors():
    return ["#f5720d", "#14c7ed", "#cd9200", "#00c8d3", "#a1a802", "#00c6aa", "#72b645", "#35c079"]

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

def categorical_pieChart_wrapper(data: pd.DataFrame, category: str, title: str, isBooleanGraph: bool = False, useOther: bool = True) -> BytesIO:
    try:
        chart_data = group_by_df(data, category, useOther)
        return categorical_pieChart(title, chart_data, isBooleanGraph)
    except:
        return None

def categorical_pieChart(title: str, df: pd.DataFrame, isBooleanGraph: bool = False) -> BytesIO:
    try: 
        fig, ax = plt.subplots()
        colors = endzone_diverging_colors()
        wedges, labels, autopcts = ax.pie(df['Value'], labels=df.Category, autopct='%1.1f%%', startangle=90,
                wedgeprops={'edgecolor': 'white'}, pctdistance=0.75, textprops={'fontsize': 14}, colors = colors) 
        # If it's a boolean graph.
        for wedge in wedges:
            if isBooleanGraph:
                if wedge.get_label() == 'True':
                    wedge.set_facecolor("#0984E3")
                elif wedge.get_label() == 'False':
                    wedge.set_facecolor("#EC3813")
            if wedge.get_label() == 'Other':
                wedge.set_facecolor("#6b6d70")

        for label in labels:
            label.set_fontsize(18)
            label.set_fontfamily("Audiowide")
        centre_circle = plt.Circle((0,0),0.50,fc='white')
        fig = plt.gcf()
        plt.title(title, fontsize=18, fontdict={'weight': 'bold'})
        fig.gca().add_artist(centre_circle)

        ax.set_aspect('equal')  # Equal aspect ratio ensures that the pie chart is a circle
        return save_matPlot(plt)
    except KeyError:
        return ''

def barGraph(data, x, y, x_label: str, y_label: str):
    sns.barplot(x=data.index, y='Value', data=data)
    plt.title('Bar Graph Example with Pandas DataFrame')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    pass

def stackedBarGraph(df: pd.DataFrame, x_col: str, y_cols: 'list[str]', title: str, uniqueId_col: str = "Play_Number", y_label: str = 'Occurrences', include_total_plays: bool = False, total_plays_label: str = ""):
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        df = df[[uniqueId_col, x_col] + y_cols]
        grouped_df = df.groupby(x_col)[y_cols].sum()
        len_df = df.groupby(x_col).size()
        x = np.arange(len(grouped_df))  # x-coordinates for the bars
        opacity = 0.8  # Opacity of the bars

        # Plot stacked bars for each column
        bottom = np.zeros(len(grouped_df))
        for i, col in enumerate(y_cols):
            ax.bar(x, grouped_df[col], alpha=opacity, color=endzone_diverging_colors()[i],
                label=col, bottom=bottom)
            bottom += grouped_df[col]
        
        if include_total_plays:
            ax.bar(x, len_df, alpha=0.5, color='none', edgecolor='black', linewidth=2, label=total_plays_label)

        ax.set_xlabel(x_col.replace('_', ' '))
        ax.set_ylabel(y_label)
        ax.set_xticks(x)
        ax.set_xticklabels(grouped_df.index)
        ax.set_title(title)
        ax.legend()

        return save_matPlot(plt)
    except:
        return None

def crossTabQuery(df_x: pd.Series, df_y: pd.Series) -> pd.DataFrame:
    crossTab = pd.crosstab(df_x, df_y, normalize="index")
    crossTab = crossTab * 100
    crossTab.reset_index(inplace=True)
    return crossTab

def crossTabQueryAgg(df_x: pd.Series, df_y: pd.Series, df_val: pd.Series, agg: str) -> pd.DataFrame:
    crossTab = pd.crosstab(df_x, df_y, values=df_val, aggfunc=agg)
    crossTab.reset_index(inplace=True)
    return crossTab

def create_ridge_plot(df: pd.DataFrame, x: str, y: str, color_col: str):
    pal = sns.color_palette(endzone_diverging_colors())
    g = sns.FacetGrid(df, row=x, hue=color_col, aspect=7.5, height=1, palette=pal)
    g.map(sns.kdeplot, y,
      bw_adjust=.5, clip_on=False,
      fill=True, alpha=1, linewidth=1.5)
    g.map(sns.kdeplot, y, clip_on=False, color="w", lw=2, bw_adjust=.5)
    g.refline(y=0, linewidth=2, linestyle="-", color=None, clip_on=False)
    
    def label(x, color, label):
        ax = plt.gca()
        ax.text(0, .5, label, fontweight="bold", color=color,
                ha="left", va="center", transform=ax.transAxes)
    g.map(label, y)

    # Remove axes details that don't play well with overlap
    g.set_titles("")
    g.set(yticks=[], ylabel="")
    g.despine(bottom=True, left=True)

    # Show the plot
    return save_matPlot(plt)

def kdePlot(data) -> BytesIO:
    #g = sns.FacetGrid(data, hue='Play_Type', height=6, aspect=1.2, legend_out=True)
    sns.swarmplot(data=data, x="Distance", y="Down", hue="Play_Type")
    return save_matPlot(plt)

def groupedBarGraph(df: pd.DataFrame, x_col: str, y_col: str, title: str, uniqueId_col: str = "Play_Number", y_label: str = 'Occurrences'):
    try:
        fig, ax= plt.subplots()
        df = df[[uniqueId_col, x_col, y_col]]
        grouped_df = df.groupby([y_col, x_col]).count()
        grouped_df = grouped_df.unstack(level=0)
        ax = grouped_df.plot(kind='bar', rot=0, figsize=(10, 6), color=endzone_diverging_colors())

        plt.xlabel(x_col.replace('_', ' '))
        plt.ylabel(y_label)
        ax.legend(title=title, labels=[col[1] for col in grouped_df.columns])
        return save_matPlot(plt)
    except:
        return None

def create_xy_map(df: pd.DataFrame, x_spatial_col: str, y_spatial_col: str, categorical_col: str, sizing_column: str = None) -> None:
    # Currently Broken
    # Background Image
    fig, ax = plt.subplots()
    img = mpimg.imread('dependencies/other/FootballField.png')
    if sizing_column:
        sns.relplot(x=x_spatial_col, y=y_spatial_col, hue=categorical_col, size=sizing_column,
                sizes=(40, 400), alpha=.5, palette="muted",
                height=6, data=df)
    else:
        sns.relplot(x=x_spatial_col, y=y_spatial_col, hue=categorical_col,
            sizes=(40, 400), alpha=.5, palette="muted",
            height=6, data=df)
        
    return save_matPlot(plt)