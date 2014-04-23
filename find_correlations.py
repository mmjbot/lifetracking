# find correlations between independent variable (productivity) and dependent

import json
import json_parsing
from json_parsing import *
import matplotlib.pyplot as plt
import math
import numpy as np

directory = "Reporter-App"
dates = ['2014-02-08', '2014-02-09', "2014-02-10", "2014-02-11", "2014-02-12", "2014-02-13", "2014-02-14", "2014-02-17", "2014-02-19", "2014-02-20", "2014-02-27", "2014-03-03", "2014-03-09", "2014-03-13", "2014-03-14", "2014-03-15", "2014-03-16", "2014-03-17", "2014-03-18"]


def first_order(var_name, sub_field_name):
	""" return a list of (x,y) pairs that correspond to (independent, dependent) variables where independent is var_name and dependent is replies to 'are you working'"""
	vals = list() # list of (x,y) pairs
	for date in dates:		
		curr_file = open(directory + "/" + date + "-reporter-export.json")
		curr_str = curr_file.read()
		curr_data = json.loads(curr_str)
		curr = Data.deserialize(curr_data)
		for snap in curr.snapshots:
			if not filter(lambda x : x.questionPrompt == "Are you working?", snap.responses):
				continue 	# only care about the ones where we reported productivity
			x_val = snap.__getattr__(var_name)
			print(x_val)
			if(sub_field_name != ""):
				x_val = x_val.__getattr__(sub_field_name)
			y_val = filter(lambda x : x.questionPrompt == "Are you working?", snap.responses)[0].answeredOptions[0]
			vals.append((x_val,y_val))
	return vals

def standardize(correlation, bucket_size):
	""" Takes a list of (x,y) values and returns a histogram of (x,y) pairs where y is the fraction of times x created a yes reponse"""
	new_correlation = list()
	for tup in correlation: # should be able to convert to a map statement
		x_val = tup[0]
		y_val = 1 if tup[1] == 'Yes' else 0
		new_correlation.append((x_val, y_val))
	x_vals = set(map(lambda tup: tup[0], new_correlation))
	buckets = np.arange(min(x_vals), max(x_vals)+bucket_size, bucket_size)
	standardized = list()
	for x in buckets: # create a histogram of how many times each x value created a "yes" response
		num_success = len(filter(lambda tup: (tup[0] >= x) and (tup[0] < (x+bucket_size)) and (tup[1] == 1), new_correlation))
		total_num = len(filter(lambda tup: (tup[0] >= x) and (tup[0] < (x+bucket_size)), new_correlation))
		fraction_success = num_success*1.0/total_num if total_num > 0 else 0.0
		standardized.append((x+bucket_size/2.0,fraction_success))
	return standardized

def separate_vals(correlation):
	correlation = sorted(correlation, key=lambda tup: tup[0])
	x_vals = map(lambda tup: tup[0], correlation)
	y_vals = map(lambda tup: tup[1], correlation)
	return (x_vals, y_vals)

def plot(correlation):
	(x_vals, y_vals) = separate_vals(correlation)
	plt.plot(x_vals, y_vals)
	plt.show()

def analyze_firstOrder(field, subfield="", bucket_size=1):
	correlation = first_order(field, subfield)
	correlation = standardize(correlation, bucket_size)
	plot(correlation)
	return correlation

# will substitute for ML optimum for now
# this is the ML step
def guess_optimums(x_vars, y_vars):
	"""Determines the "optimum y" for the query x, given a simple best-fit line for the data"""
	reorder = sorted(range(len(x_vars)), key = lambda ii: x_vars[ii])
	x_vars = [x_vars[ii] for ii in reorder]
	y_vars = [y_vars[ii] for ii in reorder]
	plt.scatter(x_vars, y_vars, s=30, alpha=0.15)
	# determine best fit line
	par = np.polyfit(x_vars, y_vars, 1, full=True)

	slope=par[0][0]
	intercept=par[0][1]
	(x0, x1) = [min(x_vars), max(x_vars)]
	y_vals = [slope*x0 + intercept, slope*x1 + intercept]
	estimated_y = [y_vals[0] + slope*i for i in range(int(x0),int(math.ceil(x1)))]

	plt.plot([x0,x1], y_vals, '-r')
	plt.show()
	return(range(int(x0),int(math.ceil(x1))), estimated_y)

	
(x_vals,y_vals) = separate_vals(analyze_firstOrder("weather", subfield="tempF", bucket_size=5))
(x, test_y) = guess_optimums(x_vals, y_vals)
print(test_y[2])
# analyze_firstOrder("weather", subfield="tempF", bucket_size=5)
# analyze_firstOrder("battery", bucket_size=0.1)
# correlation = [(1, "Yes"), (2,"No"), (3,"Yes"), (4,"Yes")]
# print(standardize(correlation,4))