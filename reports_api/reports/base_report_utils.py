
from io import BytesIO
import pandas as pd
from typing import Union
import PyPDF2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import warnings
from .utils import __save_matPlot__
warnings.filterwarnings('ignore')

# Used for encoding binary data
import base64
from matplotlib.font_manager import fontManager, FontProperties
import matplotlib.cm as cm
from matplotlib.cm import RdYlBu
import numpy as np

font_path = "reports_api//reports//static//branding//Audiowide-Regular.ttf"
fontManager.addfont(font_path)
prop = FontProperties(fname=font_path)
plt.rcParams['font.family'] = 'Audiowide'
sns.set(font=prop.get_name())

def get_pressure_away_strength(form_strength: str, pressure_left: bool, pressure_right: bool, pressure_middle: bool) -> bool:
    if form_strength  != 'Unknown':
        if form_strength == 'Left' and (pressure_right or pressure_middle): return True
        elif form_strength == 'Right' and (pressure_left or pressure_middle): return True
    return False

def get_pressure_into_strength(form_strength: str, pressure_left: bool, pressure_right: bool) -> bool:
    if form_strength  != 'Unknown':
        if form_strength == 'Left' and pressure_left: return True
        elif form_strength == 'Right' and pressure_right: return True
    return False
    
def get_plays_to_strength(form_strength: str, play_type: str, play_type_dir: str) -> bool:
    if form_strength  != 'Unknown' and play_type_dir != 'Unknown':
        return form_strength == play_type_dir
    else:
        return False

def get_number_rushers(d_formation: str, pressure_left: bool, pressure_right: bool, pressure_middle: bool) -> Union[int, None]:
    if d_formation in ["Nickel", "Dime", "Prevent", "Goal Line"]:
        return None
    else:
        return int(d_formation[0:1]) + pressure_left + pressure_middle + pressure_right

def get_down_group(distance: int) -> str:
    if distance <= 3: return "Short"
    elif distance > 3 and distance <= 6: return "Medium"
    elif distance > 6: return "Long"
    
def get_field_group(yard: int) -> str:
    if yard <= 33: return "Backed Up"
    elif yard > 33 and yard <= 66: return "Midfield"
    elif yard > 66: return "Scoring Position"

def get_edge_pressure(pressure_left: bool, pressure_right: bool) -> bool:
    if pressure_left or pressure_right: return True 
    else: return False   

def get_coverage_type(coverage: str) -> str:
    if "Man" in coverage: return "Man"
    elif "Zone" in coverage: return "Zone"
    else: return coverage 

def get_run_type(play_type: str) -> Union[str, None]:
    if "Outside" in play_type: return "Outside"
    elif "Inside" in play_type: return "Inside"
    elif "Option" in play_type: return "Option"
    else: return None

def get_personnel(running_backs: int, tight_ends: int) -> str:
    return str(running_backs) + str(tight_ends)

def get_score_state(home_score: int, home_team: str, away_score: int, away_team: str, team_of_interest: str):
    score_diff = home_score - away_score
    if score_diff == 0:
        return "Tie Game" 
    if team_of_interest == home_team:
        if score_diff >= 0 and score_diff <=8:
            return "One Possession Game"
        elif score_diff > 8:
            return "Up by two Possessions"
        elif score_diff < -8:
            return "Down by two Possessions"
        elif score_diff > 16:
            return "Up by 3+ Possessions"
        elif score_diff < - 16:
            return "Down by 3+ Possessions"
        else:
            return 'Unknown'
    elif team_of_interest == away_team:
        if score_diff <= 0 and score_diff <= -8:
            return "One Possession Game"
        elif score_diff < -8:
            return "Up by two Possessions"
        elif score_diff > 8:
            return "Down by two Possessions"        
        elif score_diff > 16:
            return "Down by 3+ Possessions"
        elif score_diff < - 16:
            return "Up by 3+ Possessions"
        else: 
            return "Unknown"

