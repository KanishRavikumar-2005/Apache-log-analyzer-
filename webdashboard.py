from flask import Flask, request, render_template, jsonify, url_for, redirect
import os
import re
import csv
import hashlib
import sys
import pandas as pd
import matplotlib.pyplot as plt
import base64
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn import datasets
from difflib import SequenceMatcher
import difflib
import seaborn as sns
import io
from collections import Counter


app = Flask(__name__)


def find_recurrence(arr):
        # Initialize an empty dictionary to store frequency of values
        frequency_dict = {}
        
        # Iterate over the array
        for value in arr:
            # If the value is already in the dictionary, increment its frequency
            if value in frequency_dict:
                frequency_dict[value] += 1
            # If the value is not in the dictionary, add it with a frequency of 1
            else:
                frequency_dict[value] = 1
        
        # Return the dictionary containing frequencies
        return frequency_dict

def plot_top_5_frequency_rank_scatter(frequency_dict):
    # Sort the dictionary by values in descending order
    sorted_frequency = sorted(frequency_dict.items(), key=lambda x: x[1], reverse=True)
    
    # Take the top 5 frequent values
    top_5_frequency = dict(sorted_frequency[:5])
    
    # Convert the dictionary to a DataFrame for easier plotting
    data = {'Values': list(top_5_frequency.keys()), 'Frequency': list(top_5_frequency.values())}
    df = pd.DataFrame(data)
    
    # Plot the rank scatter plot
    plt.figure(figsize=(8, 6))
    sns.stripplot(data=df, x='Values', y='Frequency', jitter=True, color='skyblue', size=10)
    
    # Add labels and title
    plt.xlabel('IP Addresses')
    plt.ylabel('Frequency')
    plt.title('Rank Scatter Plot of Top 5 IP Addresses Causing Errors')
    
    # Rotate x-axis labels for better readability if needed
    plt.xticks(rotation=45)
    
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes,  format='png', bbox_inches='tight')
    pic_IObytes.seek(0)
    pic_hash = base64.b64encode(pic_IObytes.read())
    return pic_hash

def plot_bottom_5_frequency_rank_scatter(frequency_dict):
    # Sort the dictionary by values in ascending order
    sorted_frequency = sorted(frequency_dict.items(), key=lambda x: x[1])
    
    # Take the bottom 5 least frequent values
    bottom_5_frequency = dict(sorted_frequency[:5])
    
    # Convert the dictionary to a DataFrame for easier plotting
    data = {'Values': list(bottom_5_frequency.keys()), 'Frequency': list(bottom_5_frequency.values())}
    df = pd.DataFrame(data)
    
    # Plot the rank scatter plot
    plt.figure(figsize=(8, 6))
    sns.stripplot(data=df, x='Values', y='Frequency', jitter=True, color='skyblue', size=10)
    
    # Add labels and title
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.title('Rank Scatter Plot of Least 5 IP Addresses Causing Errors')
    
    # Rotate x-axis labels for better readability if needed
    plt.xticks(rotation=45)
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes,  format='png', bbox_inches='tight')
    pic_IObytes.seek(0)
    pic_hash = base64.b64encode(pic_IObytes.read())
    return pic_hash
    
def plot_average_5_frequency_rank_scatter(frequency_dict):
    # Sort the dictionary by values in ascending order
    sorted_frequency = sorted(frequency_dict.items(), key=lambda x: x[1])
    
    # Calculate the median frequency
    median_index = len(sorted_frequency) // 2
    median_frequency = sorted_frequency[median_index][1]
    
    # Find the indices of values around the median
    start_index = max(0, median_index - 2)
    end_index = min(len(sorted_frequency), median_index + 3)
    
    # Take the values around the median
    average_5_frequency = dict(sorted_frequency[start_index:end_index])
    
    # Convert the dictionary to a DataFrame for easier plotting
    data = {'Values': list(average_5_frequency.keys()), 'Frequency': list(average_5_frequency.values())}
    df = pd.DataFrame(data)
    
    # Plot the rank scatter plot
    plt.figure(figsize=(8, 6))
    sns.stripplot(data=df, x='Values', y='Frequency', jitter=True, color='skyblue', size=10)
    
    # Add labels and title
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.title('Rank Scatter Plot of Median 5 IP addresses involved in errors')
    
    # Rotate x-axis labels for better readability if needed
    plt.xticks(rotation=45)
    plt.xticks(rotation=45)
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes,  format='png', bbox_inches='tight')
    pic_IObytes.seek(0)
    pic_hash = base64.b64encode(pic_IObytes.read())
    return pic_hash

def create_pie_chart(data):
    # Count the occurrences of each unique string
    counts = Counter(data)
    
    # Sort the counts dictionary by values in descending order
    sorted_counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
    
    # Take the top 5 elements and combine the rest
    top_5 = dict(list(sorted_counts.items())[:5])
    rest_count = sum(list(sorted_counts.values())[5:])
    
    # Add 'Others' category to the top 5 dictionary
    top_5['Others'] = rest_count
    
    # Get the unique strings and their corresponding counts
    labels = list(top_5.keys())
    counts = list(top_5.values())
    
    # Create a pie chart with a larger figure size and higher DPI
    plt.figure(figsize=(16, 16), dpi=100)
    plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 27})  # Set fontsize here
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    # Add title
    plt.title('Top 5 actions leading to Errors', fontsize=30)  # Increase title fontsize
    
    # Convert the plot to bytes and then to base64
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes, format='png', bbox_inches='tight')
    pic_IObytes.seek(0)
    pic_hash = base64.b64encode(pic_IObytes.read())# Decode as UTF-8
    
    # Clear the plot to release memory
    plt.clf()
    
    return pic_hash

