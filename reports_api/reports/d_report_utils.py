import pandas as pd
from .base_report_utils import calculate_nfl_efficency_row, get_points_per_game

def d_efficiency(down: int, distance: str, result: int):
    return not calculate_nfl_efficency_row(down, distance, result)

def query_d_yards_package(df: pd.DataFrame, clause: str, name: str) -> 'list[str]':
    df_subset = df.query(clause)
    if len(df_subset) < 1: return pd.DataFrame({'Play Type': [], 'Total Yards': [], 'Yards Per Attempt': [], 'Efficient Stops': [], 'Number of Plays': []})
    df_subset['Efficiency'] = df_subset.apply(lambda row: d_efficiency(row['Down'], row['Distance'], row['Result']), axis=1)
    total_efficient_plays = df_subset['Efficiency'].sum()
    total_yards = df_subset["Result"].sum()
    total_plays = len(df_subset["Result"])
    return pd.DataFrame({'Play Type': [name],'Total Yards': [df_subset["Result"].sum()], 'Yards Per Attempt': [total_yards / total_plays], 'Efficient Stops': [ total_efficient_plays / total_plays], 'Number of Plays': [total_plays]})

def d_overview_package(df: pd.DataFrame, team_of_interest: str, game_data):
    total_plays = len(df)
    forced_turnovers = len(df.query('Event == "Interception" | Event == "Fumble"'))
    ppg = get_points_per_game(df, team_of_interest, game_data)
    pressure_rate = df["Pressure_Existence"].sum() / total_plays
    edge_pressure_rate = df["Pressure_Edge"].sum() / total_plays
    middle_pressure_rate = df["Pressure_Middle"].sum() / total_plays
    
    data_pass = df[df["Play_Type"].isin(['Pocket Pass', 'Boot Pass'])]
    data_pass['Complete_Pass'] = (~data_pass['Pass_Zone'].isin(['Not Thrown', 'Unknown'])) & (data_pass["Result"] != 0)

    completion_percentage = data_pass['Complete_Pass'].sum() / len(data_pass)
    return


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