def enrich_data(df: pd.DataFrame, team_of_interest: str) -> pd.DataFrame:
    df["Number_Rushers"] = 0
    df["Down_Group"] = ""
    df["Field_Group"] = ""
    df["Pressure_Edge"] = ""
    df["Pressure_Existence"] = ""
    df["Coverage_Type"] = ""
    df["Run_Type"] = ""
    df["Personnel"] = ""
    df["Score_State"] = ""
    for index, row in df.iterrows():
        df.loc[index, "Number_Rushers"] = get_number_rushers(str(df.loc[index, "D_Formation"]), df.loc[index, "Pressure_Left"], df.loc[index, "Pressure_Right"], df.loc[index, "Pressure_Middle"])
        df.loc[index, "Down_Group"] = get_down_group(df.loc[index, "Distance"])
        df.loc[index, "Field_Group"] = get_field_group(df.loc[index, "Yard"])
        df.loc[index, "Pressure_Edge"] = get_edge_pressure(df.loc[index, "Pressure_Left"], df.loc[index, "Pressure_Right"])
        df.loc[index, "Pressure_Existence"] = df.loc[index, "Pressure_Edge"] or df.loc[index, "Pressure_Middle"]
        df.loc[index, "Coverage_Type"] = get_coverage_type( df.loc[index, "Coverage"])
        df.loc[index,"Run_Type"] = get_run_type(df.loc[index, "Play_Type"])
        df.loc[index, "Personnel"] = get_personnel(df.loc[index, "Running_Backs"], df.loc[index, "Tight_Ends"])
        df.loc[index, "Score_State"] = get_score_state(df.loc[index, "Home_Score"], df.loc[index, "Home_Team"], df.loc[index, "Away_Score"], df.loc[index, "Away_Team"], team_of_interest)
        df.loc[index, "To_Strength"] = get_plays_to_strength(df.loc[index, "Formation_Strength"], df.loc[index, "Play_Type"], df.loc[index, "Play_Type_Dir"])
        df.loc[index, "Pressure_Into_Strength"] = get_pressure_into_strength(df.loc[index, "Formation_Strength"], df.loc[index, "Pressure_Left"], df.loc[index, "Pressure_Right"])
        df.loc[index, "Pressure_Away_Strength"] = get_pressure_away_strength(df.loc[index, "Formation_Strength"], df.loc[index, "Pressure_Left"], df.loc[index, "Pressure_Right"], df.loc[index, "Pressure_Middle"])
    return df

def combine_pdf_pages(pages: list):
    pdf_writer = PyPDF2.PdfWriter()
    for pdf in pages:
        for page in pdf.pages:
            pdf_writer.add_page(page)

    combined_pdf = BytesIO()
    pdf_writer.write(combined_pdf)

    # Reset Bytes Position
    combined_pdf.seek(0)
    return combined_pdf.getvalue()

def calculate_nfl_efficency_row(down: int, distance: str, result: int) -> float:
    if down == 1: return result / distance >= .3
    elif down == 2: return result / distance >= .6
    elif down == 3: return result / distance >= 1
    elif down == 4: return result / distance >= 1

def ball_carrier_package(df: pd.DataFrame) -> pd.DataFrame:
    df['Efficiency'] = df.apply(lambda row: calculate_nfl_efficency_row(row['Down'], row['Distance'], row['Result']), axis=1)
    carries_by_ball_carrier = df.groupby('Ball_Carrier').size()
    team_average = df["Result"].mean()
    touchdowns_df = df[df['Event'] == 'Touchdown']
    touchdowns_by_ball_carrier = touchdowns_df.groupby('Ball_Carrier').size()
    fumbles_df = df[df['Event'] == 'Fumble']
    fumbles_by_ball_carrier = fumbles_df.groupby('Ball_Carrier').size()
    fumble_frequency = fumbles_by_ball_carrier / carries_by_ball_carrier
    total_yards = df.groupby('Ball_Carrier')['Result'].sum()
    average_result = df.groupby('Ball_Carrier')['Result'].mean()
    median_result = df.groupby('Ball_Carrier')['Result'].median()
    dev_result = df.groupby('Ball_Carrier')['Result'].apply(lambda x: x.mean() - team_average)
    nfl_efficiency_by_call_carrier = df.groupby('Ball_Carrier')['Efficiency'].apply(lambda x: (x.mean() / len(x)) * 100 )
    ball_carrier_df = pd.DataFrame({
        'Total Yards': total_yards,
        'Carries': carries_by_ball_carrier,
        'Touchdowns': touchdowns_by_ball_carrier,
        'Fumbles': fumbles_by_ball_carrier,
        'Fumble Frequency': fumble_frequency,
        'Average Result': average_result,
        'Median Result': median_result,
        'Difference from Team Average': dev_result,
        'Efficient Carries': nfl_efficiency_by_call_carrier,
    })
    return ball_carrier_df.fillna(0)

def passing_package(df: pd.DataFrame) -> pd.DataFrame:
    df['Efficiency'] = df.apply(lambda row: calculate_nfl_efficency_row(row['Down'], row['Distance'], row['Result']), axis=1)
    third_down_data = df[df['Down'] == 3]
    pressure_play_data = df[df['Pressure_Existence'] == True]
    passing_df = pd.DataFrame({
        'Total Yards': df["Result"].sum(),
        'Attempts': len(df),
        'Completions': df['Complete_Pass'].count(),
        'Completion Percentage': (df['Complete_Pass'].sum() / df['Complete_Pass'].count()) * 100,
        'Completion Percentage vs Pressure': (pressure_play_data['Complete_Pass'].sum() / pressure_play_data['Complete_Pass'].count()) * 100,
        'Third Down Completion Percentage': (third_down_data['Complete_Pass'].sum() / third_down_data['Complete_Pass'].count()) * 100,
        'Efficiency': (df['Efficiency'].sum() / df['Efficiency'].count()) * 100
    }, index=[0])
    return passing_df.fillna(0)


