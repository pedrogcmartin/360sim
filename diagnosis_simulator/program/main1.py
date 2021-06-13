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

import config
import numpy as np
import client
import server
import qoe_model
import xlsxwriter
import datetime

#########################
#                       #
# Progamming Variables  #
#   (Initialization)    #
#                       #
#########################

t = 0
buffer = np.zeros(config.U, dtype=float)
delta_buffer = np.zeros(config.U, dtype=float)
rx_bits = np.zeros(config.U, dtype=float)
play = np.zeros(config.U, dtype=int)
reported_CQI = np.zeros(config.U, dtype=int)
RB_allocations = np.zeros(config.U, dtype=int)
total_RB_allocations = np.zeros(config.U, dtype=int)
metric = np.zeros(config.U, dtype=float)
last_reply = np.zeros(config.U, dtype=int)
requests = [[]] * config.U

# QoE variables
cnt_stalls = np.zeros(config.U, dtype=int)
perceived_stall = np.negative(np.ones(config.U, dtype=int))
dur_stalls = np.zeros(config.U, dtype=int)
t_dur_stalls = np.zeros(config.U, dtype=int)
flg_qoe_init = [False for i in range(config.U)]
flg_qoe = [False for i in range(config.U)]
avg_stall = np.zeros(config.U, dtype=float)
avg_quality = np.zeros(config.U, dtype=float)
sum_ql = np.zeros(config.U, dtype=float)
sum_ql_sq = np.zeros(config.U, dtype=float)
sig_quality = np.zeros(config.U, dtype=float)
qoe = np.zeros(config.U, dtype=float)
qoe_workbook = xlsxwriter.Workbook('../results1/qoe1.xlsx')
qoe_worksheet = qoe_workbook.add_worksheet()
for i in range(config.U):
    qoe_worksheet.write(i, 0, 'User'+str(i+1))

REPORT = False

if REPORT:
    buffer_workbook = xlsxwriter.Workbook('../results1/buffer1.xlsx')
    buffer_worksheet = buffer_workbook.add_worksheet()

    allocation_workbook = xlsxwriter.Workbook('../results1/allocation1.xlsx')
    allocation_worksheet = allocation_workbook.add_worksheet()

    request_workbook = xlsxwriter.Workbook('../results1/request1.xlsx')

    buffer_worksheet.write(0, 0, 'Time')
    allocation_worksheet.write(0, 0, 'Time')

    for i in range(config.T+1):
        buffer_worksheet.write(i+1, 0, i)
        allocation_worksheet.write(i+1, 0, i)

    for i in range(config.U):
        buffer_worksheet.write(0, 5*i+1, 'User'+str(i+1))
        buffer_worksheet.write(0, 5*i+2, 'Play'+str(i+1))
        buffer_worksheet.write(0, 5*i+3, 'avg_U'+str(i+1))
        buffer_worksheet.write(0, 5*i+4, 'Metric'+str(i+1))
        buffer_worksheet.write(0, 5*i+5, 'ach_U'+str(i+1))
        allocation_worksheet.write(0, 2*i+1, 'CummulativeRB'+str(i+1))
        allocation_worksheet.write(0, 2*i+2, 'InstantRB'+str(i+1))


#########################
#                       #
#      Main Program     #
#                       #
#########################
print("Progress: 0.00 %")

t_init = datetime.datetime.now()
print(t_init)

# Open salient 360 dataset
salient360_dataset = client.open_file()

