#################################################################################
#                                                                               #
#   Scheduling Algorithms for 360º Video Streaming over 5G Networks Simulator   #
#                                                                               #
#   Developed by: Pedro Martin                                                  #
#                                                                               #
#################################################################################

#########################
#                       #
#       Libraries       #
#                       #
#########################

import plotly
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import config

#########################
#                       #
#     PLOT METRICS      #
#                       #
#########################

data = []

excel_file = '../results1/buffer1.xlsx'
df = pd.read_excel(excel_file)

for i in range(int((len(df.columns)-1)/5)):
    data += [go.Scatter(x=df['Time']/1000, y=df['Metric'+str(i+1)], name='User'+str(i+1))]

fig = go.Figure(data)

fig.update_xaxes(title_text='Time [s]')
fig.update_yaxes(title_text='Metric')

plotly.offline.plot(fig, filename="../results1/metric1.html")


#########################
#                       #
#    PLOT THROUGHPUT    #
#                       #
#########################

data = []

excel_file = '../results1/buffer1.xlsx'
df = pd.read_excel(excel_file)

# AVERAGE THROUGHPUT

for i in range(int((len(df.columns)-1)/5)):
    data += [go.Scatter(x=df['Time']/1000, y=df['avg_U'+str(i+1)]/(10**0), connectgaps=True, name='User'+str(i+1))]

fig = go.Figure(data)

fig.update_xaxes(title_text='Time [s]')
fig.update_yaxes(title_text='Average Throughput [Mbps]')

plotly.offline.plot(fig, filename="../results1/avg_throughput1.html")

# ACHIEVED THROUGHPUT
data = []

for i in range(int((len(df.columns)-1)/5)):
    data += [go.Scatter(x=df['Time']/1000, y=df['ach_U'+str(i+1)]/(10**6), connectgaps=True, name='User'+str(i+1))]

fig = go.Figure(data)

fig.update_xaxes(title_text='Time [s]')
fig.update_yaxes(title_text='Achieved Throughput [Mbps]')

plotly.offline.plot(fig, filename="../results1/ach_throughput1.html")


#########################
#                       #
#   PLOT ALLOCATIONS    #
#                       #
#########################

data = []

excel_file = '../results1/allocation1.xlsx'
df = pd.read_excel(excel_file)

for i in range(int((len(df.columns)-1)/2)):
	data += [go.Scatter(x=df['Time']/1000, y=df['CummulativeRB'+str(i+1)]/1000, name='User'+str(i+1))]

fig = go.Figure(data)

fig.update_xaxes(title_text='Time [s]')
fig.update_yaxes(title_text='Total number of allocated RBs x1000')

plotly.offline.plot(fig, filename="../results1/cummulative_allocation1.html")

data = []

for i in range(int((len(df.columns)-1)/2)):
	data += [go.Scatter(x=df['Time']/1000, y=df['InstantRB'+str(i+1)], name='User'+str(i+1))]

fig = go.Figure(data)

fig.update_xaxes(title_text='Time [s]')
fig.update_yaxes(title_text='Number of allocated RBs per TTI')

plotly.offline.plot(fig, filename="../results1/instant_allocation1.html")


#########################
#                       #
#  PLOT BUFFER LENGTH   #
#                       #
#########################

# Enter user number:
for i in range(config.U):
    user_id = i+1

    user = 'User' + str(user_id)
    play = 'Play' + str(user_id)

    excel_file = '../results1/buffer1.xlsx'
    df = pd.read_excel(excel_file)

    data = [go.Scatter( x=df['Time']/1000, y=df[user]/1000, name='Buffer level')]
    data += [go.Scatter( x=df['Time']/1000, y=df[play], name='Playback status')]

    fig = go.Figure(data)

    fig.update_xaxes(title_text='Time [s]')
    fig.update_yaxes(title_text='Buffer length [s]')

    plotly.offline.plot(fig, filename="../results1/buffer/buffer"+str(user_id)+"1.html")


#########################
#                       #
# PLOT REQUEST BITRATES #
#                       #
#########################

# Enter user number:
for i in range(config.U):
    user_id = i+1

    user = 'User' + str(user_id)

    excel_file = '../results1/request1.xlsx'
    df = pd.read_excel(excel_file, sheet_name=user)

    data = [go.Scatter( x=df['request_time']/1000, y=df['estimated_throughput']/(10**6), name='Estimated Throughput')]
    data += [go.Scatter( x=df['request_time']/1000, y=df['bitrate']/(10**6), name='Segment Bitrate')]

    fig = go.Figure(data)

    fig.update_xaxes(title_text='Time [s]')
    fig.update_yaxes(title_text='Mbps')

    plotly.offline.plot(fig, filename="../results1/request/request"+str(user_id)+"1.html")