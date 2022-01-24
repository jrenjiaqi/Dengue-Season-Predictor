import os
from sys import argv
import calendar

import csv

from numpy import genfromtxt

from matplotlib.figure import Figure
from scipy.signal import savgol_filter
from scipy import signal
import numpy as np


from tkinter import *
from tkinter import filedialog, messagebox, ttk
import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from tkinter import filedialog

rainfall_2018 = argv[1]
dengue_2018 = argv[2]
rainfall_2017 = argv[3]
dengue_2017 = argv[4]
user_input_upcoming_monsoon_str = argv[5]

# misc helper functions #
def convert_int_to_month(n):
    if n == 1: return "Jan"
    elif n == 2: return "Feb"
    elif n == 3: return "Mar"
    elif n == 4: return "Apr"
    elif n == 5: return "May"
    elif n == 6: return "Jun"
    elif n == 7: return "Jul"
    elif n == 8: return "Aug"
    elif n == 9: return "Sep"
    elif n == 10: return "Oct"
    elif n == 11: return "Nov"
    elif n == 12: return "Dec"
    else: return "ERROR"


def convert_num_to_name(num):
    return convert_int_to_month(num)

# end of misc helper functions #


# START OF ALGORITHM #
def xvaluefrom(derivingfile, isDengue=False):
    xes = []
    for item in derivingfile:
        xes.append(item[1])

    if isDengue:
        xes.pop(-1)  # last reading is no good
        # logic to condense the dengue csv into 12 months: every 3 months, average 5 readings instead
        counter = 0
        for x in xes:
            xes[counter] = xes[counter] + xes[counter+1] + xes[counter+2] + xes[counter+3]
            if (counter == 2) or (counter == 5) or (counter == 8) or (counter == 11):
                xes[counter] += xes[counter+4]
                xes.pop(counter+1)
                xes[counter] = round(xes[counter]/5)
            else:
                xes[counter] = round(xes[counter]/4)
            xes.pop(counter+1)
            xes.pop(counter+1)
            xes.pop(counter+1)
            counter += 1

    return xes


# all the above is placeholder for testing. might replace with whatever main function uses to provide values

from math import sqrt
from math import floor
from operator import itemgetter


def peakFinder(x):
    # for each month of rainy days..
    flaggedmonths = []
    for idx, val in enumerate(x):
        samplesize = 3  # EDIT THIS VALUE to change sample size. 3 looks appropriate
        # get the mean of this and previous 2 months, if any..
        samplemean = 0
        cnt = samplesize
        workingidx = idx
        # print(idx)
        while (workingidx != -1) and (cnt != 0):
            samplemean += x[workingidx]
            workingidx -= 1
            cnt -= 1

        if idx >= (samplesize-1):
            samplemean /= samplesize
        elif idx > 0:
            samplemean /= (idx+1)
        # print("end mean:", samplemean)

        # then get the total variance for this sample size..
        variance = 0
        cnt = samplesize
        workingidx = idx
        while (workingidx != -1) and (cnt != 0):
            variance += ((x[workingidx]-samplemean)**2)
            workingidx -= 1
            cnt -= 1

        if idx >= (samplesize-1):
            variance /= samplesize-1  # samplesize-1 as it's the sample size std dev. i didn't come up with it
        elif idx > 0:
            variance /= idx
        # print("end variance:", variance)

        # finally, get the SAMPLE std dev for this samplesize
        samplestddev = sqrt(variance)
        # print("end std dev:", samplestddev)

        sensitivity = 3.6  # EDIT THIS VALUE to make it more or less sensitive, lower is more sensitive. 3-4 can lah
        # if rainy days on this month exceed the std dev of the past 3 months, add it to the flagged list
        if val > (samplestddev*sensitivity):
            flaggedmonths.append(((idx+1), val))

    # now process flagged months into salient warning periods:
    # the first reading always gets flagged as it has no std dev to compare, dump it
    flaggedmonths.pop(0)

    # for the sake of readability:
    month = itemgetter(0)
    rains = itemgetter(1)
    # note to self: mth is a tuple
    for mthidx, mth in enumerate(flaggedmonths):
        # if consecutive months and lower rainy days, dump it
        if month(flaggedmonths[mthidx+1]) == (month(flaggedmonths[mthidx])+1):
            z = min(rains(flaggedmonths[mthidx+1]), (rains(flaggedmonths[mthidx])+1))
            # print("compared", rains(flaggedmonths[mthidx]), "and", (rains(flaggedmonths[mthidx+1])))
            if (rains(flaggedmonths[mthidx+1])) == z:
                # print("zeroing", flaggedmonths[mthidx+1])
                flaggedmonths[mthidx+1] = (0, 0)  # zero, don't pop, because the iterating gets wonky and skips
            else:
                # print("zeroing", flaggedmonths[mthidx])
                flaggedmonths[mthidx] = (0, 0)
        if mthidx == len(flaggedmonths)-2:
            break  # skip processing the last value

    # out of boolean hell, now just to present info:
    warningpeaks = []
    for warned in flaggedmonths:
        if month(warned) != 0:
            warningpeaks.append(month(warned))

    return warningpeaks


