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
    for U in config.U:
        qoe_workbook = xlsxwriter.Workbook('../results/'+str(sim+1)+'/qoe_python3_u'+str(U)+'_t'+str(int(config.T/1000))+'.xlsx')
        qoe_worksheet = qoe_workbook.add_worksheet()
        for i in range(U):
            qoe_worksheet.write(i, 0, 'User'+str(i+1))

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
        last_reply = np.zeros(U, dtype=int)
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

        print("Progress (", str(U), "): 0.00 %")

        for t in range(0, config.T+1, config.TTI):
            # CLIENT SIDE
            for i in range(U):
                # Update buffer
                if RB_allocations[i] != 0:
                    delta_buffer[i], rx_bits[i] = client.buffer_update(i, requests[i], RB_allocations[i], rx_bits[i], t)
                    buffer[i] += delta_buffer[i]
                    # Buffer max. capacity; Check if there is enough content for playback after buffering
                    if buffer[i] > config.B:
                        buffer[i] = config.B
                        play[i] = 1

                # Buffering event
                if play[i] == 0:
                    if not requests[i] or requests[i][-1]['reply_bits'] == 0:
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
            RB_allocations = np.zeros(U, dtype=int)

            RB_allocations, total_RB_allocations = server.allocation_RR(requests, RB_allocations, total_RB_allocations, U)

            # Update running status
            if not t % 1000:
                print("Progress (", str(U), "):", int(t/1000))

        # Compute and store QoE values
        for i in range(U):
            qoe[i] = qoe_model.compute_QoE(cnt_stalls[i], sum_ql[i], sum_ql_sq[i], t_dur_stalls[i], config.T)
            qoe_worksheet.write(i, 1, qoe[i])
            qoe_worksheet.write(i, 2, cnt_stalls[i])
            qoe_worksheet.write(i, 3, sum_ql[i])
            qoe_worksheet.write(i, 4, t_dur_stalls[i])

        qoe_workbook.close()

t_final = datetime.datetime.now()
print(t_final)
print(t_final-t_init)