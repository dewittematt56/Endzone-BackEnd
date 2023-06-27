
import pandas as pd
from typing import Union
import warnings
warnings.filterwarnings('ignore')
# Used for encoding binary data
import numpy as np

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

def calculate_nfl_efficency_row(down: int, distance: str, result: int) -> bool:
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
    return pd.DataFrame({
        'Total Yards': total_yards,
        'Carries': carries_by_ball_carrier,
        'Touchdowns': touchdowns_by_ball_carrier,
        'Fumbles': fumbles_by_ball_carrier,
        'Fumble Frequency': fumble_frequency,
        'Yards per Carry': average_result,
        'Median Yards Per Carry': median_result,
        'Difference from Team Average': dev_result,
        'Efficient Carries': nfl_efficiency_by_call_carrier,
    }).fillna(0).sort_values('Total Yards', ascending=False)

def receiver_package(df: pd.DataFrame) -> pd.DataFrame:
    df['Efficiency'] = df.apply(lambda row: calculate_nfl_efficency_row(row['Down'], row['Distance'], row['Result']), axis=1)
    df_thrown = df[df["Pass_Zone"] != 'Non-Passing-Play']
    df_receptions = df_thrown[(df_thrown["Result"]  != 0)]
    touchdowns_df = df_receptions[df_receptions['Event'] == 'Touchdown']
    team_average = df_receptions["Result"].mean()

    return pd.DataFrame({
        'Targets': df_thrown.groupby("Ball_Carrier").size(),
        'Receptions': df_receptions.groupby('Ball_Carrier').size(),
        'Total Yards': df_thrown.groupby('Ball_Carrier')['Result'].sum(),
        'Touchdowns': touchdowns_df.groupby('Ball_Carrier').size(),
        'Yards per Catch': df_receptions.groupby('Ball_Carrier')['Result'].median(),
        'Median Yards Per Catch': df_receptions.groupby('Ball_Carrier')['Result'].median(),
        "Difference from Team Average": df_receptions.groupby('Ball_Carrier')['Result'].apply(lambda x: x.mean() - team_average),
        "Efficient Receptions": df_thrown.groupby('Ball_Carrier')['Efficiency'].apply(lambda x: (x.mean() / len(x)) * 100 )
    }).fillna(0).sort_values('Total Yards', ascending=False)

def passing_package(df: pd.DataFrame) -> pd.DataFrame:
    try:
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
    except Exception:
        return None

def subset_redzone_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["Yard"] >= 80]
    # Define the conditions and corresponding values
    conditions = [(df['Yard'].between(80, 90, inclusive='both')),(df['Yard'].between(90, 95, inclusive='both')),(df['Yard'] > 95)]
    df['Redzone_Position'] = np.select(conditions, ['Yard Marker 20-10', 'Yard Marker 10-5', 'Goaline'], default='')
    return df

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
    if total_plays > 0:
        return [round(sum([rush_explosive, pass_explosive]) / total_plays  * 100), sum([rush_explosive, pass_explosive])]
    else:
        return [0, 0]
    
def get_negative_rate(df):
    total_plays = len(df)
    total_negative_plays = len(df.query("Result  < -1"))
    if total_plays > 0:
        return [round(total_negative_plays / total_plays  * 100), total_negative_plays]
    else:
        return [0, 0]
    