def get_nfl_efficiency(df: pd.DataFrame) -> str:
    total_length = len(df)
    if total_length > 0:
        first_plays = df.query('Down == 1')
        first = 0 if not len(first_plays) > 0 else len(first_plays.query("Result / Distance >= .3")) / len(first_plays)
        second_plays = df.query('Down == 2')
        second = 0 if not len(second_plays) > 0 else len(second_plays.query("Result / Distance >= .6")) / len(second_plays)
        third_plays = df.query('Down == 3')
        third = 0 if not len(third_plays) > 0 else len(third_plays.query("Result / Distance >= 1")) / len(third_plays)
        fourth_plays = df.query('Down == 4')
        fourth = 0 if not len(fourth_plays) > 0 else len(fourth_plays.query("Result / Distance >= 1")) / len(fourth_plays)
        return [round(sum([first, second, third, fourth]) / sum([len(first_plays) > 0, len(second_plays) > 0, len(third_plays) > 0, len(fourth_plays) > 0])  * 100), total_length]
    else: 
        return [0, total_length]
    
def get_efficiency(df: pd.DataFrame) -> "list[str]":
    total_len = len(df)
    if total_len > 0:
        return [(round((len(df.query('Result <= 3 | Result >= Distance')) / total_len) * 100)), total_len]
    else: 
        return [0, total_len]
    
def get_explosive_rate(df):
    total_plays = len(df)
    rush_plays = df.query('Run_Type == "Inside Run" | Run_Type == "Outside Run" | Run_Type == "Option"')
    rush_explosive = 0 if not len(rush_plays) > 0 else len(rush_plays.query("Result  >= 10"))
    pass_plays = df.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')
    pass_explosive = 0 if not len(pass_plays) > 0 else len(pass_plays.query("Result  >= 20"))
    return [round(sum([rush_explosive, pass_explosive]) / total_plays  * 100), sum([rush_explosive, pass_explosive])]

def get_negative_rate(df):
    total_plays = len(df)
    total_negative_plays = len(df.query("Result  < -1"))
    return [round(total_negative_plays / total_plays  * 100), total_negative_plays]

