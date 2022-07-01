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
import random

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
K_bits = np.zeros(config.U, dtype=float)
t_rx_bits = np.zeros(config.U, dtype=int)
throughput = np.zeros(config.U, dtype=float)
play = np.zeros(config.U, dtype=int)
reported_CQI = np.zeros(config.U, dtype=int)
user_CQI = np.zeros(config.U, dtype=int)
RB_allocations = np.zeros(config.U, dtype=int)
total_RB_allocations = np.zeros(config.U, dtype=int)
metric = np.zeros(config.U, dtype=float)
last_reply = np.zeros(config.U, dtype=float)
requests = [[] for i in range(config.U)]
flg_firstU = [True for i in range(config.U)]
Nactive_users = 0
exclusion_cnt = 0
#idx_exc = 0
mins_list = []
exc_list = []

# QoE variables
qoe3 = 0.0
qoe4 = 0.0
qoe2 = 0.0
cnt_stalls = np.zeros(config.U, dtype=int)
cnt_milisegments = np.zeros(config.U, dtype=int)
perceived_stall = np.negative(np.ones(config.U, dtype=int))
dur_stalls = np.zeros(config.U, dtype=int)
t_dur_stalls = np.zeros(config.U, dtype=int)
flg_qoe_init = [False for i in range(config.U)]
flg_qoe = [False for i in range(config.U)]
flg_start_QoE = [False for i in range(config.U)]
avg_stall = np.zeros(config.U, dtype=float)
avg_quality = np.zeros(config.U, dtype=float)
sum_ql = np.zeros(config.U, dtype=float)
sum_ql_sq = np.zeros(config.U, dtype=float)
sig_quality = np.zeros(config.U, dtype=float)
qoe = np.zeros(config.U, dtype=float)
ID = 'QAAD'+'_'+str(config.U)
qoe_workbook = xlsxwriter.Workbook('../results/qoe'+ID+'.xlsx')
qoe_worksheet = qoe_workbook.add_worksheet()
for i in range(config.U):
    qoe_worksheet.write(i, 0, 'User'+str(i+1))

REPORT = True

if REPORT:
    buffer_workbook = xlsxwriter.Workbook('../results/buffer'+ID+'.xlsx')
    buffer_worksheet = buffer_workbook.add_worksheet()

    allocation_workbook = xlsxwriter.Workbook('../results/allocation'+ID+'.xlsx')
    allocation_worksheet = allocation_workbook.add_worksheet()

    request_workbook = xlsxwriter.Workbook('../results/request'+ID+'.xlsx')

    buffer_worksheet.write(0, 0, 'Time')
    allocation_worksheet.write(0, 0, 'Time')

    for i in range(config.T+1):
        buffer_worksheet.write(i+1, 0, i)
        allocation_worksheet.write(i+1, 0, i)

    for idx, i in enumerate(range(config.U)):
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
print "Progress: 0.00 %"

t_init = datetime.datetime.now()
print(t_init)

# Open salient 360 dataset
salient360_dataset = client.open_file()

# Generate random initialization times list
init_list = random.sample(range(1, 1000), config.U)
init_list = sorted(init_list)

init_list = [0 for i in range(config.U)]

print init_list

