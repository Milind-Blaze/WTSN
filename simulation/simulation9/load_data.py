import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# request_filepath = "./fast1_request_response/request_time.csv"
request_filepath = "./fast1_request_response/response_time.csv"

# load the csv file at request_filepath
request_df = pd.read_csv(request_filepath)
# find the inter-arrival time between requests
# request_df['inter_arrival_time'] = request_df['Request Timestamp (ns)'].diff()
# request_df['inter_arrival_time'] = request_df['Response Timestamp (ns)'].diff()
# print(request_df.head())
# # plot the histogram of the inter-arrival time after dividing by 10^6 to convert to ms
# plt.hist(request_df['inter_arrival_time']/10**6, bins=100)
# plt.xlabel("Inter-arrival time (ms)")
# plt.ylabel("Frequency")
# plt.title("Histogram of Inter-arrival time")
# plt.show()
# # print the mean and standard deviation of the inter-arrival time
# print("Mean of inter-arrival time: ", np.mean(request_df['inter_arrival_time'])/10**6)
# print("Standard deviation of inter-arrival time: ", np.std(request_df['inter_arrival_time'])/10**6)

# arrival_time = np.array(request_df['Request Timestamp (ns)'])
arrival_time = np.array(request_df['Response Timestamp (ns)'])
inter_arrival_time = np.diff(arrival_time)
print(list(inter_arrival_time))
print(np.mean(inter_arrival_time/10**6))
print(np.std(inter_arrival_time/10**6))

print(np.std(np.array([2]*10)))