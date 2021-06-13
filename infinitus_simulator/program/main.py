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
#      Main Program     #
#                       #
#########################
t_init = datetime.datetime.now()
print(t_init)

# Open salient 360 dataset
salient360_dataset = client.open_file()

for sim in range(config.Sim):
    # Open excel workbook to store outputs
    qoe_workbook = xlsxwriter.Workbook('../results/qoe_PF_sim'+str(sim+1)+'.xlsx')
    qoe_worksheet = qoe_workbook.add_worksheet('Sim'+str(sim+1))

    for i in range(config.U[-1]):
        qoe_worksheet.write(i, 0, 'User'+str(i+1))

    qoe_worksheet.write(config.U[-1]+0, 0, "#Users")
    qoe_worksheet.write(config.U[-1]+1, 0, "QoE>=3")
    qoe_worksheet.write(config.U[-1]+2, 0, "QoE>=4")
    qoe_worksheet.write(config.U[-1]+3, 0, "QoE<2")

    for idx, U in enumerate(config.U):

        #########################
        #                       #
        # Progamming Variables  #
        #   (Initialization)    #
        #                       #
        #########################

        t = 0
        buffer = np.zeros(U, dtype=float)
        delta_buffer = np.zeros(U, dtype=float)
        rx_bits = np.zeros(U, dtype=float)
        play = np.zeros(U, dtype=int)
        reported_CQI = np.zeros(U, dtype=int)
        RB_allocations = np.zeros(U, dtype=int)
        total_RB_allocations = np.zeros(U, dtype=int)
        metric = np.zeros(U, dtype=float)
        last_reply = np.zeros(U, dtype=float)
        requests = [[]] * U

        # QoE variables
        cnt_stalls = np.zeros(U, dtype=int)
        perceived_stall = np.negative(np.ones(U, dtype=int))
        dur_stalls = np.zeros(U, dtype=int)
        t_dur_stalls = np.zeros(U, dtype=int)
        flg_qoe_init = [False for i in range(U)]
        flg_qoe = [False for i in range(U)]
        avg_stall = np.zeros(U, dtype=float)
        avg_quality = np.zeros(U, dtype=float)
        sum_ql = np.zeros(U, dtype=float)
        sum_ql_sq = np.zeros(U, dtype=float)
        sig_quality = np.zeros(U, dtype=float)
        qoe = np.zeros(U, dtype=float)

        for t in range(0, config.T+1, config.TTI):
            # CLIENT SIDE
            for i in range(U):
                # Update buffer
                if RB_allocations[i] != 0:
                    delta_buffer[i], rx_bits[i], requests[i] = client.buffer_update(i, requests[i], RB_allocations[i], rx_bits[i], t)
                    buffer[i] += delta_buffer[i]
                    # Buffer max. capacity; Check if there is enough content for playback after buffering
                    if buffer[i] >= config.B - 0.1:
                        buffer[i] = config.B
                        play[i] = 1

                # Buffering event
                if play[i] == 0:
                    if not requests[i] or requests[i][-1]['reply_bits'] == 0:
                        # Initial buffering - Request every tile with the lowest quality or if there is space - Request every tile with the lowest quality
                        requests[i] = client.request_LQ(requests[i], t)

                # Normal video playback
                else:
                    # There is space for a new segment and every request has been completly replied
                    if config.B - buffer[i] >= 1000 and requests[i][-1]['reply_bits'] == 0: 
                        # Request segment with rate adaptation (RA)
                        requests[i] = client.request_RA(requests[i], t, t_dur_stalls[i], client.throughput_estimation(requests[i]), salient360_dataset, i)

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
            RB_allocations = np.zeros(U, dtype=int)

            # Allocate each Kth RB
            for k in range(config.K):
                # Initialize metrics/RB_allocations arrays
                metric = np.negative(np.ones(U, dtype=float))
                
                # Compute each user metric
                for i in range(U):
                #    metric[i] = server.compute_metric_RR(requests[i], last_reply[i], t)
                #    metric[i] = server.compute_metric_BET(requests[i], rx_bits[i], t, reported_CQI[i], RB_allocations[i])
                    metric[i] = server.compute_metric_PF(requests[i], rx_bits[i], t, reported_CQI[i], RB_allocations[i], 1, 0)
                #    metric[i] = server.compute_metric_PF(requests[i], rx_bits[i], t, reported_CQI[i], RB_allocations[i], 1, 1)
            
                # Allocate 1 RB to 1 user
                last_reply, RB_allocations, total_RB_allocations = server.allocation(metric, RB_allocations, total_RB_allocations, last_reply, float(t) + float(k)/1000.0)

            # Update running status
            if not t % 2500:
                print "Progress (", str(U), "):", float(t/1000.0)

        # Compute and store QoE values
        for i in range(U):
            qoe[i] = qoe_model.compute_QoE(cnt_stalls[i], sum_ql[i], sum_ql_sq[i], t_dur_stalls[i])
            qoe_worksheet.write(i, idx+1, qoe[i])

            """qoe_worksheet.write(i, 1, qoe[i])
            qoe_worksheet.write(i, idx+2, sum_ql[i])
            qoe_worksheet.write(i, idx+3, sum_ql_sq[i])
            qoe_worksheet.write(i, idx+4, len(requests[i]))
            qoe_worksheet.write(i, idx+5, cnt_stalls[i])
            qoe_worksheet.write(i, idx+6, t_dur_stalls[i])
            qoe_worksheet.write(i, idx+7, t_dur_stalls[i]-dur_stalls[i])"""

        qoe_worksheet.write(config.U[-1]+0, idx+1, U)
        qoe_worksheet.write(config.U[-1]+1, idx+1, sum(i >= 3 for i in qoe)/float(U))
        qoe_worksheet.write(config.U[-1]+2, idx+1, sum(i >= 4 for i in qoe)/float(U))
        qoe_worksheet.write(config.U[-1]+3, idx+1, sum(i < 2 for i in qoe)/float(U))


    qoe_workbook.close()

    t_final = datetime.datetime.now()
    print(t_final)
    print(t_final-t_init)