#while t <= config.T:
for t in range(0, config.T+1, config.TTI):
    #Number of initialized users
    """if Ninit_users < config.U and t == init_list[Ninit_users]:
        Ninit_users += 1"""

    # CLIENT SIDE
    for i in range (config.U):
        # Get user's current CQI
        user_CQI[i] = client.get_CQI(i, t)

        """if not t_rx_bits[i] % config.theta and t > 1 and requests[i][-1]['reply_bits']:
            throughput[i], flg_firstU[i] = client.estimate_throughput(throughput[i], K_bits[i], t, buffer[i], flg_firstU[i])
            K_bits[i] = 0"""

        # Update buffer
        if RB_allocations[i] != 0:
            delta_buffer[i], rx_bits[i], requests[i], Nactive_users = client.buffer_update(user_CQI[i], requests[i], Nactive_users, RB_allocations[i], rx_bits[i], t)
            buffer[i] += delta_buffer[i]
            # Buffer max. capacity; Check if there is enough content for playback after buffering
            if buffer[i] >= config.Binit - config.epsilon:
                play[i] = 1
    
        # Store buffer parameters
        if REPORT:
            client.store_buffer(t, t_rx_bits[i], i, buffer_worksheet, allocation_worksheet, buffer[i], play[i], rx_bits[i], user_CQI[i], metric[i], total_RB_allocations[i], RB_allocations[i])

        # Buffering event
        if play[i] == 0:
            if t >= init_list[i]:
                if not requests[i] or (requests[i] and requests[i][-1]['reply_bits'] == 0):
                    # Initial buffering - Request every tile with the lowest quality or if there is space - Request every tile with the lowest quality
                    #requests[i] = client.request_LQ(requests[i], t)
                    requests[i] = client.request_LQ_QAAD(requests[i], t)
                    Nactive_users += 1

                else:
                    t_rx_bits[i] += 1

        # Normal video playback
        else:
            # There is space for a new segment and every request has been completly replied
            if requests[i][-1]['reply_bits'] == 0:
                if config.Binit- buffer[i] >= config.S:
                    # Request segment with rate adaptation (RA)
                    #requests[i] = client.request_RA(requests[i], t, t_dur_stalls[i]+init_list[i], client.throughput_estimation(requests[i], init_list[i], i), salient360_dataset, i, buffer[i])
                    #requests[i] = client.request_RA(requests[i], t, t_dur_stalls[i]+init_list[i], throughput[i], salient360_dataset, i, buffer[i])

                    requests[i] = client.request_RA_QAAD(requests[i], t, t_dur_stalls[i]+init_list[i], client.throughput_estimation(requests[i], init_list[i], i), salient360_dataset, i, buffer[i])
                    #requests[i] = client.request_RA_QAAD(requests[i], t, t_dur_stalls[i]+init_list[i], throughput[i], salient360_dataset, i, buffer[i])
                    Nactive_users += 1

            
            else:
                t_rx_bits[i] += 1

            # Client watches TTI seconds of video
            buffer[i] -= config.TTI

            # Client suffers a stall event
            if buffer[i] <= 0:
                buffer[i] = 0
                play[i] = 0

        # Update QoE inputs
        if t >= init_list[i]:
            cnt_milisegments[i], cnt_stalls[i], perceived_stall[i], dur_stalls[i], t_dur_stalls[i], sum_ql[i], sum_ql_sq[i], flg_qoe[i], flg_qoe_init[i], flg_start_QoE[i]  = qoe_model.update_QoE(cnt_milisegments[i], cnt_stalls[i], perceived_stall[i], dur_stalls[i], t_dur_stalls[i], sum_ql[i], sum_ql_sq[i], play[i], flg_qoe[i], flg_qoe_init[i], flg_start_QoE[i], init_list[i], requests[i], salient360_dataset, i, t)
        
        #if i == 0:
        #    print t, init_list[i], play[i], flg_start_QoE[i], t_dur_stalls[i]

        # Report CQI
        if not t % 5:
            reported_CQI[i] = user_CQI[i]

    # SERVER SIDE
    RB_allocations = np.zeros(config.U, dtype=int)

    metric = np.negative(np.ones(config.U, dtype=float))

    """if not exclusion_cnt:
        if t > config.t_exc:
            mins_list = sorted([(x, i) for (i, x) in enumerate(reported_CQI)], reverse=False)[:7]
            for idx_exc in mins_list:
                exc_list.append(idx_exc[1])

            exclusion_cnt = config.T-config.t_exc+1
    
    else:
        exclusion_cnt -= 1"""


    for i in range(config.U):
        if t >= init_list[i] and i not in exc_list:
            #metric[i] = server.compute_metric_newRR(requests[i], last_reply[i], t)
            #metric[i] = server.compute_metric_newBET(requests[i], rx_bits[i], t_rx_bits[i], buffer[i])
            metric[i] = server.compute_metric_newMT(requests[i], reported_CQI[i])
            #metric[i] = server.compute_metric_newPF(requests[i], rx_bits[i], t_rx_bits[i], reported_CQI[i], 0.5) #0.001
            #metric[i] = server.compute_metric_newAlgorithm(requests[i], rx_bits[i], t_rx_bits[i], reported_CQI[i], config.U, 10)
            #metric[i] = server.compute_metric_FRED(requests[i], reported_CQI[i], buffer[i], 0.0*10**3, t)

    last_reply, RB_allocations, total_RB_allocations = server.newAllocation(requests, reported_CQI, metric, RB_allocations, total_RB_allocations, last_reply, Nactive_users, t)
    #last_reply, RB_allocations, total_RB_allocations = server.allocation(metric, RB_allocations, total_RB_allocations, last_reply, t)

    # Allocate each Kth RB
    #for k in range(config.K):
        # Initialize metrics/RB_allocations arrays
        #metric = np.negative(np.ones(config.U, dtype=float))
        
        # Compute each user metric
        #for i in range(config.U):
        #    metric[i] = server.compute_metric_RR(requests[i], last_reply[i], t)
        #    metric[i] = server.compute_metric_BET(requests[i], rx_bits[i], t, reported_CQI[i], RB_allocations[i])
        #    metric[i] = server.compute_metric_PF(requests[i], rx_bits[i], t, reported_CQI[i], RB_allocations[i], 1, 0)
        #    metric[i] = server.compute_metric_PF(requests[i], rx_bits[i], t, reported_CQI[i], RB_allocations[i], 1, 1)
        #    metric[i] = server.compute_metric_newPF(requests[i], rx_bits[i], t_rx_bits[i], reported_CQI[i])

        # Allocate 1 RB to 1 user
        #last_reply, RB_allocations, total_RB_allocations = server.allocation(metric, RB_allocations, total_RB_allocations, last_reply, float(t) + float(k)/1000.0)

    # Update running status
    if not t % 1000:
        print "Progress (", str(config.U), "):", int(t/1000)

