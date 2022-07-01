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


REPORT = True

if REPORT:
    buffer_workbook = xlsxwriter.Workbook('../results/buffer.xlsx')
    buffer_worksheet = buffer_workbook.add_worksheet()

    allocation_workbook = xlsxwriter.Workbook('../results/allocation.xlsx')
    allocation_worksheet = allocation_workbook.add_worksheet()

    request_workbook = xlsxwriter.Workbook('../results/request.xlsx')

    buffer_worksheet.write(0, 0, 'Time')
    allocation_worksheet.write(0, 0, 'Time')

    for i in range(config.T+1):
        buffer_worksheet.write(i+1, 0, i)
        allocation_worksheet.write(i+1, 0, i)

    for i in range(config.U[0]):
        buffer_worksheet.write(0, 5*i+1, 'User'+str(i+1))
        buffer_worksheet.write(0, 5*i+2, 'Play'+str(i+1))
        buffer_worksheet.write(0, 5*i+3, 'avg_U'+str(i+1))
        buffer_worksheet.write(0, 5*i+4, 'Metric'+str(i+1))
        buffer_worksheet.write(0, 5*i+5, 'ach_U'+str(i+1))
        allocation_worksheet.write(0, 2*i+1, 'CummulativeRB'+str(i+1))
        allocation_worksheet.write(0, 2*i+2, 'InstantRB'+str(i+1))