def getDelayfromPastData(y17rain, y17deng, y18rain, y18deng):
    delay = 0
    delayquotient = 0
    # find average gap between peak in rain, to peak in dengue
    for peak in y17rain:
        nextdengpeak = [i for i in y17deng if i > peak]
        nextdengpeak.append(0)  # in case no corresponding peak until eof
        # print("nextdengpeak is", nextdengpeak[0])
        if nextdengpeak[0] != 0:  # if there is a corresponding peak..
            delay += nextdengpeak[0] - peak  # add it to the delay
            delayquotient += 1

    for peak in y18rain:
        nextdengpeak = [i for i in y18deng if i > peak]
        nextdengpeak.append(0)  # in case no corresponding peak until eof
        # print("nextdengpeak is", nextdengpeak[0])
        if nextdengpeak[0] != 0:  # if there is a corresponding peak..
            delay += nextdengpeak[0] - peak  # add it to the delay
            delayquotient += 1

    return floor(delay / delayquotient)


y17rain = xvaluefrom(genfromtxt((argv[3]), delimiter=",", skip_header=1, dtype="S7,i8"))
y18rain = xvaluefrom(genfromtxt((argv[1]), delimiter=",", skip_header=1, dtype="S7,i8"))
y17deng = xvaluefrom(genfromtxt((argv[4]), delimiter=",", skip_header=1, dtype="S7,i8"), isDengue=True)
y18deng = xvaluefrom(genfromtxt((argv[2]), delimiter=",", skip_header=1, dtype="S7,i8"), isDengue=True)
userinput = [int(i) for i in argv[5].split(",")]

calculatedDelay = getDelayfromPastData(peakFinder(y17rain), peakFinder(y17deng), peakFinder(y18rain), peakFinder(y18deng))


def applyDelayToUserMonths(userMonths):
    return [x+calculatedDelay for x in userMonths]


print(peakFinder(y17rain))
print(peakFinder(y17deng))
print(peakFinder(y18rain))
print(peakFinder(y18deng))

print(getDelayfromPastData(y17rain,y18rain,y17deng,y18deng))
print(applyDelayToUserMonths(userinput))
# END OF ALGORITHM #

# here we do the graph in the left grid
# create global variables to hold the csvs
x_dengue_2018 = []
y_dengue_2018 = []
rainx_2018 = []
rainy_2018 = []
y_filtered_2018 = []

x_dengue_2017 = []
y_dengue_2017 = []
rainx_2017 = []
rainy_2017 = []
y_filtered_2017 = []