def find_highest_frequency(lst):
    # Count the frequency of each element in the list
    frequency_counter = Counter(lst)
    
    # Find the element with the highest frequency
    highest_frequency_value = max(frequency_counter, key=frequency_counter.get)
    highest_frequency = frequency_counter[highest_frequency_value]
    
    return highest_frequency_value, highest_frequency
    


def splitFile(filename):
    log_pattern = r"\[(.*?)\] \[(.*?)\] (.*)"  # Matches timestamp, log level, and message

    name = filename

    with open(os.path.join("uploads", name), "r") as apl:
        log_lines = apl.readlines()

    def create_idMD5(data):
        if isinstance(data, str):
            data = data.encode()
        # Create MD5 hash object
        hasher = hashlib.md5()
        # Update the hasher with the data
        hasher.update(data)
        # Get the digest as a hexadecimal string
        return hasher.hexdigest()

    def analyze_log_line(log_line):
        match = re.match(log_pattern, log_line)
        if match:
            times = match.group(1)
            tssp = times.split(' ')
            timestamp = {
                "date": tssp[2], "month": tssp[1], "year": tssp[4], "day": tssp[0], "time": tssp[3]
            }
            log_level = match.group(2)
            message = match.group(3)
            mgs = r"\[(.*?)\]\s*(.+)"
            mych = re.match(mgs, message)
            is_client_side = False
            ip = "server::default"
            if mych:
                is_client_side = True
                myc = mych.group(1)
                mym = mych.group(2)
                mycips = myc.split(" ")
                ip = mycips[1]
            return timestamp, log_level, is_client_side, message, create_idMD5(log_line), ip
        else:
            return None
    fnx = os.path.join("splitted", f"log_analysis-{name}.csv")
    with open(fnx, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Date", "Month", "Year", "Day", "Time", "Log Level", "Message", "Side", "IP Address"])
        count = 0
        for log_line in log_lines:
            result = analyze_log_line(log_line)
            if result:
                timestamp, log_level, ic,  message, lineId, ipadd = result
                im = "Server"
                if ic:
                    im = "Client"
                writer.writerow([lineId, timestamp['date'], timestamp['month'], timestamp['year'], timestamp['day'], timestamp['time'], log_level, message, im, ipadd])
                count = count + 1
            else:
                with open(f"IssueLogText-{name}.log", "a") as ilt:
                    ilt.write(log_line)
        print(f"Wrote {count}/{len(log_lines)} Data")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the request contains a file
        if 'file_upload' in request.files:
            file = request.files['file_upload']
            # Do something with the file, like save it or process it
            try:
                file.save(os.path.join("uploads", file.filename))
            
                splitFile( file.filename)


            except Exception as e:
                print("Nope: " + e)

            return redirect(url_for('index'))
            

    
    # If it's a GET request or the form wasn't submitted, render the form
    elif request.method == 'GET':
        dir_list = os.listdir("splitted")
        return render_template('index.html', jlist=jsonify({"list": dir_list}).json)


@app.route("/dash/<name>", methods=["GET", "POST"])
def dashboard(name):
    df = pd.read_csv(f"splitted/{name}")
    datatr = {}
    datatr["head"] = base64.b64encode(df.head().to_html().encode('ascii')).decode("ascii")
    months = []
    for i in df["Month"]:
        if (i in months) == False:
            months.append(i)
    datatr["months"] = base64.b64encode(str(months).encode('ascii')).decode("ascii")
    data_based = {}
    for month in months:
        data_based[month] = df[(df["Month"] == month)]

    aer = ""

    targets = []
    for mth in months:
        dax = data_based[mth][(data_based[mth]["Log Level"] == "error")].Message
        dem = dax.values
        for ls in dem:
            if type(ls) == str:
                aer += ls +"\n"
                targets.append(ls)

    datatr["errors"] = base64.b64encode(aer.encode("ascii")).decode("ascii")
    client_targets = []
    server_targets = []
    for side in targets:
        if "client" in side:
            client_targets.append(side)
        else:
            server_targets.append(side)

    client_pattern = r"\[client (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\] (.*)"
    client_targets_unset = []
    client_problem_ip = []
    client_problem_link = {}
    for m in client_targets:
        words = re.match(client_pattern, m)
        client_targets_unset.append(words.group(2))
        client_problem_ip.append(words.group(1))
        client_problem_link.setdefault(words.group(1), []).append(words.group(2))

    ctus = list(set(client_targets_unset))
    recurrence_dict = find_recurrence(client_problem_ip)
    
    scatter_high = plot_top_5_frequency_rank_scatter(recurrence_dict)
    scatter_low = plot_bottom_5_frequency_rank_scatter(recurrence_dict)
    scatter_medium = plot_average_5_frequency_rank_scatter(recurrence_dict)
    datatr["highip"] = scatter_high.decode("ascii")
    datatr["lowip"] = scatter_low.decode("ascii")
    datatr["median"] = scatter_medium.decode("ascii")
    issue_ip, issue_times =  find_highest_frequency(client_problem_ip)
    highest_ip_tired = client_problem_link[issue_ip]
    high_err = create_pie_chart(highest_ip_tired)
    datatr["higheh"] = high_err.decode("ascii")


    return render_template("dash.html", datalst = jsonify(datatr).json, dname = name, hec =issue_ip, hect = issue_times )

if __name__ == '__main__':
    app.run(debug=True, port=8080)
