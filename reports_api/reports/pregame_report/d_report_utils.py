import pandas as pd
from ..utils.data_report_utils import *

def d_efficiency(down: int, distance: str, result: int):
    return not calculate_nfl_efficency_row(down, distance, result)

def query_d_yards_package(df: pd.DataFrame, clause: str, name: str) -> 'list[str]':
    df_subset = df.query(clause)
    if len(df_subset) < 1: return pd.DataFrame({'Play Type': [], 'Total Yards': [], 'Yards Per Attempt': [], 'Efficient Stops': [], 'Attempts': []})
    df_subset['Efficiency'] = df_subset.apply(lambda row: d_efficiency(row['Down'], row['Distance'], row['Result']), axis=1)
    total_efficient_plays = df_subset['Efficiency'].sum()
    total_yards = df_subset["Result"].sum()
    total_plays = len(df_subset["Result"])
    return pd.DataFrame({'Play Type': [name],'Total Yards': [df_subset["Result"].sum()], 'Yards Per Attempt': [total_yards / total_plays], 'Efficient Stops': [ (total_efficient_plays / total_plays) * 100], 'Attempts': [total_plays]})

def d_overview_package(df: pd.DataFrame, team_of_interest: str, game_data):
    """ Get Basic Stats for a overview of a Defense """
    total_plays = len(df)
    total_points_allowed = get_total_points(df, team_of_interest, game_data)
    data_pass = df[df["Play_Type"].isin(['Pocket Pass', 'Boot Pass'])]
    data_pass['Complete_Pass'] = (~data_pass['Pass_Zone'].isin(['Not Thrown', 'Unknown'])) & (data_pass["Result"] != 0)
    
    d_overview_dict = {}
    d_overview_dict["points_per_game"] = total_points_allowed / len(df["Game_ID"].unique())
    d_overview_dict["points_per_drive"] = total_points_allowed / len(df["Drive"].unique())
    d_overview_dict["third_down_conversion_allowed"] = get_nfl_efficiency(df.query('Down == 3'))
    d_overview_dict["fourth_down_conversion_allowed"] = get_nfl_efficiency(df.query('Down == 4'))
    d_overview_dict["forced_turnovers"] = len(df.query('Event == "Interception" | Event == "Fumble"'))
    d_overview_dict["pressure_rate"] = df["Pressure_Existence"].sum() / total_plays
    d_overview_dict["edge_pressure_rate"] = df["Pressure_Edge"].sum() / total_plays
    d_overview_dict["middle_pressure_rate"]  = df["Pressure_Middle"].sum() / total_plays
    d_overview_dict["completion_percentage"] = data_pass['Complete_Pass'].sum() / len(data_pass)
    d_overview_dict["qbr"] = calculate_qbr(data_pass[data_pass["Pass_Zone"] != 'Not Thrown'])
    return d_overview_dict

def d_yards_package(df: pd.DataFrame):
    yards_dict = {}
    yards_dict["All"] = query_d_yards_package(df, 'Play_Type != "OMEGA POG LUFFY"', "All")
    yards_dict['Inside Run'] = query_d_yards_package(df, 'Play_Type == "Inside Run"', "Inside Run")
    yards_dict['Outside Run'] = query_d_yards_package(df, 'Play_Type == "Outside Run"', "Outside Run")
    yards_dict['Pocket Pass'] = query_d_yards_package(df, 'Play_Type == "Pocket Pass"', "Pocket Pass")
    yards_dict['Boot Pass'] = query_d_yards_package(df, 'Play_Type == "Boot Pass"', "Boot Pass")
    yards_dict['Option'] = query_d_yards_package(df, 'Play_Type == "Option"', "Option")
    yards_dict['Total Rush'] = query_d_yards_package(df, 'Play_Type == "Inside Run" | Play_Type == "Outside"', "Total Rush")
    yards_dict['Total Pass'] = query_d_yards_package(df, 'Pass_Zone != "Non-Passing-Play"', "Total Pass")
    return pd.concat(yards_dict.values(), ignore_index=True)

def d_passing_pack(df: pd.DataFrame):
    df['Complete_Pass'] = (~df['Pass_Zone'].isin(['Not Thrown', 'Unknown'])) & (df["Result"] != 0)
    return pd.DataFrame({
        "Yards": df.groupby('Formation')['Result'].sum(),
        "Average Gain": df.groupby('Formation')['Result'].mean(),
        "Completion Percentage": df.groupby('Formation')['Complete_Pass'].apply(lambda x: (x.sum() / len(x)) * 100 ),
        "QBR": df.groupby("Formation").apply(calculate_qbr)
    })

def d_formation_pack(df: pd.DataFrame):
    df['Complete_Pass'] = (~df['Pass_Zone'].isin(['Not Thrown', 'Unknown'])) & (df["Result"] != 0)
    return pd.DataFrame({
        "Yards": df.groupby('Pass_Zone')['Result'].sum(),
        "Average Gain": df.groupby('Pass_Zone')['Result'].mean(),
        "Completions": df.groupby('Pass_Zone')['Complete_Pass'].sum(),
        "Attempts": df.groupby("Pass_Zone").size(),
        "Completion Percentage": df.groupby('Pass_Zone')['Complete_Pass'].apply(lambda x: (x.sum() / len(x)) * 100 ),
        "QBR": df.groupby("Pass_Zone").apply(calculate_qbr)
    })