def get_efficiencies(df: pd.DataFrame) -> dict:
    efficiency_dict = {}
    efficiency_dict['EfficiencyOverall'] = get_efficiency(df)
    efficiency_dict["EfficiencyFirst"] = get_efficiency(df.query('Down == 1'))
    efficiency_dict["EfficiencySecond"] = get_efficiency(df.query('Down == 2'))
    efficiency_dict["EfficiencyThird"] = get_efficiency(df.query('Down == 3'))
    efficiency_dict['EfficiencyPressure'] = get_efficiency(df.query('Pressure_Left | Pressure_Right | Pressure_Middle'))
    efficiency_dict['EfficiencyPressureEdge'] = get_efficiency(df.query('Pressure_Left | Pressure_Right'))
    efficiency_dict['EfficiencyPressureMiddle'] = get_efficiency(df.query('Pressure_Middle'))
    efficiency_dict["InsideRunsEfficiency"] = get_efficiency(df.query('Run_Type == "Inside"'))
    efficiency_dict["OutsideRunsEfficiency"] = get_efficiency(df.query('Run_Type == "Outside"'))
    efficiency_dict["PassEfficiency"] = get_efficiency(df.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"'))
    efficiency_dict['NFLEfficiencyOverall'] = get_nfl_efficiency(df)
    efficiency_dict['NFLEfficiencyFirst'] = get_nfl_efficiency(df.query('Down == 1'))
    efficiency_dict['NFLEfficiencySecond'] = get_nfl_efficiency(df.query('Down == 2'))
    efficiency_dict["ThirdDownConversionRate"] = get_nfl_efficiency(df.query('Down == 3'))
    efficiency_dict["FourthDownConversionRate"] = get_nfl_efficiency(df.query('Down == 4'))
    efficiency_dict["explosivePlayRate"] = get_explosive_rate(df)
    efficiency_dict["negativePlayRate"] = get_negative_rate(df)
    return efficiency_dict

def get_yardage(df: pd.DataFrame):
    total_plays = len(df)
    if total_plays > 0:
        total =df["Result"].sum()
        perGame = round(df["Result"].sum() / df['Game_ID'].nunique(), 2)
        perPlay = round(df["Result"].sum() / len(df), 2)

        return [total, perGame, perPlay]
    else:
        return [0, 0, 0]

def breakdown_yardage(df: pd.DataFrame) -> dict:
    yardage_dict = {}
    yardage_dict["totalYards"] = get_yardage(df)
    yardage_dict["insideRunYards"] = get_yardage(df.query('Run_Type == "Inside"'))
    yardage_dict["outsideRunYards"] = get_yardage(df.query('Run_Type == "Outside"'))
    yardage_dict["passingYards"] = get_yardage(df.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"'))
    return yardage_dict

def endzone_color_ramp(ticks: int) -> list:
    return RdYlBu(np.linspace(0, 1, ticks))

def group_by_df(df: pd.DataFrame, column: str) -> pd.DataFrame:
    grouped_df = df.groupby(column).count()
    other_values = 0
    rows = []
    for index, row in grouped_df.iterrows():
        if not (grouped_df.loc[index, "Play_Number"] / len(df)) >= .1:
            other_values = other_values + grouped_df.loc[index, "Play_Number"]
        else:
            rows.append(pd.Series({'Category': index, 'Value': grouped_df.loc[index, "Play_Number"]}))
    
    if other_values > 0:
        rows.append(pd.Series({'Category': 'Other', 'Value': other_values}))
    return pd.DataFrame(rows)

def categorical_pieChart_wrapper(data: pd.DataFrame, category: str, title: str) -> BytesIO:
    chart_data = group_by_df(data, category)
    return categorical_pieChart(title, chart_data)

def categorical_pieChart(title: str, df: pd.DataFrame) -> BytesIO:
    try: 
        fig, ax = plt.subplots()
        colors = endzone_color_ramp(len(df))
        wedges, labels, autopcts = ax.pie(df['Value'], labels=df.Category, autopct='%1.1f%%', startangle=90,
                wedgeprops={'edgecolor': 'white'}, pctdistance=0.75, textprops={'fontsize': 14}, colors = colors)
        
        for label in labels:
            label.set_fontsize(18)
            label.set_fontfamily("Audiowide")
        centre_circle = plt.Circle((0,0),0.50,fc='white')
        fig = plt.gcf()
        plt.title(title, fontsize=18, fontdict={'weight': 'bold'})
        fig.gca().add_artist(centre_circle)

        ax.set_aspect('equal')  # Equal aspect ratio ensures that the pie chart is a circle
        return __save_matPlot__(plt)
    except KeyError:
        return ''

def barGraph(data, x, y, x_label: str, y_label: str):
    sns.barplot(x=data.index, y='Value', data=data)
    plt.title('Bar Graph Example with Pandas DataFrame')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    pass

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
    pal = sns.cubehelix_palette(start=2, rot=0.1, dark=0.2, light=0.8, reverse=True, hue=0.1)
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
    return __save_matPlot__(plt)

def kdePlot(data) -> BytesIO:
    #g = sns.FacetGrid(data, hue='Play_Type', height=6, aspect=1.2, legend_out=True)
    sns.swarmplot(data=data, x="Distance", y="Down", hue="Play_Type")

    return __save_matPlot__(plt)

def groupedBarGraph(df: pd.DataFrame, x_col: str, y_col: str, title: str, uniqueId_col: str = "Play_Number", y_label: str = 'Occurrences'):
    fig, ax= plt.subplots()
    df = df[[uniqueId_col, x_col, y_col]]
    grouped_df = df.groupby([y_col, x_col]).count()
    grouped_df = grouped_df.unstack(level=0)
    num_colors = len(grouped_df.columns.levels[1])
    cmap = cm.get_cmap('RdYlBu', num_colors)
    ax = grouped_df.plot(kind='bar', rot=0, figsize=(10, 6), color=[cmap(i) for i in range(num_colors)])
    plt.xlabel(x_col.replace('_', ' '))
    plt.ylabel(y_label)
    ax.legend(title=title, labels=[col[1] for col in grouped_df.columns])
    return __save_matPlot__(plt)

def create_xy_map(df: pd.DataFrame, x_spatial_col: str, y_spatial_col: str, categorical_col: str, sizing_column: str = None) -> None:
    # Currently Broken
    # Background Image
    fig, ax = plt.subplots()
    img = mpimg.imread('reports_api\\reports\\static\\other\\FootballField.png')
    if sizing_column:
        sns.relplot(x=x_spatial_col, y=y_spatial_col, hue=categorical_col, size=sizing_column,
                sizes=(40, 400), alpha=.5, palette="muted",
                height=6, data=df)
    else:
        sns.relplot(x=x_spatial_col, y=y_spatial_col, hue=categorical_col,
            sizes=(40, 400), alpha=.5, palette="muted",
            height=6, data=df)
        
    return __save_matPlot__(plt)