def get_efficiencies(df: pd.DataFrame) -> dict:
    efficiency_dict = {}
    efficiency_dict['EfficiencyOverall'] = get_nfl_efficiency(df)
    efficiency_dict["EfficiencyFirst"] = get_nfl_efficiency(df.query('Down == 1'))
    efficiency_dict["EfficiencySecond"] = get_nfl_efficiency(df.query('Down == 2'))
    efficiency_dict["EfficiencyThird"] = get_nfl_efficiency(df.query('Down == 3'))
    efficiency_dict['EfficiencyPressure'] = get_nfl_efficiency(df.query('Pressure_Left | Pressure_Right | Pressure_Middle'))
    efficiency_dict['EfficiencyPressureEdge'] = get_nfl_efficiency(df.query('Pressure_Left | Pressure_Right'))
    efficiency_dict['EfficiencyPressureMiddle'] = get_nfl_efficiency(df.query('Pressure_Middle'))
    efficiency_dict["InsideRunsEfficiency"] = get_nfl_efficiency(df.query('Run_Type == "Inside"'))
    efficiency_dict["OutsideRunsEfficiency"] = get_nfl_efficiency(df.query('Run_Type == "Outside"'))
    efficiency_dict["PassEfficiency"] = get_nfl_efficiency(df.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"'))
    efficiency_dict["ThirdDownConversionRate"] = get_nfl_efficiency(df.query('Down == 3'))
    efficiency_dict["FourthDownConversionRate"] = get_nfl_efficiency(df.query('Down == 4'))
    efficiency_dict["explosivePlayRate"] = get_explosive_rate(df)
    efficiency_dict["negativePlayRate"] = get_negative_rate(df)
    return efficiency_dict

def get_situational_efficiencies(df: pd.DataFrame) -> pd.DataFrame:
    df_len = len(df)
    situational_dict = {}
    situational_dict["average"] = [df["Result"].mean(), df_len]
    situational_dict["nfl_efficiency"] = get_nfl_efficiency(df)
    situational_dict["nfl_efficiency_zone"] = get_nfl_efficiency(df[df['Coverage'].str.contains('Zone')])
    situational_dict["nfl_efficiency_man"] = get_nfl_efficiency(df[df['Coverage'].str.contains('Man')])
    situational_dict["nfl_efficiency_pressure"] = get_nfl_efficiency(df.query('Pressure_Existence == True'))
    situational_dict["nfl_efficiency_edge_pressure"] = get_nfl_efficiency(df.query('Pressure_Edge == True'))
    situational_dict["nfl_efficiency_middle_pressure"] = get_nfl_efficiency(df.query('Pressure_Middle == True'))
    if(df_len > 1):
        situational_dict["conversion_rate"] = [len(df.query('Result >= Distance')) / df_len, df_len]
    else:
        situational_dict["conversion_rate"] = [0, df_len]
        
    return situational_dict

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

def isHomeTeam(game, team_of_interest) -> bool:
    try:
        if game.loc[0]["Home_Team"] == team_of_interest:
            return True
        return False
    except Exception:
        return False
    
def points_package(df: pd.DataFrame, team_of_interest: str, game_data: pd.DataFrame):
    total_points_allowed = get_total_points(df, team_of_interest, game_data)
    total_games = len(df["Game_ID"].unique())
    total_drives = len(df["Drive"].unique())
    total_plays = len(df)
    points_dict = {}
    points_dict["points_per_game"] = [total_points_allowed / total_games, total_games]
    points_dict["points_per_drive"] = [total_points_allowed / total_drives, total_drives]
    points_dict["points_per_play"] = [total_points_allowed / total_plays, total_plays]
    return points_dict

def get_total_points(df: pd.DataFrame, team_of_interest: str, game_data: pd.DataFrame):
    grouped_df = df.groupby('Game_ID')
    print(grouped_df)
    max_rows = grouped_df.apply(lambda x: x.loc[x['Play_Number'].idxmax()])
    print(max_rows)
    points = 0
    for index, row in max_rows.iterrows():
        game_id = row['Game_ID']
        print(game_id)
        game_info = game_data.loc[game_data['Game_ID'] == game_id]
        print(game_info)
        if isHomeTeam(game_info, team_of_interest):
            points += row["Home_Score"]
        else:
            points += row["Away_Score"]
    return points

def calculate_qbr(df: pd.DataFrame):
    df['Complete_Pass'] = (~df['Pass_Zone'].isin(['Not Thrown', 'Unknown'])) & (df["Result"] != 0)
    total_yards = df["Result"].sum()
    total_touchdowns = len(df[df["Event"] == "Touchdown"])
    total_completions = df["Complete_Pass"].sum()
    total_interceptions = len(df[df["Event"] == "Interceptions"])
    total_attempts = len(df)
    return round((((8.4 * total_yards) + (330 * total_touchdowns) + (100 * total_completions) - (200 * total_interceptions)) / total_attempts), 2)