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
    qoe_workbook = xlsxwriter.Workbook('../results/qoe_simOLD_RR'+str(sim+1)+'.xlsx')
    qoe_worksheet = qoe_workbook.add_worksheet('Sim'+str(sim+1))

    for i in range(config.U[-1]):
        qoe_worksheet.write(i+1, 0, 'User'+str(i+1))

    qoe_worksheet.write(config.U[-1]+1, 0, "#Users")
    qoe_worksheet.write(config.U[-1]+2, 0, "QoE>=3")
    qoe_worksheet.write(config.U[-1]+3, 0, "QoE>=4")
    qoe_worksheet.write(config.U[-1]+4, 0, "QoE<2")

    for i in range(len(config.U)):
        qoe_worksheet.write(config.U[-1]+1, len(config.U)*0+i+1, config.U[i])
        qoe_worksheet.write(0, len(config.U)*0+i+1, 'RR')
        qoe_worksheet.write(config.U[-1]+1, len(config.U)*1+i+1, config.U[i])
        qoe_worksheet.write(0, len(config.U)*1+i+1, 'BET')
        qoe_worksheet.write(config.U[-1]+1, len(config.U)*2+i+1, config.U[i])
        qoe_worksheet.write(0, len(config.U)*2+i+1, 'MT')
        qoe_worksheet.write(config.U[-1]+1, len(config.U)*3+i+1, config.U[i])
        qoe_worksheet.write(0, len(config.U)*3+i+1, 'PF')

    for idx, U in enumerate(config.U):

        #########################
        #                       #
        # Progamming Variables  #
        #   (Initialization)    #
        #                       #
        #########################

        t = 0
        reported_CQI = np.zeros(U, dtype=int)
        user_CQI = np.zeros(U, dtype=int)

        # RR parameters
        buffer_RR = np.zeros(U, dtype=float)
        delta_buffer_RR = np.zeros(U, dtype=float)
        rx_bits_RR = np.zeros(U, dtype=float)
        play_RR = np.zeros(U, dtype=int)
        RB_allocations_RR = np.zeros(U, dtype=int)
        total_RB_allocations_RR = np.zeros(U, dtype=int)
        metric_RR = np.zeros(U, dtype=float)
        last_reply_RR = np.zeros(U, dtype=float)
        requests_RR = [[]] * U

        # BET parameters
        """buffer_BET = np.zeros(U, dtype=float)
        delta_buffer_BET = np.zeros(U, dtype=float)
        rx_bits_BET = np.zeros(U, dtype=float)
        play_BET = np.zeros(U, dtype=int)
        RB_allocations_BET = np.zeros(U, dtype=int)
        total_RB_allocations_BET = np.zeros(U, dtype=int)
        metric_BET = np.zeros(U, dtype=float)
        last_reply_BET = np.zeros(U, dtype=float)
        requests_BET = [[]] * U

        # MT parameters
        buffer_MT = np.zeros(U, dtype=float)
        delta_buffer_MT = np.zeros(U, dtype=float)
        rx_bits_MT = np.zeros(U, dtype=float)
        play_MT = np.zeros(U, dtype=int)
        RB_allocations_MT = np.zeros(U, dtype=int)
        total_RB_allocations_MT = np.zeros(U, dtype=int)
        metric_MT = np.zeros(U, dtype=float)
        last_reply_MT = np.zeros(U, dtype=float)
        requests_MT = [[]] * U

        # PF parameters
        buffer_PF = np.zeros(U, dtype=float)
        delta_buffer_PF = np.zeros(U, dtype=float)
        rx_bits_PF = np.zeros(U, dtype=float)
        play_PF = np.zeros(U, dtype=int)
        RB_allocations_PF = np.zeros(U, dtype=int)
        total_RB_allocations_PF = np.zeros(U, dtype=int)
        metric_PF = np.zeros(U, dtype=float)
        last_reply_PF = np.zeros(U, dtype=float)
        requests_PF = [[]] * U"""

        # QoE parameters
        # RR QoE parameters
        cnt_stalls_RR = np.zeros(U, dtype=int)
        perceived_stall_RR = np.negative(np.ones(U, dtype=int))
        dur_stalls_RR = np.zeros(U, dtype=int)
        t_dur_stalls_RR = np.zeros(U, dtype=int)
        flg_qoe_init_RR = [False for i in range(U)]
        flg_qoe_RR = [False for i in range(U)]
        avg_stall_RR = np.zeros(U, dtype=float)
        avg_quality_RR = np.zeros(U, dtype=float)
        sum_ql_RR = np.zeros(U, dtype=float)
        sum_ql_sq_RR = np.zeros(U, dtype=float)
        sig_quality_RR = np.zeros(U, dtype=float)
        qoe_RR = np.zeros(U, dtype=float)

        # BET QoE parameters
        """cnt_stalls_BET = np.zeros(U, dtype=int)
        perceived_stall_BET = np.negative(np.ones(U, dtype=int))
        dur_stalls_BET = np.zeros(U, dtype=int)
        t_dur_stalls_BET = np.zeros(U, dtype=int)
        flg_qoe_init_BET = [False for i in range(U)]
        flg_qoe_BET = [False for i in range(U)]
        avg_stall_BET = np.zeros(U, dtype=float)
        avg_quality_BET = np.zeros(U, dtype=float)
        sum_ql_BET = np.zeros(U, dtype=float)
        sum_ql_sq_BET = np.zeros(U, dtype=float)
        sig_quality_BET = np.zeros(U, dtype=float)
        qoe_BET = np.zeros(U, dtype=float)

        # MT QoE parameters
        cnt_stalls_MT = np.zeros(U, dtype=int)
        perceived_stall_MT = np.negative(np.ones(U, dtype=int))
        dur_stalls_MT = np.zeros(U, dtype=int)
        t_dur_stalls_MT = np.zeros(U, dtype=int)
        flg_qoe_init_MT = [False for i in range(U)]
        flg_qoe_MT = [False for i in range(U)]
        avg_stall_MT = np.zeros(U, dtype=float)
        avg_quality_MT = np.zeros(U, dtype=float)
        sum_ql_MT = np.zeros(U, dtype=float)
        sum_ql_sq_MT = np.zeros(U, dtype=float)
        sig_quality_MT = np.zeros(U, dtype=float)
        qoe_MT = np.zeros(U, dtype=float)

        # PF QoE parameters
        cnt_stalls_PF = np.zeros(U, dtype=int)
        perceived_stall_PF = np.negative(np.ones(U, dtype=int))
        dur_stalls_PF = np.zeros(U, dtype=int)
        t_dur_stalls_PF = np.zeros(U, dtype=int)
        flg_qoe_init_PF = [False for i in range(U)]
        flg_qoe_PF = [False for i in range(U)]
        avg_stall_PF = np.zeros(U, dtype=float)
        avg_quality_PF = np.zeros(U, dtype=float)
        sum_ql_PF = np.zeros(U, dtype=float)
        sum_ql_sq_PF = np.zeros(U, dtype=float)
        sig_quality_PF = np.zeros(U, dtype=float)
        qoe_PF = np.zeros(U, dtype=float)"""

        for t in range(0, config.T+1, config.TTI):
            # CLIENT SIDE
            #print
            for i in range(U):
                # Get user's current CQI
                user_CQI[i] = client.get_CQI(i, t, sim)
                
                # Update buffer
                # RR
                if RB_allocations_RR[i] != 0:
                    delta_buffer_RR[i], rx_bits_RR[i], requests_RR[i] = client.buffer_update(user_CQI[i], requests_RR[i], RB_allocations_RR[i], rx_bits_RR[i], t)
                    buffer_RR[i] += delta_buffer_RR[i]

                    # Buffer max. capacity; Check if there is enough content for playback after buffering
                    if buffer_RR[i] >= config.init - 0.1:
                        #buffer_RR[i] = config.B
                        play_RR[i] = 1
                # BET
                """if RB_allocations_BET[i] != 0:
                    delta_buffer_BET[i], rx_bits_BET[i], requests_BET[i] = client.buffer_update(user_CQI[i], requests_BET[i], RB_allocations_BET[i], rx_bits_BET[i], t)
                    buffer_BET[i] += delta_buffer_BET[i]

                    # Buffer max. capacity; Check if there is enough content for playback after buffering
                    if buffer_BET[i] >= config.init - 0.1:
                        #buffer_BET[i] = config.B
                        play_BET[i] = 1

                # MT
                if RB_allocations_MT[i] != 0:
                    delta_buffer_MT[i], rx_bits_MT[i], requests_MT[i] = client.buffer_update(user_CQI[i], requests_MT[i], RB_allocations_MT[i], rx_bits_MT[i], t)
                    buffer_MT[i] += delta_buffer_MT[i]
                    
                    if buffer_MT[i] >= config.init - 0.1:
                        #buffer_MT[i] = config.B
                        play_MT[i] = 1

                # PF
                if RB_allocations_PF[i] != 0:
                    delta_buffer_PF[i], rx_bits_PF[i], requests_PF[i] = client.buffer_update(user_CQI[i], requests_PF[i], RB_allocations_PF[i], rx_bits_PF[i], t)
                    buffer_PF[i] += delta_buffer_PF[i]

                    # Buffer max. capacity; Check if there is enough content for playback after buffering
                    if buffer_PF[i] >= config.init - 0.1:
                        #buffer_PF[i] = config.B
                        play_PF[i] = 1"""

                # Buffering event
                # RR
                if play_RR[i] == 0:
                    if not requests_RR[i] or requests_RR[i][-1]['reply_bits'] == 0:
                        # Initial buffering - Request every tile with the lowest quality or if there is space - Request every tile with the lowest quality
                        requests_RR[i] = client.request_LQ(requests_RR[i], t)

                # Normal video playback
                else:
                    # There is space for a new segment and every request has been completly replied
                    if config.B - buffer_RR[i] >= 1000 and requests_RR[i][-1]['reply_bits'] == 0: 
                        # Request segment with rate adaptation (RA)
                        requests_RR[i] = client.request_RA(requests_RR[i], t, t_dur_stalls_RR[i],client.throughput_estimation(requests_RR[i]), salient360_dataset, i, buffer_RR[i], sim)

                    # Client watches TTI seconds of video
                    buffer_RR[i] -= config.TTI

                    # Client suffers a stall event
                    if buffer_RR[i] <= 0:
                        buffer_RR[i] = 0
                        play_RR[i] = 0

                # BET
                """if play_BET[i] == 0:
                    if not requests_BET[i] or requests_BET[i][-1]['reply_bits'] == 0:
                        # Initial buffering - Request every tile with the lowest quality or if there is space - Request every tile with the lowest quality
                        requests_BET[i] = client.request_LQ(requests_BET[i], t)

                # Normal video playback
                else:
                    # There is space for a new segment and every request has been completly replied
                    if config.B - buffer_BET[i] >= 1000 and requests_BET[i][-1]['reply_bits'] == 0: 
                        # Request segment with rate adaptation (RA)
                        requests_BET[i] = client.request_RA(requests_BET[i], t, t_dur_stalls_BET[i],client.throughput_estimation(requests_BET[i]), salient360_dataset, i, buffer_BET[i], sim)

                    # Client watches TTI seconds of video
                    buffer_BET[i] -= config.TTI

                    # Client suffers a stall event
                    if buffer_BET[i] <= 0:
                        buffer_BET[i] = 0
                        play_BET[i] = 0

                # MT
                if play_MT[i] == 0:
                    if not requests_MT[i] or requests_MT[i][-1]['reply_bits'] == 0:
                        # Initial buffering - Request every tile with the lowest quality or if there is space - Request every tile with the lowest quality
                        requests_MT[i] = client.request_LQ(requests_MT[i], t)

                # Normal video playback
                else:
                    # There is space for a new segment and every request has been completly replied
                    if config.B - buffer_MT[i] >= 1000 and requests_MT[i][-1]['reply_bits'] == 0: 
                        # Request segment with rate adaptation (RA)
                        requests_MT[i] = client.request_RA(requests_MT[i], t, t_dur_stalls_MT[i],client.throughput_estimation(requests_MT[i]), salient360_dataset, i, buffer_MT[i], sim)

                    # Client watches TTI seconds of video
                    buffer_MT[i] -= config.TTI

                    # Client suffers a stall event
                    if buffer_MT[i] <= 0:
                        buffer_MT[i] = 0
                        play_MT[i] = 0

                # PF
                if play_PF[i] == 0:
                    if not requests_PF[i] or requests_PF[i][-1]['reply_bits'] == 0:
                        # Initial buffering - Request every tile with the lowest quality or if there is space - Request every tile with the lowest quality
                        requests_PF[i] = client.request_LQ(requests_PF[i], t)

                # Normal video playback
                else:
                    # There is space for a new segment and every request has been completly replied
                    if config.B - buffer_PF[i] >= 1000 and requests_PF[i][-1]['reply_bits'] == 0: 
                        # Request segment with rate adaptation (RA)
                        requests_PF[i] = client.request_RA(requests_PF[i], t, t_dur_stalls_PF[i],client.throughput_estimation(requests_PF[i]), salient360_dataset, i, buffer_PF[i], sim)

                    # Client watches TTI seconds of video
                    buffer_PF[i] -= config.TTI

                    # Client suffers a stall event
                    if buffer_PF[i] <= 0:
                        buffer_PF[i] = 0
                        play_PF[i] = 0"""

                # Update QoE inputs
                cnt_stalls_RR[i], perceived_stall_RR[i], dur_stalls_RR[i], t_dur_stalls_RR[i], sum_ql_RR[i], sum_ql_sq_RR[i], flg_qoe_RR[i], flg_qoe_init_RR[i]  = qoe_model.update_QoE(cnt_stalls_RR[i], perceived_stall_RR[i], dur_stalls_RR[i], t_dur_stalls_RR[i], sum_ql_RR[i], sum_ql_sq_RR[i], play_RR[i], flg_qoe_RR[i], flg_qoe_init_RR[i], requests_RR[i], salient360_dataset, i, t, sim)
                """cnt_stalls_BET[i], perceived_stall_BET[i], dur_stalls_BET[i], t_dur_stalls_BET[i], sum_ql_BET[i], sum_ql_sq_BET[i], flg_qoe_BET[i], flg_qoe_init_BET[i]  = qoe_model.update_QoE(cnt_stalls_BET[i], perceived_stall_BET[i], dur_stalls_BET[i], t_dur_stalls_BET[i], sum_ql_BET[i], sum_ql_sq_BET[i], play_BET[i], flg_qoe_BET[i], flg_qoe_init_BET[i], requests_BET[i], salient360_dataset, i, t, sim)
                cnt_stalls_MT[i], perceived_stall_MT[i], dur_stalls_MT[i], t_dur_stalls_MT[i], sum_ql_MT[i], sum_ql_sq_MT[i], flg_qoe_MT[i], flg_qoe_init_MT[i]  = qoe_model.update_QoE(cnt_stalls_MT[i], perceived_stall_MT[i], dur_stalls_MT[i], t_dur_stalls_MT[i], sum_ql_MT[i], sum_ql_sq_MT[i], play_MT[i], flg_qoe_MT[i], flg_qoe_init_MT[i], requests_MT[i], salient360_dataset, i, t, sim)
                cnt_stalls_PF[i], perceived_stall_PF[i], dur_stalls_PF[i], t_dur_stalls_PF[i], sum_ql_PF[i], sum_ql_sq_PF[i], flg_qoe_PF[i], flg_qoe_init_PF[i]  = qoe_model.update_QoE(cnt_stalls_PF[i], perceived_stall_PF[i], dur_stalls_PF[i], t_dur_stalls_PF[i], sum_ql_PF[i], sum_ql_sq_PF[i], play_PF[i], flg_qoe_PF[i], flg_qoe_init_PF[i], requests_PF[i], salient360_dataset, i, t, sim)"""

                # Report CQI
                if t % 5 == 0:
                    reported_CQI[i] = client.get_CQI(i, t, sim)

            # SERVER SIDE
            RB_allocations_RR = np.zeros(U, dtype=int)
            """RB_allocations_BET = np.zeros(U, dtype=int)
            RB_allocations_MT = np.zeros(U, dtype=int)
            RB_allocations_PF = np.zeros(U, dtype=int)"""

            # Allocate each Kth RB
            for k in range(config.K):
                # Initialize metrics/RB_allocations arrays
                metric_RR = np.negative(np.ones(U, dtype=float))
                """metric_BET = np.negative(np.ones(U, dtype=float))
                metric_MT = np.negative(np.ones(U, dtype=float))
                metric_PF = np.negative(np.ones(U, dtype=float))"""
                
                # Compute each user metric
                for i in range(U):
                    metric_RR[i] = server.compute_metric_RR(requests_RR[i], last_reply_RR[i], t)
                    """metric_BET[i] = server.compute_metric_BET(requests_BET[i], rx_bits_BET[i], t, reported_CQI[i], RB_allocations_BET[i])
                    metric_MT[i] = server.compute_metric_PF(requests_MT[i], rx_bits_MT[i], t, reported_CQI[i], RB_allocations_MT[i], 1, 0)
                    metric_PF[i] = server.compute_metric_PF(requests_PF[i], rx_bits_PF[i], t, reported_CQI[i], RB_allocations_PF[i], 1, 1)"""
            
                # Allocate 1 RB to 1 user
                last_reply_RR, RB_allocations_RR, total_RB_allocations_RR = server.allocation(metric_RR, RB_allocations_RR, total_RB_allocations_RR, last_reply_RR, float(t) + float(k)/1000.0)
                """last_reply_BET, RB_allocations_BET, total_RB_allocations_BET = server.allocation(metric_BET, RB_allocations_BET, total_RB_allocations_BET, last_reply_BET, float(t) + float(k)/1000.0)
                last_reply_MT, RB_allocations_MT, total_RB_allocations_MT = server.allocation(metric_MT, RB_allocations_MT, total_RB_allocations_MT, last_reply_MT, float(t) + float(k)/1000.0)
                last_reply_PF, RB_allocations_PF, total_RB_allocations_PF = server.allocation(metric_PF, RB_allocations_PF, total_RB_allocations_PF, last_reply_PF, float(t) + float(k)/1000.0)"""

            # Update running status
            if not t % 2500:
                print "Progress (", str(U), "):", float(t/1000.0)

        # Compute and store QoE values
        for i in range(U):
            qoe_RR[i] = qoe_model.compute_QoE(i, cnt_stalls_RR[i], sum_ql_RR[i], sum_ql_sq_RR[i], t_dur_stalls_RR[i])
            """qoe_BET[i] = qoe_model.compute_QoE(cnt_stalls_BET[i], sum_ql_BET[i], sum_ql_sq_BET[i], t_dur_stalls_BET[i])
            qoe_MT[i] = qoe_model.compute_QoE(cnt_stalls_MT[i], sum_ql_MT[i], sum_ql_sq_MT[i], t_dur_stalls_MT[i])
            qoe_PF[i] = qoe_model.compute_QoE(cnt_stalls_PF[i], sum_ql_PF[i], sum_ql_sq_PF[i], t_dur_stalls_PF[i])"""

            qoe_worksheet.write(i+1, len(config.U)*0+idx+1, qoe_RR[i])
            """qoe_worksheet.write(i+1, len(config.U)*1+idx+1, qoe_BET[i])
            qoe_worksheet.write(i+1, len(config.U)*2+idx+1, qoe_MT[i])
            qoe_worksheet.write(i+1, len(config.U)*3+idx+1, qoe_PF[i])"""

            #qoe_worksheet.write(i, 1, qoe[i])
            #qoe_worksheet.write(i, idx+2, sum_ql[i])
            #qoe_worksheet.write(i, idx+3, sum_ql_sq[i])
            #qoe_worksheet.write(i, idx+4, len(requests[i]))
            #qoe_worksheet.write(i, idx+5, cnt_stalls[i])
            #qoe_worksheet.write(i, idx+6, t_dur_stalls[i])
            #qoe_worksheet.write(i, idx+7, t_dur_stalls[i]-dur_stalls[i])

        qoe_worksheet.write(config.U[-1]+2, len(config.U)*0+idx+1, sum(i >= 3 for i in qoe_RR)/float(U))
        qoe_worksheet.write(config.U[-1]+3, len(config.U)*0+idx+1, sum(i >= 4 for i in qoe_RR)/float(U))
        qoe_worksheet.write(config.U[-1]+4, len(config.U)*0+idx+1, sum(i < 2 for i in qoe_RR)/float(U))

        """qoe_worksheet.write(config.U[-1]+2, len(config.U)*1+idx+1, sum(i >= 3 for i in qoe_BET)/float(U))
        qoe_worksheet.write(config.U[-1]+3, len(config.U)*1+idx+1, sum(i >= 4 for i in qoe_BET)/float(U))
        qoe_worksheet.write(config.U[-1]+4, len(config.U)*1+idx+1, sum(i < 2 for i in qoe_BET)/float(U))

        qoe_worksheet.write(config.U[-1]+2, len(config.U)*2+idx+1, sum(i >= 3 for i in qoe_MT)/float(U))
        qoe_worksheet.write(config.U[-1]+3, len(config.U)*2+idx+1, sum(i >= 4 for i in qoe_MT)/float(U))
        qoe_worksheet.write(config.U[-1]+4, len(config.U)*2+idx+1, sum(i < 2 for i in qoe_MT)/float(U))

        qoe_worksheet.write(config.U[-1]+2, len(config.U)*3+idx+1, sum(i >= 3 for i in qoe_PF)/float(U))
        qoe_worksheet.write(config.U[-1]+3, len(config.U)*3+idx+1, sum(i >= 4 for i in qoe_PF)/float(U))
        qoe_worksheet.write(config.U[-1]+4, len(config.U)*3+idx+1, sum(i < 2 for i in qoe_PF)/float(U))"""


    qoe_workbook.close()

    t_final = datetime.datetime.now()
    print(t_final)
    print(t_final-t_init)