# print(os.getcwd())
with open(rainfall_2018, 'r') as csvfile3:
    plots = csv.reader(csvfile3, delimiter=',')
    next(plots)
    for row in plots:
        if row[1] == "NA":  # if there is no such week (due to calendar), then the value from previous week carry over
            row[1] = rainy_2018[-1]
            month = row[0]
            rainmonth = int(month[-2:]) * 4
            rainx_2018.append(int(rainmonth))
            rainy_2018.append(int(row[1]))
        else:
            month = row[0]
            rainmonth = int(month[-2:]) * 4
            rainx_2018.append(int(rainmonth))
            rainy_2018.append(int(row[1]))

with open(dengue_2018, 'r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    next(plots)
    for row in plots:
        if row[1] == "NA":  # if there is no such week (due to calendar), then the value from previous week carry over
            row[1] = y_dengue_2018[-1]
            x_dengue_2018.append(int(row[0]))
            y_dengue_2018.append(int(row[1]))
        else:
            x_dengue_2018.append(int(row[0]))
            y_dengue_2018.append(int(row[1]))

y_filtered_2018 = savgol_filter(y_dengue_2018, 53, 11)  # (the y list, number of x values (i.e. 53 weeks), filter intensity)

with open(rainfall_2017, 'r') as csvfile3:
    plots = csv.reader(csvfile3, delimiter=',')
    next(plots)
    for row in plots:
        if row[1] == "NA":  # if there is no such week (due to calendar), then the value from previous week carry over
            row[1] = rainy_2017[-1]
            month = row[0]
            rainmonth = int(month[-2:]) * 4
            rainx_2017.append(int(rainmonth))
            rainy_2017.append(int(row[1]))
        else:
            month = row[0]
            rainmonth = int(month[-2:]) * 4
            rainx_2017.append(int(rainmonth))
            rainy_2017.append(int(row[1]))

with open(dengue_2017, 'r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    next(plots)
    for row in plots:
        if row[1] == "NA":  # if there is no such week (due to calendar), then the value from previous week carry over
            row[1] = y_dengue_2017[-1]
            x_dengue_2017.append(int(row[0]))
            y_dengue_2017.append(int(row[1]))
        else:
            x_dengue_2017.append(int(row[0]))
            y_dengue_2017.append(int(row[1]))

y_filtered_2017 = savgol_filter(y_dengue_2017, 53, 11)  # (the y list, number of x values (i.e. 53 weeks), filter intensity)

# START OF GUI #
root = Tk()
root.title('Rainfall vs Dengue Predictor-Analyser')
root.geometry('{}x{}+{}+{}'.format(900, 570, 10, 20))     # WidthxHeight+Xpos+Ypos
root.resizable(False, False)                            # window will be FIXED size

# create all of the main containers
top_frame = Frame(root, bg='cyan', width=450, height=50, pady=3)
center = Frame(root, bg='purple', width=50, height=40, padx=3, pady=3)

# layout all of the main containers
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
top_frame.grid(row=0, sticky="nsew")
center.grid(row=1, sticky="nsew")


def view_rainfall_in_new_window():

    totalwidth = 553
    totalheight = 375

    window = tk.Toplevel(root)
    window.title("CSV data for Rainfall (both years)")
    window.geometry("{}x{}".format(totalwidth,totalheight))
    window.resizable(0, 0)

    class Table:

        def __init__(self, root):

            # code for creating table
            for i in range(total_rows):
                for j in range(total_columns):
                    self.e = Entry(root, width=15, fg='blue',
                                   font=('Arial', 16, 'bold'))

                    self.e.grid(row=i, column=j)
                    self.e.insert(END, lst[i][j])

                    # take the data
    rain_index_list = []
    rain_both_summ_list = [["Month number", "1st year (blue)", "2nd year (green)"]]
    for i in range(len(y18rain)):
        rain_index_list.append(i+1)
    for i in range(len(rain_index_list)):
        rain_both_summ_list.append([rain_index_list[i],y18rain[i], y17rain[i]])
    lst = rain_both_summ_list

    # find total number of rows and
    # columns in list
    total_rows = len(lst)
    total_columns = len(lst[0])

    t = Table(window)



def view_dengue_in_new_window():

    totalwidth = 1200
    totalheight = 430

    window1 = tk.Toplevel(root)
    window1.title("CSV data for Dengue Cases (both years)")
    window1.geometry("{}x{}".format(totalwidth,totalheight))
    window1.resizable(0, 0)

    class Table1:

        def __init__(self, root):

            # code for creating table
            for i in range(18+1):
                for j in range(3):
                    self.e = Entry(root, width=15, fg='blue',
                                   font=('Arial', 11, 'bold'))

                    self.e.grid(row=i, column=j)
                    self.e.insert(END, lst[i][j])

    class Table2:

        def __init__(self, root):

            # code for creating table
            for i in range(18+1):
                for j in range(3):
                    self.e = Entry(root, width=15, fg='blue',
                                   font=('Arial', 11, 'bold'))

                    self.e.grid(row=i, column=j)
                    self.e.insert(END, lst2[i][j])

    class Table3:

        def __init__(self, root):

            # code for creating table
            for i in range(17 + 1):
                for j in range(3):
                    self.e = Entry(root, width=15, fg='blue',
                                   font=('Arial', 11, 'bold'))

                    self.e.grid(row=i, column=j)
                    self.e.insert(END, lst3[i][j])

                    # take the data
    dengue_index_list = []
    dengue_both_summ_list = [["Week num", "1st year (orange)", "2nd year (red)"]]
    for i in range(18+1):
        dengue_index_list.append(i+1)
    for i in range(len(dengue_index_list)):
        dengue_both_summ_list.append([dengue_index_list[i],y_dengue_2018[i], y_dengue_2017[i]])
    lst = dengue_both_summ_list

    # find total number of rows and
    # columns in list
    total_rows = len(lst)
    total_columns = len(lst[0])

    frame_1 = Frame(window1, bg='cyan', width=totalwidth/3, height=totalheight)
    frame_1.grid(row=0, column=1, sticky="nsew")
    # create table in window
    t1 = Table1(frame_1)

    window1.grid_columnconfigure(0, weight=1)
    window1.grid_columnconfigure(2, weight=1)

    dengue_index_list2 = []
    dengue_both_summ_list2 = [["Week num", "1st year (orange)", "2nd year (red)"]]
    for i in range(18+1):
        dengue_index_list2.append(i+1+18)
    for i in range(len(dengue_index_list2)):
        dengue_both_summ_list2.append([dengue_index_list2[i],y_dengue_2018[i+18], y_dengue_2017[i+18]])
    lst2 = dengue_both_summ_list2

    frame_2 = Frame(window1, bg='pink', width=totalwidth / 3, height=totalheight)
    frame_2.grid(row=0, column=3, sticky="nsew")
    t2 = Table2(frame_2)

    window1.grid_columnconfigure(4, weight=1)

    dengue_index_list3 = []
    dengue_both_summ_list3 = [["Week num", "1st year (orange)", "2nd year (red)"]]
    for i in range(16+1):
        dengue_index_list3.append(i+1+18+18)
    for i in range(len(dengue_index_list3)):
        dengue_both_summ_list3.append([dengue_index_list3[i],y_dengue_2018[i+18+18], y_dengue_2017[i+18+18]])
    lst3 = dengue_both_summ_list3

    frame_3 = Frame(window1, bg='purple', width=totalwidth / 3, height=totalheight)
    frame_3.grid(row=0, column=5, sticky="new")
    t2 = Table3(frame_3)

    window1.grid_columnconfigure(6, weight=1)

# create the widgets for the top frame
model_label = Label(top_frame, text='Rainfall vs Dengue Predictor-Analyser', padx=5)
view_rainfall_datasets = Button(top_frame, text='View Rainfall Datasets', padx=5, command=view_rainfall_in_new_window, bg='lightyellow', cursor="hand2")
view_dengue_datasets = Button(top_frame, text='View Dengue Datasets', padx=5, command=view_dengue_in_new_window, bg='lightyellow', cursor="hand2")
canvas1 = tk.Canvas(top_frame, width=250-6, height=50, bg='brown')

# layout the widgets in the top frame
model_label.grid(row=0, column=0, pady=5, sticky="NSEW")
model_label.config(font=("Arial", 13))  # changes the font and font size of label. NOTE: preserve the cell width!
view_rainfall_datasets.grid(row=0, column=1, pady=5, sticky="NSEW", padx=5)
view_dengue_datasets.grid(row=0, column=2, pady=5, sticky="NSEW")
canvas1.grid(row=0, column=4, pady=5)

# creates as much space between model_label and canvas1(brown)
top_frame.grid_columnconfigure(3, weight=1) # so that canvas3 can be aligned to the extreme right

# create the center widgets
center.grid_rowconfigure(0, weight=1)
center.grid_columnconfigure(1, weight=1)

ctr_left = Frame(center, bg='blue', width=450-5, height=190, padx=5, pady=5)
ctr_right = Frame(center, bg='green', width=450-5, height=190, padx=5, pady=5)

ctr_left.grid(row=0, column=0, sticky="ns")
ctr_right.grid(row=0, column=2, sticky="ns")


title_label = Label(ctr_right, text='Prediction of Peak Dengue Season:', width=30)
title_label.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=NSEW)
title_label.config(font=("Arial", 13))

upcoming_rainfall_month_str = convert_int_to_month(int(user_input_upcoming_monsoon_str))
upcoming_rainfall_month_label = Label(ctr_right, text='Upcoming monsoon month entered:', width=30)
upcoming_rainfall_month_output = Label(ctr_right, text=upcoming_rainfall_month_str, width=22)

upcoming_rainfall_month_label.grid(row=2, column=1, padx=5, pady=5)
upcoming_rainfall_month_output.grid(row=2, column=2, padx=5, pady=5)

predicted_dengue_month_str = convert_int_to_month(applyDelayToUserMonths(userinput).pop())
predicted_dengue_month_label = Label(ctr_right, text='Predicted upcoming dengue month:', width=30)
predicted_dengue_month_output = Label(ctr_right, text=predicted_dengue_month_str, width=22)

predicted_dengue_month_label.grid(row=3, column=1, padx=5, pady=5)
predicted_dengue_month_output.grid(row=3, column=2, padx=5, pady=5)

distance_str = getDelayfromPastData(peakFinder(y17rain),peakFinder(y18rain),\
                                    peakFinder(y17deng),peakFinder(y18deng))
distance_label = Label(ctr_right, text='Average Delay (by algorithm):', width=30)
distance_output = Label(ctr_right, text=str(distance_str) + " month(s) approx", width=22)

distance_label.grid(row=4, column=1, padx=5, pady=5)
distance_output.grid(row=4, column=2, padx=5, pady=5)

ctr_right.grid_rowconfigure(5, minsize=10)

title_label = Label(ctr_right, text='Analysis of Rainfall Data vs Dengue Data:', width=30)
title_label.grid(row=6, column=1, columnspan=2, padx=5, pady=5, sticky=NSEW)
title_label.config(font=("Arial", 13))

peak_rainfall_month_2018_str = ", ".join(list(map(convert_num_to_name,peakFinder(y18rain))))
peak_rainfall_month_2018_label = Label(ctr_right, text='(1st year) Peak Rainfall Months:', width=30)
peak_rainfall_month_2018_output = Label(ctr_right, text=peak_rainfall_month_2018_str, width=22)

peak_rainfall_month_2018_label.grid(row=7, column=1, padx=5, pady=5)
peak_rainfall_month_2018_output.grid(row=7, column=2, padx=5, pady=5)

peak_dengue_month_2018_str = ", ".join(list(map(convert_num_to_name,peakFinder(y18deng))))
peak_dengue_month_2018_label = Label(ctr_right, text='(1st year) Peak Dengue Months:', width=30)
peak_dengue_month_2018_output = Label(ctr_right, text=peak_dengue_month_2018_str, width=22)

peak_dengue_month_2018_label.grid(row=8, column=1, padx=5, pady=5)
peak_dengue_month_2018_output.grid(row=8, column=2, padx=5, pady=5)

peak_rainfall_month_2017_str = ", ".join(list(map(convert_num_to_name, peakFinder(y17rain))))
peak_rainfall_month_2017_label = Label(ctr_right, text='(2nd year) Peak Rainfall Months:', width=30)
peak_rainfall_month_2017_output = Label(ctr_right, text=peak_rainfall_month_2017_str, width=22)

peak_rainfall_month_2017_label.grid(row=9, column=1, padx=5, pady=5)
peak_rainfall_month_2017_output.grid(row=9, column=2, padx=5, pady=5)

peak_dengue_month_2017_str = ", ".join(list(map(convert_num_to_name,peakFinder(y17deng))))
peak_dengue_month_2017_label = Label(ctr_right, text='(2nd year) Peak Dengue Months:', width=30)
peak_dengue_month_2017_output = Label(ctr_right, text=peak_dengue_month_2017_str, width=22)

peak_dengue_month_2017_label.grid(row=10, column=1, padx=5, pady=5)
peak_dengue_month_2017_output.grid(row=10, column=2, padx=5, pady=5)

avg_str = str(int((sum(y_dengue_2018) \
+ sum(y_dengue_2017))/(len(y_dengue_2018) + len(y_dengue_2017))))
print(y_dengue_2018)
print(y_dengue_2017)
print(avg_str)
avg_label = Label(ctr_right, text='Mean Monthly Dengue Cases:', width=30)
avg_output = Label(ctr_right, text=avg_str, width=22)

avg_label.grid(row=11, column=1, padx=5, pady=5)
avg_output.grid(row=11, column=2, padx=5, pady=5)

avg2_str = str(int((sum(rainy_2018) \
+ sum(rainy_2017))/(len(rainy_2018) + len(rainy_2017))))
avg2_label = Label(ctr_right, text='Mean Monthly Rainfall Frequency:', width=30)
avg2_output = Label(ctr_right, text=avg2_str, width=22)

avg2_label.grid(row=12, column=1, padx=5, pady=5)
avg2_output.grid(row=12, column=2, padx=5, pady=5)

ctr_right.grid_rowconfigure(13, minsize=10)

title_label = Label(ctr_right, text='Please enter week no to see info (WW):', width=30)
title_label.grid(row=14, column=1, columnspan=2, padx=5, pady=5, sticky=NSEW)
title_label.config(font=("Arial", 13))

get_dengue_2018_output = None
get_dengue_2017_output = None

get_dengue_2018 = str("None")
get_dengue_2017 = str("None")


def callback():
    global get_dengue_2018, get_dengue_2018_output
    global get_dengue_2017, get_dengue_2017_output
    if entry_W.get().isnumeric():
        if int(entry_W.get()) > 53 or int(entry_W.get()) < 1:
            messagebox.showwarning("ERROR!", "Entry value must be valid week no!")
        else:
            get_dengue_2018 = y_dengue_2018[int(entry_W.get())-1]   # because week 1 stored in index 0
            get_dengue_2017 = y_dengue_2017[int(entry_W.get())-1]
            get_dengue_2018_output.configure(text=str(get_dengue_2018))
            get_dengue_2017_output.configure(text=str(get_dengue_2017))
    else:
        messagebox.showwarning("ERROR!", "Entry value must be numeric!")

entry_W = Entry(ctr_right, background="pink", width=36, justify="center")
MyButton1 = Button(ctr_right, text="Submit", width=20, command=callback, \
                   cursor="hand2", background="lightblue")

# width_label.grid(row=12, column=1, padx=2)
# length_label.grid(row=1, column=2)
entry_W.grid(row=15, column=1, sticky="E", padx=5)
# entry_L.grid(row=1, column=3)
MyButton1.grid(row=15, column=2, sticky="EW", padx=5)

get_dengue_2018_label = Label(ctr_right, text='(1st year) Dengue cases on that week:', width=30)
get_dengue_2018_output = Label(ctr_right, text=get_dengue_2018, width=22)

get_dengue_2018_label.grid(row=16, column=1, padx=5, pady=5)
get_dengue_2018_output.grid(row=16, column=2, padx=5, pady=5)

get_dengue_2017_label = Label(ctr_right, text='(2nd year) Dengue cases on that week:', width=30)
get_dengue_2017_output = Label(ctr_right, text=get_dengue_2017, width=22)

get_dengue_2017_label.grid(row=17, column=1, padx=5, pady=5)
get_dengue_2017_output.grid(row=17, column=2, padx=5, pady=5)

ctr_right.grid_rowconfigure(18, weight=1)

# to plot the graph
fig = plt.figure(figsize=(4, 4))

plt.plot(x_dengue_2018, y_dengue_2018, color='lightsalmon', label='dengue cases (1st year)')
plt.plot(x_dengue_2018, y_filtered_2018, color='aquamarine', label='dengue cases (1st year) filtered')
plt.plot(x_dengue_2017, y_dengue_2017, color='red', label='dengue cases (2nd year)')
plt.plot(x_dengue_2017, y_filtered_2017, color='purple', label='dengue cases (2nd year) filtered')
plt.plot(rainx_2018, rainy_2018, color='blue', label='rainfall (1st year)')
plt.plot(rainx_2017, rainy_2017, color='forestgreen', label='rainfall (2nd year)')

plt.xlabel('weeks')
plt.ylabel('number of dengue cases/rainy days')
plt.title('number of dengue cases vs rainy days')
plt.legend()
export_graph = plt.gcf()

# You can make your x axis labels vertical using the rotation
# plt.xticks(x, rotation=90)

# specify the left grid as master of the graph
canvas = FigureCanvasTkAgg(fig, master=ctr_left)
canvas.draw()
canvas.get_tk_widget().grid(row=1, column=0, ipadx=40, ipady=20)

# navigation toolbar
toolbarFrame = tk.Frame(master=ctr_left)
toolbarFrame.grid(row=2, column=0, sticky="NSEW")
toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)

