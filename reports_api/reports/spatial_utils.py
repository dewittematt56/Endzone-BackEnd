import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# img = mpimg.imread('reports_api\\reports\\static\\other\\FootballField.png')
# # Endzone Cords System
# fig, ax = plt.subplots()
# plt.imshow(img, extent=[0, 1.25, 0, 0.7])
# x = [0.1, 0.2, 0.3, 0.4, 0.5]
# y = [0.5, 0.4, 0.3, 0.2, 0.1]
# ax.set_xticks([])
# ax.set_yticks([])

# plt.scatter(x, y, c=["Blue"], s=33, marker='x')
# #plt.plot(x, y, 'ro', marker = 'x', c=["Blue"], s=1)
# plt.show()


import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

def create_field_map(df: pd.DataFrame) -> None:
    # Background Image
    fig, ax = plt.subplots()
    img = mpimg.imread('reports_api\\reports\\static\\other\\FootballField.png')
    plt.imshow(img, extent=[0, 1.25, 0, 0.7])
    sns.scatterplot(data=df, x='x', y='y', hue='Play_Type', palette=palette)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')
# Show the plot
# Generate a color palette
palette = sns.color_palette("hls", 3)

# Create a sample DataFrame
data = {'x': [0.1, 0.2, 0.3, 0.4, 0.5], 'y': [0.5, 0.4, 0.3, 0.2, 0.1], 'Play_Type': ['Inside Run', 'Outside Run', 'Pass', 'Pass', 'Inside Run']}
df = pd.DataFrame(data)

# Create a scatter plot with colors based on Play_Type
img = mpimg.imread('reports_api\\reports\\static\\other\\FootballField.png')
fig, ax = plt.subplots()
plt.imshow(img, extent=[0, 1.25, 0, 0.7])
sns.scatterplot(data=df, x='x', y='y', hue='Play_Type', palette=palette, marker='x')
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel('')
ax.set_ylabel('')
# Show the plot
plt.show()