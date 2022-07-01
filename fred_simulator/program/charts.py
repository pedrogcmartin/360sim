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
import pandas as pd
import config

config = {
  'toImageButtonOptions': {
    'format': 'svg', # one of png, svg, jpeg, webp
    'filename': 'custom_image',
    'height': 495,
    'width': 700,
    'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
  }
}

layout = go.Layout(
plot_bgcolor="#FFF",

legend=dict(
    # Top-right
    #x=0.75,
    #y=0.98,
    #Bottom-right
    x=0.51,
    y=0.04,
    traceorder='normal',
    font=dict(
        family='Times New Roman',
        size=23,
        color='#000'
    ),
    bordercolor='#000000',
    borderwidth=1
))

ID = ''

#########################
#                       #
#     PLOT METRICS      #
#                       #
#########################
"""
print('metrics')

data = []

excel_file = '../results/buffer'+ID+'.xlsx'
df = pd.read_excel(excel_file)

for i in range(int((len(df.columns)-1)/5)):
    data += [go.Scatter(x=df['Time']/1000, y=df['Metric'+str(i+1)], name='User'+str(i+1))]

fig = go.Figure(data=data, layout=layout)

fig.update_xaxes(title_text='Time [s]', title_font = {'size': 22}, title_font_family="Times New Roman", gridcolor="#000000", gridwidth=0.3, showline=True, linewidth=0.5, linecolor='black', mirror=True, rangemode="nonnegative")
fig.update_yaxes(title_text='Metric', title_font = {'size': 22}, title_font_family="Times New Roman", gridcolor="#000000", gridwidth=0.3, showline=True, linewidth=0.5, linecolor='black', mirror=True, rangemode="nonnegative")

plotly.offline.plot(fig, config=config, filename="../results/metric"+ID+".html")
"""

#########################
#                       #
#    PLOT THROUGHPUT    #
#                       #
#########################
"""
print('throughputs')

data = []

excel_file = '../results/buffer'+ID+'.xlsx'
df = pd.read_excel(excel_file)

# AVERAGE THROUGHPUT

for i in range(int((len(df.columns)-1)/5)):
    data += [go.Scatter(x=df['Time']/1000, y=df['avg_U'+str(i+1)]/(10**0), connectgaps=True, name='User'+str(i+1))]

fig = go.Figure(data=data, layout=layout)

fig.update_xaxes(title_text='Time [s]', title_font = {'size': 28}, title_font_family="Times New Roman", gridcolor="#000000", gridwidth=0.3, showline=True, linewidth=0.5, linecolor='black', mirror=True, rangemode="nonnegative")
fig.update_yaxes(title_text='Average Throughput [Mbps]', title_font = {'size': 28}, title_font_family="Times New Roman", gridcolor="#000000", gridwidth=0.3, showline=True, linewidth=0.5, linecolor='black', mirror=True, rangemode="nonnegative")

plotly.offline.plot(fig, config=config, filename="../results/avg_throughput"+ID+".html")


# ACHIEVED THROUGHPUT
data = []

for i in range(int((len(df.columns)-1)/5)):
    data += [go.Scatter(x=df['Time']/1000, y=df['ach_U'+str(i+1)]/(10**6), connectgaps=True, name='User'+str(i+1))]

fig = go.Figure(data)

fig.update_xaxes(title_text='Time [s]')
fig.update_yaxes(title_text='Achieved Throughput [Mbps]')

plotly.offline.plot(fig, filename="../results/ach_throughput"+ID+".html")
"""
"""
#########################
#                       #
#   PLOT ALLOCATIONS    #
#                       #
#########################

print('allocations')

data = []

excel_file = '../results/allocation'+ID+'.xlsx'
df = pd.read_excel(excel_file)

for i in range(int((len(df.columns)-1)/2)):
	data += [go.Scatter(x=df['Time']/1000, y=df['CummulativeRB'+str(i+1)]/1000, name='User'+str(i+1))]

fig = go.Figure(data=data, layout=layout)

fig.update_xaxes(title_text='Time [s]', title_font = {'size': 28}, title_font_family="Times New Roman", gridcolor="#000000", gridwidth=0.3, showline=True, linewidth=0.5, linecolor='black', mirror=True, rangemode="nonnegative")
fig.update_yaxes(title_text='Total number of allocated RBs x1000', title_font = {'size': 28}, title_font_family="Times New Roman", gridcolor="#000000", gridwidth=0.3, showline=True, linewidth=0.5, linecolor='black', mirror=True, rangemode="nonnegative")

plotly.offline.plot(fig, config=config, filename="../results/cummulative_allocation"+ID+".html")


data = []

for i in range(int((len(df.columns)-1)/2)):
	data += [go.Scatter(x=df['Time']/1000, y=df['InstantRB'+str(i+1)], name='User'+str(i+1))]

fig = go.Figure(data)

fig.update_xaxes(title_text='Time [s]')
fig.update_yaxes(title_text='Number of allocated RBs per TTI')

plotly.offline.plot(fig, filename="../results/instant_allocation"+ID+".html")
"""