while t <= config.T:
    # CLIENT SIDE
    for i in range (config.U):
        # Update buffer
        if RB_allocations[i] != 0:
            delta_buffer[i], rx_bits[i], requests[i] = client.buffer_update(i, requests[i], RB_allocations[i], rx_bits[i], t)
            buffer[i] += delta_buffer[i]
            # Buffer max. capacity; Check if there is enough content for playback after buffering
            if buffer[i] >= config.B - 0.1:
                buffer[i] = config.B
                play[i] = 1

        # Store buffer parameters
        if REPORT:
            client.store_buffer(t, i, buffer_worksheet, allocation_worksheet, buffer[i], play[i], rx_bits[i], reported_CQI[i], metric[i], total_RB_allocations[i], RB_allocations[i])

        # Buffering event
        if play[i] == 0:
            if not requests[i] or (requests[i][-1]['reply_bits'] == 0 and play[i] == 0):
                # Initial buffering - Request every tile with the lowest quality or if there is space - Request every tile with the lowest quality
                requests[i] = client.request_LQ(requests[i], t)

        # Normal video playback
        elif play[i] == 1:
            # There is space for a new segment and every request has been completly replied
            if config.B - buffer[i] >= 1000 and requests[i][-1]['reply_bits'] == 0 and len(requests[i]) < config.Ns: 
                # Request segment with rate adaptation (RA)
                requests[i] = client.request_RA(requests[i], t, client.throughput_estimation(requests[i]), salient360_dataset, i)

            # Client watches TTI seconds of video
            buffer[i] -= config.TTI

            # Client suffers a stall event
            if buffer[i] <= 0:
                buffer[i] = 0
                play[i] = 0

        # Update QoE inputs
        cnt_stalls[i], perceived_stall[i], dur_stalls[i], t_dur_stalls[i], sum_ql[i], sum_ql_sq[i], flg_qoe[i], flg_qoe_init[i]  = qoe_model.update_QoE(cnt_stalls[i], perceived_stall[i], dur_stalls[i], t_dur_stalls[i], sum_ql[i], sum_ql_sq[i], play[i], flg_qoe[i], flg_qoe_init[i], requests[i], salient360_dataset, i, t)

        # Report CQI
        if t % 5 == 0:
            reported_CQI[i] = client.get_CQI(i, t)

    # SERVER SIDE
    RB_allocations = np.zeros(config.U, dtype=int)

    # Allocate each Kth RB
    for k in range(config.K):
        # Initialize metrics/RB_allocations arrays
        metric = np.negative(np.ones(config.U, dtype=int))
        
        # Compute each user metric
        for i in range(config.U):
            metric[i] = server.compute_metric_RR(requests[i], last_reply[i], t)
        #    #metric[i] = server.compute_metric_BET(requests[i], rx_bits[i], t, reported_CQI[i], RB_allocations[i])
        #    #metric[i] = server.compute_metric_PF(requests[i], rx_bits[i], t, reported_CQI[i], RB_allocations[i], 1, 0)
        #    #metric[i] = server.compute_metric_PF(requests[i], rx_bits[i], t, reported_CQI[i], RB_allocations[i], 1, 1)
    
        # Allocate 1 RB to 1 user
        last_reply, RB_allocations, total_RB_allocations = server.allocation(metric, RB_allocations, total_RB_allocations, last_reply, t + float(k/1000), k)

    t += config.TTI

    # Update running status
    if not t % 1000:
        print("Progress (", str(config.U), "):", int(t/1000))

# Compute and store QoE values
for i in range(config.U):
    qoe[i] = qoe_model.compute_QoE(cnt_stalls[i], sum_ql[i], sum_ql_sq[i], t_dur_stalls[i], config.T, i)
    qoe_worksheet.write(i, 1, qoe[i])
    qoe_worksheet.write(i, 2, sum_ql[i])
    qoe_worksheet.write(i, 3, sum_ql_sq[i])
    qoe_worksheet.write(i, 4, len(requests[i]))
    qoe_worksheet.write(i, 5, cnt_stalls[i])
    qoe_worksheet.write(i, 6, t_dur_stalls[i])
    qoe_worksheet.write(i, 7, t_dur_stalls[i]-dur_stalls[i])

qoe_workbook.close()

t_final = datetime.datetime.now()
print(t_final)
print(t_final-t_init)

if REPORT:
    # Store requests parameters
    header = ['request_time', 'bitrate', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 't10', 't11', 't12', 't13', 't14', 't15', 't16', 't17', 't18', 't19', 't20', 't21', 't22', 't23', 'reply_time', 'estimated_throughput']
    for idx1, i in enumerate(requests):
        request_worksheet = request_workbook.add_worksheet('User'+str(idx1+1))
        for header_col in range (28):
            request_worksheet.write(0, header_col, header[header_col])
        for idx2, j in enumerate(i):
            for idx3, k in enumerate(j.values()):
                if idx3 < 2:
                    request_worksheet.write(idx2+1, idx3, k)
                elif idx3 == 2:
                    for idx4, l in enumerate(k):
                        request_worksheet.write(idx2+1, idx3+idx4, l)
                elif idx3 >= 4:
                    request_worksheet.write(idx2+1, idx3+(config.Nx*config.Ny)-2, k)

    buffer_workbook.close()
    allocation_workbook.close()
    request_workbook.close()