for sim in range(config.Sim):
    # Open excel workbook to store outputs
    qoe_workbook = xlsxwriter.Workbook('../results/qoe_sim'+str(sim+1)+'.xlsx')
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
        requests_BET = [[]] * U"""

        # MT parameters
        """buffer_MT = np.zeros(U, dtype=float)
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
        K_bits_RR = np.zeros(U, dtype=float)
        throughput_RR = np.zeros(U, dtype=float)

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
        qoe_BET = np.zeros(U, dtype=float)"""

        # MT QoE parameters
        """cnt_stalls_MT = np.zeros(U, dtype=int)
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
            for i in range(U):
                # Get user's current CQI
                user_CQI[i] = client.get_CQI(i, t, sim)

                if not t % config.theta and t != 0:
                    throughput_RR[i] = client.estimate_throughput(throughput_RR[i], K_bits_RR[i], t, buffer_RR[i])
                    K_bits_RR[i] = 0

                # Update buffer
                # RR
                if RB_allocations_RR[i] != 0:
                    delta_buffer_RR[i], rx_bits_RR[i], K_bits_RR[i], requests_RR[i] = client.buffer_update(user_CQI[i], requests_RR[i], RB_allocations_RR[i], rx_bits_RR[i], K_bits_RR[i], t)
                    buffer_RR[i] += delta_buffer_RR[i]

                    # Buffer max. capacity; Check if there is enough content for playback after buffering
                    #if buffer_RR[i] >= config.B - 0.1:
                    #    buffer_RR[i] = config.B
                    #    play_RR[i] = 1
                    if buffer_RR[i] >= config.Binit - 0.1:
                        play_RR[i] = 1

                # BET
                """if RB_allocations_BET[i] != 0:
                    delta_buffer_BET[i], rx_bits_BET[i], requests_BET[i] = client.buffer_update(user_CQI[i], requests_BET[i], RB_allocations_BET[i], rx_bits_BET[i], t)
                    buffer_BET[i] += delta_buffer_BET[i]

                    # Buffer max. capacity; Check if there is enough content for playback after buffering
                    #if buffer_BET[i] >= config.B - 0.1:
                    #    buffer_BET[i] = config.B
                    #    play_BET[i] = 1
                    if buffer_BET[i] >= 5*10**3 - 0.1:
                        play_BET[i] = 1"""

                # MT
                """if RB_allocations_MT[i] != 0:
                    delta_buffer_MT[i], rx_bits_MT[i], requests_MT[i] = client.buffer_update(user_CQI[i], requests_MT[i], RB_allocations_MT[i], rx_bits_MT[i], t)
                    buffer_MT[i] += delta_buffer_MT[i]
                    
                    #if buffer_MT[i] >= config.B - 0.1:
                    #    buffer_MT[i] = config.B
                    #    play_MT[i] = 1
                    if buffer_MT[i] >= 5*10**3 - 0.1:
                        play_MT[i] = 1

                # PF
                if RB_allocations_PF[i] != 0:
                    delta_buffer_PF[i], rx_bits_PF[i], requests_PF[i] = client.buffer_update(user_CQI[i], requests_PF[i], RB_allocations_PF[i], rx_bits_PF[i], t)
                    buffer_PF[i] += delta_buffer_PF[i]

                    # Buffer max. capacity; Check if there is enough content for playback after buffering
                    #if buffer_PF[i] >= config.B - 0.1:
                    #    buffer_PF[i] = config.B
                    #    play_PF[i] = 1
                    if buffer_PF[i] >= 5*10**3 - 0.1:
                        play_PF[i] = 1"""

                # Store buffer parameters
                if REPORT:
                    client.store_buffer(t, i, buffer_worksheet, allocation_worksheet, buffer_RR[i], play_RR[i], rx_bits_RR[i], reported_CQI[i], metric_RR[i], total_RB_allocations_RR[i], RB_allocations_RR[i])
                    #client.store_buffer(t, i, buffer_worksheet, allocation_worksheet, buffer_BET[i], play_BET[i], rx_bits_BET[i], reported_CQI[i], metric_BET[i], total_RB_allocations_BET[i], RB_allocations_BET[i])

                # Buffering event
                # RR
                if play_RR[i] == 0:
                    if not requests_RR[i] or requests_RR[i][-1]['reply_bits'] == 0:
                        # Initial buffering - Request every tile with the lowest quality or if there is space - Request every tile with the lowest quality
                        requests_RR[i] = client.request_LQ(requests_RR[i], t)

                # Normal video playback
                else:
                    # There is space for a new segment and every request has been completly replied
                    if requests_RR[i][-1]['reply_bits'] == 0: 
                        # Request segment with rate adaptation (RA)
                        requests_RR[i] = client.request_RA_QAAD(requests_RR[i], t, throughput_RR[i], buffer_RR[i])
                        #requests_RR[i] = client.request_RA_QAAD(requests_RR[i], t, client.throughput_estimation(requests_RR[i]), buffer_RR[i])
                        #requests_RR[i] = client.request_RA(requests_RR[i], t, t_dur_stalls_RR[i], client.throughput_estimation(requests_RR[i]), buffer_RR[i])

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
                    if requests_BET[i][-1]['reply_bits'] == 0: 
                        # Request segment with rate adaptation (RA)
                        requests_BET[i] = client.request_RA(requests_BET[i], t, t_dur_stalls_BET[i], client.throughput_estimation(requests_BET[i]))

                    # Client watches TTI seconds of video
                    buffer_BET[i] -= config.TTI

                    # Client suffers a stall event
                    if buffer_BET[i] <= 0:
                        buffer_BET[i] = 0
                        play_BET[i] = 0"""

                # MT
                """if play_MT[i] == 0:
                    if not requests_MT[i] or requests_MT[i][-1]['reply_bits'] == 0:
                        # Initial buffering - Request every tile with the lowest quality or if there is space - Request every tile with the lowest quality
                        requests_MT[i] = client.request_LQ(requests_MT[i], t)

                # Normal video playback
                else:
                    # There is space for a new segment and every request has been completly replied
                    if requests_MT[i][-1]['reply_bits'] == 0: 
                        # Request segment with rate adaptation (RA)
                        requests_MT[i] = client.request_RA(requests_MT[i], t, t_dur_stalls_MT[i], client.throughput_estimation(requests_MT[i]))

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
                    if requests_PF[i][-1]['reply_bits'] == 0: 
                        # Request segment with rate adaptation (RA)
                        requests_PF[i] = client.request_RA(requests_PF[i], t, t_dur_stalls_PF[i], client.throughput_estimation(requests_PF[i]))

                    # Client watches TTI seconds of video
                    buffer_PF[i] -= config.TTI

                    # Client suffers a stall event
                    if buffer_PF[i] <= 0:
                        buffer_PF[i] = 0
                        play_PF[i] = 0"""

                # Update QoE inputs
                cnt_stalls_RR[i], perceived_stall_RR[i], dur_stalls_RR[i], t_dur_stalls_RR[i], flg_qoe_RR[i], flg_qoe_init_RR[i]  = qoe_model.stall_update_Fred(cnt_stalls_RR[i], perceived_stall_RR[i], dur_stalls_RR[i], t_dur_stalls_RR[i], play_RR[i], flg_qoe_RR[i], flg_qoe_init_RR[i])
                #cnt_stalls_BET[i], perceived_stall_BET[i], dur_stalls_BET[i], t_dur_stalls_BET[i], flg_qoe_BET[i], flg_qoe_init_BET[i]  = qoe_model.stall_update_Fred(cnt_stalls_BET[i], perceived_stall_BET[i], dur_stalls_BET[i], t_dur_stalls_BET[i], play_BET[i], flg_qoe_BET[i], flg_qoe_init_BET[i])
                #cnt_stalls_MT[i], perceived_stall_MT[i], dur_stalls_MT[i], t_dur_stalls_MT[i], flg_qoe_MT[i], flg_qoe_init_MT[i]  = qoe_model.stall_update_Fred(cnt_stalls_MT[i], perceived_stall_MT[i], dur_stalls_MT[i], t_dur_stalls_MT[i], play_MT[i], flg_qoe_MT[i], flg_qoe_init_MT[i])
                #cnt_stalls_PF[i], perceived_stall_PF[i], dur_stalls_PF[i], t_dur_stalls_PF[i], flg_qoe_PF[i], flg_qoe_init_PF[i]  = qoe_model.stall_update_Fred(cnt_stalls_PF[i], perceived_stall_PF[i], dur_stalls_PF[i], t_dur_stalls_PF[i], play_PF[i], flg_qoe_PF[i], flg_qoe_init_PF[i])

                # Report CQI
                if t % 5 == 0:
                    reported_CQI[i] = user_CQI[i]

            # SERVER SIDE
            RB_allocations_RR = np.zeros(U, dtype=int)
            #RB_allocations_BET = np.zeros(U, dtype=int)
            #RB_allocations_MT = np.zeros(U, dtype=int)
            #RB_allocations_PF = np.zeros(U, dtype=int)

            #RB_allocations_RR, total_RB_allocations_RR = server.allocation_RR(requests_RR, RB_allocations_RR, total_RB_allocations_RR, U)

            # Allocate each Kth RB
            for k in range(config.K):
                # Initialize metrics/RB_allocations arrays
                metric_RR = np.negative(np.ones(U, dtype=float))
                #metric_BET = np.negative(np.ones(U, dtype=float))
                #metric_MT = np.negative(np.ones(U, dtype=float))
                #metric_PF = np.negative(np.ones(U, dtype=float))
                
                # Compute each user metric
                for i in range(U):
                    metric_RR[i] = server.compute_metric_RR(requests_RR[i], last_reply_RR[i], t)
                    #metric_BET[i] = server.compute_metric_BET(requests_BET[i], rx_bits_BET[i], t, reported_CQI[i], RB_allocations_BET[i])
                    #metric_MT[i] = server.compute_metric_PF(requests_MT[i], rx_bits_MT[i], t, reported_CQI[i], RB_allocations_MT[i], 1, 0)
                    #metric_PF[i] = server.compute_metric_PF(requests_PF[i], rx_bits_PF[i], t, reported_CQI[i], RB_allocations_PF[i], 1, 1)
            
                # Allocate 1 RB to 1 user
                last_reply_RR, RB_allocations_RR, total_RB_allocations_RR = server.allocation(metric_RR, RB_allocations_RR, total_RB_allocations_RR, last_reply_RR, float(t) + float(k)/1000.0)
                #last_reply_BET, RB_allocations_BET, total_RB_allocations_BET = server.allocation(metric_BET, RB_allocations_BET, total_RB_allocations_BET, last_reply_BET, float(t) + float(k)/1000.0)
                #last_reply_MT, RB_allocations_MT, total_RB_allocations_MT = server.allocation(metric_MT, RB_allocations_MT, total_RB_allocations_MT, last_reply_MT, float(t) + float(k)/1000.0)
                #last_reply_PF, RB_allocations_PF, total_RB_allocations_PF = server.allocation(metric_PF, RB_allocations_PF, total_RB_allocations_PF, last_reply_PF, float(t) + float(k)/1000.0)

            # Update running status
            if not t % 2500:
                print "Progress (", str(U), "):", float(t/1000.0)

        # Compute and store QoE values
        for i in range(U):
            #qoe_RR[i] = qoe_model.compute_QoE(cnt_stalls_RR[i], t_dur_stalls_RR[i], requests_RR[i])
            #qoe_BET[i] = qoe_model.compute_QoE(cnt_stalls_BET[i], t_dur_stalls_BET[i], requests_BET[i])
            #qoe_MT[i] = qoe_model.compute_QoE(cnt_stalls_MT[i], t_dur_stalls_MT[i], requests_MT[i])
            #qoe_PF[i] = qoe_model.compute_QoE(cnt_stalls_PF[i], t_dur_stalls_PF[i], requests_PF[i])

            qoe_worksheet.write(i+1, len(config.U)*0+idx+1, qoe_RR[i])
            #qoe_worksheet.write(i+1, len(config.U)*1+idx+1, qoe_BET[i])
            #qoe_worksheet.write(i+1, len(config.U)*2+idx+1, qoe_MT[i])
            #qoe_worksheet.write(i+1, len(config.U)*3+idx+1, qoe_PF[i])

            #qoe_worksheet.write(i, 1, qoe[i])
            #qoe_worksheet.write(i+1, idx+2, sum_ql_RR[i])
            #qoe_worksheet.write(i+1, idx+3, sum_ql_sq_RR[i])
            #qoe_worksheet.write(i+1, idx+4, len(requests_RR[i]))
            #qoe_worksheet.write(i+1, idx+5, cnt_stalls_RR[i])
            #qoe_worksheet.write(i+1, idx+6, t_dur_stalls_RR[i])
            #qoe_worksheet.write(i+1, idx+7, t_dur_stalls_RR[i]-dur_stalls_RR[i])

        qoe_worksheet.write(config.U[-1]+2, len(config.U)*0+idx+1, sum(i >= 3 for i in qoe_RR)/float(U))
        qoe_worksheet.write(config.U[-1]+3, len(config.U)*0+idx+1, sum(i >= 4 for i in qoe_RR)/float(U))
        qoe_worksheet.write(config.U[-1]+4, len(config.U)*0+idx+1, sum(i < 2 for i in qoe_RR)/float(U))

        """qoe_worksheet.write(config.U[-1]+2, len(config.U)*1+idx+1, sum(i >= 3 for i in qoe_BET)/float(U))
        qoe_worksheet.write(config.U[-1]+3, len(config.U)*1+idx+1, sum(i >= 4 for i in qoe_BET)/float(U))
        qoe_worksheet.write(config.U[-1]+4, len(config.U)*1+idx+1, sum(i < 2 for i in qoe_BET)/float(U))"""

        """qoe_worksheet.write(config.U[-1]+2, len(config.U)*2+idx+1, sum(i >= 3 for i in qoe_MT)/float(U))
        qoe_worksheet.write(config.U[-1]+3, len(config.U)*2+idx+1, sum(i >= 4 for i in qoe_MT)/float(U))
        qoe_worksheet.write(config.U[-1]+4, len(config.U)*2+idx+1, sum(i < 2 for i in qoe_MT)/float(U))

        qoe_worksheet.write(config.U[-1]+2, len(config.U)*3+idx+1, sum(i >= 3 for i in qoe_PF)/float(U))
        qoe_worksheet.write(config.U[-1]+3, len(config.U)*3+idx+1, sum(i >= 4 for i in qoe_PF)/float(U))
        qoe_worksheet.write(config.U[-1]+4, len(config.U)*3+idx+1, sum(i < 2 for i in qoe_PF)/float(U))"""


    qoe_workbook.close()

    t_final = datetime.datetime.now()
    print(t_final)
    print(t_final-t_init)

if REPORT:
    # Store requests parameters
    header = ['request_time', 'bitrate', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 't10', 't11', 't12', 't13', 't14', 't15', 't16', 't17', 't18', 't19', 't20', 't21', 't22', 't23', 'reply_time', 'estimated_throughput']
    
    for idx1, i in enumerate(requests_RR):
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

                    if idx3 == 5 and idx2 == 5:
                        request_worksheet.write(idx2+0, idx3+(config.Nx*config.Ny)-2, k)
                        request_worksheet.write(idx2-1, idx3+(config.Nx*config.Ny)-2, k)
                        request_worksheet.write(idx2-2, idx3+(config.Nx*config.Ny)-2, k)
                        request_worksheet.write(idx2-3, idx3+(config.Nx*config.Ny)-2, k)
                        request_worksheet.write(idx2-4, idx3+(config.Nx*config.Ny)-2, k)

    buffer_workbook.close()
    allocation_workbook.close()
    request_workbook.close()