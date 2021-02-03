import os, argparse, sys
from download import DataDownloader
import matplotlib.pyplot as plt
import numpy as np

def get_data(data_source):
    """Sorts data by year and region.

    Keyword arguments:
    data_source - data of regions

    Returns: nested dictionary
    """
    dict = {}
    nested_dict = {}
    region_name = data_source[0][0]
    #Counts all data in dataset and sorts the result by year and region
    for x in range(len(data_source[0])):
        #region name is a key into dictionary if it changes,
        #it has to change destination for new data
        if region_name != data_source[0][x] or x+1 == len(data_source[0]):
            if data_source[4][x][:4] in dict and x+1 == len(data_source[0]):
                dict[data_source[4][x][:4]] += 1

            #if key do not exists in dictionary,
            #creats a copy on that key,
            #otherwise concatenate data
            if not region_name in nested_dict:
                nested_dict[region_name] = dict.copy()
            else:
                for key in dict:
                    if key in nested_dict[region_name]:
                        nested_dict[region_name][key] += dict[key]
                    else:
                        nested_dict[region_name][key] = dict[key]
            region_name = data_source[0][x]
            dict.clear()
            dict[data_source[4][x][:4]] = 1
        else:
            if data_source[4][x][:4] in dict:
                dict[data_source[4][x][:4]] += 1
            else:
                dict[data_source[4][x][:4]] = 1
    return nested_dict


def plot_stat(data_source, fig_location = None, show_figure = False):
    """Creates bar graph of accidents in regions for each year

    Keyword arguments:
    data_source - data of regions
    fig_location - path to save the file
    show_figure - determines whether the graph is displayed
    """

    if not len(data_source[1][0]):
        print("\n0 correct regions given")
        return

    dict = get_data(data_source[1])
    years_count = 0
    region_array = []
    year_array = []

    #gets array of years and array of regions
    for key in dict:
        region_array.append(key)
        if len(dict[key]) != len(year_array):
            for key2 in dict[key]:
                year_array.append(key2)

    y1 = []
    index = 0
    fig, ax = plt.subplots(len(year_array), figsize=(9,10), constrained_layout=True)
    #generates one graph for each year
    for year in year_array:
        #gets count of accidents in that year
        for region in dict:
            y1.append(dict[region][year])

        tmp = y1.copy()
        tmp.sort(reverse=True)
        numbers_of_bars = y1.copy()
        j = 0
        #gains the order of the region by count of accident
        for number in tmp:
            j+=1
            i = 0
            for number2 in numbers_of_bars:
                if number2 == number:
                    numbers_of_bars[i] = j
                i+=1

        rects = ax[index].bar(region_array, y1, width=0.9, bottom=0, align='center', color='C3')
        i = 0
        #prints number of accidents and order for each bar
        for rect in rects:
            value = y1[i]
            ax[index].annotate('{}'.format(value), xy=(rect.get_x() + rect.get_width() / 2, value), xytext=(0, -11), textcoords="offset points", ha='center', va='bottom')
            ax[index].annotate('{}'.format(numbers_of_bars[i]), xy=(rect.get_x() + rect.get_width() / 2, value), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
            i+=1
        ax[index].grid(which='both',axis='y', color='#444444', linestyle='dotted', linewidth=1)
        ax[index].set_ymargin(0.2)
        ax[index].set_title(year)
        ax[index].set_xlabel("kraje")
        ax[index].set_ylabel("pocet nehod")
        ax[index].spines['top'].set_visible(False)
        ax[index].spines['right'].set_visible(False)
        ax[index].spines['bottom'].set_position('zero')
        index+=1
        y1.clear()

    #displays a graphs if an argument has been entered
    if show_figure:
        plt.show()

    #saves graphs to .png file, if an path has been entered
    if fig_location != None:
        if not len(fig_location):
            print("ERROR: FIG_LOCATION: parametr nesmi byt prazdny", file=sys.stderr)
        elif fig_location[len(fig_location)-1]=='/':
            print("ERROR: FIG_LOCATION: nebyl zadan nazev souboru", file=sys.stderr)
        else:
            if fig_location[0]=='/':
                fig_location = fig_location[1:]
            i=0
            #creates directory, if directory do not exists
            while i<len(fig_location)-1:
                if fig_location[i] == '/':
                    if not os.path.isdir(fig_location[:i]):
                        os.mkdir(fig_location[:i])
                i+=1

            try:
                fig.savefig(fig_location)
            except FileNotFoundError:
                print("ERROR: FIG_LOCATION: nebyly vytvoreny slozky", file=sys.stderr)

    plt.close(fig)

#argument parser for --show_figure and --fig_location
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--show_figure', dest="show_figure", action="store_true",
                    help='show_figure help')
parser.add_argument('--fig_location', dest="fig_location", action="store",
                    help='show_figure help')

args = parser.parse_args()
data_source = DataDownloader().get_list(["PHA", "KVK", "STC"])
plot_stat(data_source, show_figure=args.show_figure, fig_location=args.fig_location)