#########################
#                       #
# PLOT REQUEST BITRATES #
#                       #
#########################

print('bitrates')

data = []

# Enter user number:
#for i in range(config.U):
for i in [0]:
    user_id = i+1

    user = 'User' + str(user_id)

    excel_file = '../results/request'+ID+'.xlsx'
    df = pd.read_excel(excel_file, sheet_name=user)

    data = [go.Scatter( x=df['request_time']/1000, y=df['bitrate']/(10**6), name='Segment Bitrate')]
    data += [go.Scatter( x=df['request_time']/1000, y=df['estimated_throughput']/(10**6), name='Estimated Throughput')]

    fig = go.Figure(data=data, layout=layout)

    fig.update_xaxes(title_text='Time [s]', title_font = {'size': 28}, title_font_family="Times New Roman", gridcolor="#000000", gridwidth=0.3, showline=True, linewidth=0.5, linecolor='black', mirror=True, rangemode="nonnegative")
    fig.update_yaxes(title_text='Mbps', title_font = {'size': 28}, title_font_family="Times New Roman", gridcolor="#000000", gridwidth=0.3, showline=True, linewidth=0.5, linecolor='black', mirror=True, rangemode="nonnegative")#, range=[0, 2.5])

    plotly.offline.plot(fig, config=config, filename="../results/request/request"+ID+'_'+str(user_id)+".html")
    #plotly.offline.plot(fig, filename="../results/request/requestBQA1_"+str(user_id)+".html")
    #plotly.offline.plot(fig, filename="../results/request/requestBQA2_"+str(user_id)+".html")
    #plotly.offline.plot(fig, filename="../results/request/requestBFA_"+str(user_id)+".html")


#########################
#                       #
#  PLOT BUFFER LENGTH   #
#                       #
#########################

print('buffers')

# Enter user number:
#for i in range(config.U):
data = []

#for i in range(config.U):
for i in [0]:
    user_id = i+1

    user = 'User' + str(user_id)
    #play = 'Play' + str(user_id)

    excel_file = '../results/buffer'+ID+'.xlsx'
    df = pd.read_excel(excel_file)

    data = [go.Scatter( x=df['Time']/1000, y=df[user]/1000, name='Buffer level')]
    #data += [go.Scatter( x=df['Time']/1000, y=df[play], name='Playback status')]

    fig = go.Figure(data=data, layout=layout)

    fig.update_xaxes(title_text='Time [s]', title_font = {'size': 28}, title_font_family="Times New Roman", gridcolor="#000000", gridwidth=0.3, showline=True, linewidth=0.5, linecolor='black', mirror=True, rangemode="nonnegative")
    fig.update_yaxes(title_text='Buffer length [s]', title_font = {'size': 28}, title_font_family="Times New Roman", gridcolor="#000000", gridwidth=0.3, showline=True, linewidth=0.5, linecolor='black', mirror=True, rangemode="nonnegative")

    plotly.offline.plot(fig, config=config, filename="../results/buffer/buffer"+ID+'_'+str(user_id)+".html")
    #plotly.offline.plot(fig, filename="../results/buffer/bufferBQA1_"+str(user_id)+".html")
    #plotly.offline.plot(fig, filename="../results/buffer/bufferBQA2_"+str(user_id)+".html")
    #plotly.offline.plot(fig, filename="../results/buffer/bufferBFA_"+str(user_id)+".html")