import pathlib

def export_data():
    export_graph.savefig('graph.png')   #this code added to save to png
    with open('data.txt', 'w') as wr:
        wr.write("Rainfall vs Dengue Analyser\n")
        wr.write("==============================================================\n\n")
        wr.write("Prediction of Peak Dengue Season:\n\n")
        wr.write("Upcoming monsoon month entered:" + upcoming_rainfall_month_str)
        wr.write("\n\n")
        wr.write("Average Delay (by algorithm): " + str(distance_str))
        wr.write("\n\n\n\n")
        wr.write("Analysis of Rainfall Data vs Dengue Data: \n\n")
        wr.write("(1st year) Peak Rainfall Months: " + peak_rainfall_month_2018_str)
        wr.write("\n\n")
        wr.write("(1st year) Peak Dengue Months: " + peak_dengue_month_2018_str)
        wr.write("\n\n")
        wr.write("(2nd year) Peak Rainfall Months: " + peak_rainfall_month_2017_str)
        wr.write("\n\n")
        wr.write("(2nd year) Peak Dengue Months: " + peak_dengue_month_2017_str)
        wr.write("\n\n")
        wr.write("Mean Monthly Dengue Cases: " + avg_str)
        wr.write("\n\n")
        wr.write("Mean Monthly Rainfall Frequency: " + avg2_str)
        wr.write("\n\n")

    path = pathlib.Path(__file__).parent.absolute()
    messagebox.showinfo("Write Successful", "Successfully exported graph.png + data.txt into dir: " + str(path))


browseButton_CSV = tk.Button(text="Export Prediction+Analysis!", command=export_data, bg='green', fg='white', cursor="hand2",
                             font=('helvetica', 12, 'bold'))
canvas1.create_window(125, 27, window=browseButton_CSV)  # x, y positions

root.mainloop()
