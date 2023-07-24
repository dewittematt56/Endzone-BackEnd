import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def make_pie(sizes, labels, colors, radius=1):
    col = [[i/255 for i in c] for c in colors]
    plt.axis('equal')
    width = 0.35
    kwargs = dict(colors=col, startangle=180)
    outside, _ = plt.pie(sizes, radius=radius, pctdistance=1-width/2, labels=labels, **kwargs)
    plt.setp(outside, width=width, edgecolor='white')

def make_donut_chart(dataframe, group_column, subgroup_column):
    # Extract unique values and counts from the DataFrame
    group_labels = dataframe[group_column].value_counts().index.tolist()
    group_sizes = dataframe[group_column].value_counts().tolist()
    group_colors = [(226, 33, 7), (60, 121, 189)]  # Modify as needed

    subgroup_labels = dataframe[subgroup_column].value_counts().index.tolist()
    subgroup_sizes = dataframe[subgroup_column].value_counts().tolist()
    subgroup_colors = [(226, 33, 7), (60, 121, 189), (25, 25, 25)]  # Modify as needed

    make_pie(group_sizes, group_labels, group_colors, radius=1.2)
    make_pie(subgroup_sizes, subgroup_labels, subgroup_colors, radius=1)

if __name__ == '__main__':
    # Create a sample DataFrame
    data = [
        ('3240', '4f9da333-e1b5-4e81-83d3-e630b44d9b87', 33, 19, 'Burnsville', 65, 'Right', 2, 5, 4, 'Unknown', '3-4', 'Double Wide', 'Left', 0, 0, 'Outside Run', None, 'Left', 'Non-Passing-Play', 'Zone 4', False, False, False, 2, 'Turnover', 24, 8.85672996129329, 5.931039241194341, 6.461807247892547, 5.898282310919432, 0, 0, 'Endzone-System', '2022-01-01 00:00:00'),
        ('3208', '4f9da333-e1b5-4e81-83d3-e630b44d9b87', 1, 1, 'Burnsville', 20, 'Middle', 1, 10, 1, 'Unknown', '3-4', 'Spread', 'Right', 0, 0, 'Inside Run', None, 'Right', 'Non-Passing-Play', 'Zone 4', False, False, False, 24, 'None', 1, 2.129406808495282, 5.001047203121441, 2, 5, 0, 0, 'Endzone-System', '2022-01-01 00:00:00'),
        ('3210', '4f9da333-e1b5-4e81-83d3-e630b44d9b87', 3, 1, 'Burnsville', 20, 'Left', 3, 10, 1, 'Unknown', '3-4', 'Spread', 'Right', 0, 0, 'Boot Pass', None, None, 'Non-Passing-Play', 'Zone 3', True, True, False, 7, 'None', 7, 2.6626496490734435, 4.238336493543856, 1.97844189208686, 5.1934979723793, 0, 0, 'Endzone-System', '2022-01-01 00:00:00'),
        ('3214', '4f9da333-e1b5-4e81-83d3-e630b44d9b87', 7, 3, 'Burnsville', 42, 'Left', 3, 8, 1, 'Unknown', '3-4', 'Triangle', 'Right', 0, 0, 'Pocket Pass', None, None, 'Non-Passing-Play', 'Zone 4', False, True, False, 7, 'None', -7, 3.452527878751961, 4.381024056435448, 4.178953046564239, 4.634748738682478, 0, 0, 'Endzone-System', '2022-01-01 00:00:00'),
        ('3224', '4f9da333-e1b5-4e81-83d3-e630b44d9b87', 17, 11, 'Burnsville', 25, 'Middle', 2, 14, 2, 'Unknown', '3-4', 'Triangle', 'Right', 0, 0, 'Inside Run', None, 'Right', 'Non-Passing-Play', 'Zone 3', False, False, False, 24, 'None', 10, 3.4524976750890435, 5.260632684973938, 2.487194570262408, 4.270679693994684, 0, 0, 'Endzone-System', '2022-01-01 00:00:00'),
        ('3215', '4f9da333-e1b5-4e81-83d3-e630b44d9b87', 8, 5, 'Burnsville', 30, 'Middle', 1, 10, 1, 'Unknown', '3-4', 'Double Wide', 'Right', 0, 0, 'Inside Run', None, 'Left', 'Non-Passing-Play', 'Zone 2', False, False, False, 24, 'None', 4, 3.367780569235252, 5.25059889760665, 2.9808614153492594, 5.876627168255336, 0, 0, 'Endzone-System', '2022-01-01 00:00:00'),
        ('3221', '4f9da333-e1b5-4e81-83d3-e630b44d9b87', 14, 9, 'Burnsville', 57, 'Left', 1, 10, 2, 'Unknown', '3-4', 'Triangle', 'Left', 0, 0, 'Outside Run', None, 'Left', 'Non-Passing-Play', 'Zone 3', False, False, False, 24, 'None', 12, 6.887326462395353, 4.216181026441359, 5.668912671862344, 5.863119974690784, 0, 0, 'Endzone-System', '2022-01-01 00:00:00'),
        ('3223', '4f9da333-e1b5-4e81-83d3-e630b44d9b87', 16, 11, 'Burnsville', 29, 'Left', 1, 10, 2, 'Unknown', '3-4', 'Triangle', 'Right', 0, 0, 'Boot Pass', None, None, 'Non-Passing-Play', 'Zone 4', False, False, False, 7, 'None', 6, 6.401963042727809, 5.472091219684629, 6.155507168387731, 5.449023402321489, 0, 0, 'Endzone-System', '2022-01-01 00:00:00'),
        ('3217', '4f9da333-e1b5-4e81-83d3-e630b44d9b87', 10, 6, 'Burnsville', 38, 'Right', 3, 7, 1, 'Unknown', '3-4', 'Triangle', 'Right', 0, 0, 'Pocket Pass', None, None, 'Non-Passing-Play', 'Zone 3', False, False, False, 2, 'None', 8, 2.135824283097893, 4.549718796144745, 3.312747641828791, 5.874813230613493, 0, 0, 'Endzone-System', '2022-01-01 00:00:00')
    ]

    df = pd.DataFrame(data, columns=[
        'ID', 'Game_ID', 'Play_Number', 'Drive', 'Possession', 'Yard', 'Hash', 'Down', 'Distance', 'Quarter',
        'Motion', 'D_Formation', 'O_Formation', 'Formation_Strength', 'Home_Score', 'Away_Score', 'Play_Type',
        'Play', 'Play_Type_Dir', 'Pass_Zone', 'Coverage', 'Pressure_Left', 'Pressure_Middle', 'Pressure_Right',
        'Ball_Carrier', 'Event', 'Result', 'Result_X', 'Result_Y', 'Play_X', 'Play_Y', 'Pass_X', 'Pass_Y',
        'Creator', 'Creation_Date'
    ])

    print(df)
    make_donut_chart(df, 'O_Formation', 'Coverage')
    plt.show()