# Compute and store QoE values
for i in range(config.U):
    qoe[i] = qoe_model.compute_QoE(i, cnt_milisegments[i], cnt_stalls[i], sum_ql[i], sum_ql_sq[i], t_dur_stalls[i])
    qoe_worksheet.write(i, 1, qoe[i])
    qoe_worksheet.write(i, 2, sum_ql[i])
    qoe_worksheet.write(i, 3, sum_ql_sq[i])
    qoe_worksheet.write(i, 4, len(requests[i]))
    qoe_worksheet.write(i, 5, cnt_stalls[i])
    qoe_worksheet.write(i, 6, t_dur_stalls[i])
    qoe_worksheet.write(i, 7, t_dur_stalls[i]-dur_stalls[i])

    if qoe[i] >= 3:
        qoe3 += 1

        if qoe[i] >= 4:
            qoe4 += 1
    
    elif qoe[i] < 2:
        qoe2 += 1


qoe_workbook.close()

t_final = datetime.datetime.now()
print t_final
print t_final-t_init, '\n'

print "Global QoE >= 3:\t", 100*qoe3/float(config.U), "%"
print "Global QoE >= 4:\t", 100*qoe4/float(config.U), "%"
print "Global QoE < 2: \t", 100*qoe2/float(config.U), "%", '\n'
print int(config.U - qoe3)

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

                    if idx3 == 5 and idx2 == 3:
                        request_worksheet.write(idx2+0, idx3+(config.Nx*config.Ny)-2, k)
                        request_worksheet.write(idx2-1, idx3+(config.Nx*config.Ny)-2, k)
                        request_worksheet.write(idx2-2, idx3+(config.Nx*config.Ny)-2, k)

    buffer_workbook.close()
    allocation_workbook.close()
    request_workbook.close()