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
#      Main Program     #
#                       #
#########################
t_init = datetime.datetime.now()
print(t_init)

# Open salient 360 dataset
salient360_dataset = client.open_file()

for sim in range(config.Sim):
    # Open excel workbook to store outputs
    qoe_workbook = xlsxwriter.Workbook('../results/qoe_1stTry_PC'+str(sim+1)+'.xlsx')
    qoe_worksheet = qoe_workbook.add_worksheet('Sim'+str(sim+1))

    for i in range(config.U[-1]):
        qoe_worksheet.write(i+1, 0, 'User'+str(i+1))

    qoe_worksheet.write(config.U[-1]+1, 0, "#Users")
    qoe_worksheet.write(config.U[-1]+2, 0, "QoE>=3")
    qoe_worksheet.write(config.U[-1]+3, 0, "QoE>=4")
    qoe_worksheet.write(config.U[-1]+4, 0, "QoE<2")

    for i in range(len(config.U)):
        qoe_worksheet.write(config.U[-1]+1, len(config.U)*0+i+1, config.U[i])
        qoe_worksheet.write(0, len(config.U)*0+i+1, '#1')
        qoe_worksheet.write(config.U[-1]+1, len(config.U)*1+i+1, config.U[i])
        qoe_worksheet.write(0, len(config.U)*1+i+1, '#2')
        qoe_worksheet.write(config.U[-1]+1, len(config.U)*2+i+1, config.U[i])
        qoe_worksheet.write(0, len(config.U)*2+i+1, '#3')
        qoe_worksheet.write(config.U[-1]+1, len(config.U)*3+i+1, config.U[i])
        qoe_worksheet.write(0, len(config.U)*3+i+1, '#4')

    for idx, U in enumerate(config.U):
        for idx_rand, i in enumerate(range(U)):
            random.seed((sim+1)*10**6+U*10**3+(i+1))
            #random.seed((sim+1)*10**3+(i+1))
            print idx_rand+1, "HMD", random.randint(0, 56), "CQI", random.randint(1, 200)

        #########################
        #                       #
        # Progamming Variables  #
        #   (Initialization)    #
        #                       #
        #########################

        t = 0
        reported_CQI = np.zeros(U, dtype=int)
        user_CQI = np.zeros(U, dtype=int)
        init_list = random.sample(range(1, 1000), U)
        init_list = sorted(init_list)

        print init_list

        # RR parameters
        buffer_RR = np.zeros(U, dtype=float)
        delta_buffer_RR = np.zeros(U, dtype=float)
        rx_bits_RR = np.zeros(U, dtype=float)
        t_rx_bits_RR = np.zeros(U, dtype=int)
        throughput_RR = np.zeros(U, dtype=int)
        play_RR = np.zeros(U, dtype=int)
        RB_allocations_RR = np.zeros(U, dtype=int)
        total_RB_allocations_RR = np.zeros(U, dtype=int)
        metric_RR = np.zeros(U, dtype=float)
        last_reply_RR = np.zeros(U, dtype=float)
        requests_RR = [[] for i in range(U)]
        flg_firstU_RR = [True for i in range(U)]
        Nactive_users_RR = 0
        avgBuffer_RR = np.zeros(U, dtype=float)
        cntBuffer_RR = np.zeros(U, dtype=float)

        # BET parameters
        buffer_BET = np.zeros(U, dtype=float)
        delta_buffer_BET = np.zeros(U, dtype=float)
        rx_bits_BET = np.zeros(U, dtype=float)
        t_rx_bits_BET = np.zeros(U, dtype=int)
        throughput_BET = np.zeros(U, dtype=int)
        play_BET = np.zeros(U, dtype=int)
        RB_allocations_BET = np.zeros(U, dtype=int)
        total_RB_allocations_BET = np.zeros(U, dtype=int)
        metric_BET = np.zeros(U, dtype=float)
        last_reply_BET = np.zeros(U, dtype=float)
        requests_BET = [[] for i in range(U)]
        flg_firstU_BET = [True for i in range(U)]
        Nactive_users_BET = 0
        avgBuffer_BET = np.zeros(U, dtype=float)
        cntBuffer_BET = np.zeros(U, dtype=float)

        # MT parameters
        buffer_MT = np.zeros(U, dtype=float)
        delta_buffer_MT = np.zeros(U, dtype=float)
        rx_bits_MT = np.zeros(U, dtype=float)
        t_rx_bits_MT = np.zeros(U, dtype=int)
        throughput_MT = np.zeros(U, dtype=int)
        play_MT = np.zeros(U, dtype=int)
        RB_allocations_MT = np.zeros(U, dtype=int)
        total_RB_allocations_MT = np.zeros(U, dtype=int)
        metric_MT = np.zeros(U, dtype=float)
        last_reply_MT = np.zeros(U, dtype=float)
        requests_MT = [[] for i in range(U)]
        flg_firstU_MT = [True for i in range(U)]
        Nactive_users_MT = 0
        avgBuffer_MT = np.zeros(U, dtype=float)
        cntBuffer_MT = np.zeros(U, dtype=float)

        # PF parameters
        buffer_PF = np.zeros(U, dtype=float)
        delta_buffer_PF = np.zeros(U, dtype=float)
        rx_bits_PF = np.zeros(U, dtype=float)
        t_rx_bits_PF = np.zeros(U, dtype=int)
        throughput_PF = np.zeros(U, dtype=int)
        play_PF = np.zeros(U, dtype=int)
        RB_allocations_PF = np.zeros(U, dtype=int)
        total_RB_allocations_PF = np.zeros(U, dtype=int)
        metric_PF = np.zeros(U, dtype=float)
        last_reply_PF = np.zeros(U, dtype=float)
        requests_PF = [[] for i in range(U)]
        flg_firstU_PF = [True for i in range(U)]
        Nactive_users_PF = 0
        avgBuffer_PF = np.zeros(U, dtype=float)
        cntBuffer_PF = np.zeros(U, dtype=float)

        # QoE parameters
        # RR QoE parameters
        cnt_milisegments_RR = np.zeros(U, dtype=int)
        cnt_stalls_RR = np.zeros(U, dtype=int)
        perceived_stall_RR = np.negative(np.ones(U, dtype=int))
        dur_stalls_RR = np.zeros(U, dtype=int)
        t_dur_stalls_RR = np.zeros(U, dtype=int)
        flg_qoe_init_RR = [False for i in range(U)]
        flg_qoe_RR = [False for i in range(U)]
        flg_start_QoE_RR = [False for i in range(U)]
        avg_stall_RR = np.zeros(U, dtype=float)
        avg_quality_RR = np.zeros(U, dtype=float)
        sum_ql_RR = np.zeros(U, dtype=float)
        sum_ql_sq_RR = np.zeros(U, dtype=float)
        sig_quality_RR = np.zeros(U, dtype=float)
        qoe_RR = np.zeros(U, dtype=float)

        # BET QoE parameters
        cnt_milisegments_BET = np.zeros(U, dtype=int)
        cnt_stalls_BET = np.zeros(U, dtype=int)
        perceived_stall_BET = np.negative(np.ones(U, dtype=int))
        dur_stalls_BET = np.zeros(U, dtype=int)
        t_dur_stalls_BET = np.zeros(U, dtype=int)
        flg_qoe_init_BET = [False for i in range(U)]
        flg_qoe_BET = [False for i in range(U)]
        flg_start_QoE_BET = [False for i in range(U)]
        avg_stall_BET = np.zeros(U, dtype=float)
        avg_quality_BET = np.zeros(U, dtype=float)
        sum_ql_BET = np.zeros(U, dtype=float)
        sum_ql_sq_BET = np.zeros(U, dtype=float)
        sig_quality_BET = np.zeros(U, dtype=float)
        qoe_BET = np.zeros(U, dtype=float)

        # MT QoE parameters
        cnt_milisegments_MT = np.zeros(U, dtype=int)
        cnt_stalls_MT = np.zeros(U, dtype=int)
        perceived_stall_MT = np.negative(np.ones(U, dtype=int))
        dur_stalls_MT = np.zeros(U, dtype=int)
        t_dur_stalls_MT = np.zeros(U, dtype=int)
        flg_qoe_init_MT = [False for i in range(U)]
        flg_qoe_MT = [False for i in range(U)]
        flg_start_QoE_MT = [False for i in range(U)]
        avg_stall_MT = np.zeros(U, dtype=float)
        avg_quality_MT = np.zeros(U, dtype=float)
        sum_ql_MT = np.zeros(U, dtype=float)
        sum_ql_sq_MT = np.zeros(U, dtype=float)
        sig_quality_MT = np.zeros(U, dtype=float)
        qoe_MT = np.zeros(U, dtype=float)

        # PF QoE parameters
        cnt_milisegments_PF = np.zeros(U, dtype=int)
        cnt_stalls_PF = np.zeros(U, dtype=int)
        perceived_stall_PF = np.negative(np.ones(U, dtype=int))
        dur_stalls_PF = np.zeros(U, dtype=int)
        t_dur_stalls_PF = np.zeros(U, dtype=int)
        flg_qoe_init_PF = [False for i in range(U)]
        flg_qoe_PF = [False for i in range(U)]
        flg_start_QoE_PF = [False for i in range(U)]
        avg_stall_PF = np.zeros(U, dtype=float)
        avg_quality_PF = np.zeros(U, dtype=float)
        sum_ql_PF = np.zeros(U, dtype=float)
        sum_ql_sq_PF = np.zeros(U, dtype=float)
        sig_quality_PF = np.zeros(U, dtype=float)
        qoe_PF = np.zeros(U, dtype=float)

        for t in range(0, config.T+1, config.TTI):
            # CLIENT SIDE
            #print
            for i in range(U):
                # Get user's current CQI
                user_CQI[i] = client.get_CQI(i, t, sim, U)

                """if not t_rx_bits_RR[i] % config.theta and t > 1 and requests_RR[i][-1]['reply_bits']:
                    throughput_RR[i], flg_firstU_RR[i] = client.estimate_throughput(throughput_RR[i], K_bits_RR[i], t, buffer_RR[i], flg_firstU_RR[i])
                    K_bits_RR[i] = 0
                
                if not t_rx_bits_BET[i] % config.theta and t > 1 and requests_BET[i][-1]['reply_bits']:
                    throughput_BET[i], flg_firstU_BET[i] = client.estimate_throughput(throughput_BET[i], K_bits_BET[i], t, buffer_BET[i], flg_firstU_BET[i])
                    K_bits_BET[i] = 0
                
                if not t_rx_bits_MT[i] % config.theta and t > 1 and requests_MT[i][-1]['reply_bits']:
                    throughput_MT[i], flg_firstU_MT[i] = client.estimate_throughput(throughput_MT[i], K_bits_MT[i], t, buffer_MT[i], flg_firstU_MT[i])
                    K_bits_MT[i] = 0
                
                if not t_rx_bits_PF[i] % config.theta and t > 1 and requests_PF[i][-1]['reply_bits']:
                    throughput_PF[i], flg_firstU_PF[i] = client.estimate_throughput(throughput_PF[i], K_bits_PF[i], t, buffer_PF[i], flg_firstU_PF[i])
                    K_bits_PF[i] = 0"""
                
                # Update buffer
                # RR
                if RB_allocations_RR[i] != 0:
                    delta_buffer_RR[i], rx_bits_RR[i], requests_RR[i], Nactive_users_RR = client.buffer_update(user_CQI[i], requests_RR[i], Nactive_users_RR, RB_allocations_RR[i], rx_bits_RR[i], t)
                    buffer_RR[i] += delta_buffer_RR[i]

                    # Buffer max. capacity; Check if there is enough content for playback after buffering
                    if buffer_RR[i] >= config.init - config.epsilon:
                        #buffer_RR[i] = config.B
                        play_RR[i] = 1

                # BET
                if RB_allocations_BET[i] != 0:
                    delta_buffer_BET[i], rx_bits_BET[i], requests_BET[i], Nactive_users_BET = client.buffer_update(user_CQI[i], requests_BET[i], Nactive_users_BET, RB_allocations_BET[i], rx_bits_BET[i], t)
                    buffer_BET[i] += delta_buffer_BET[i]

                    # Buffer max. capacity; Check if there is enough content for playback after buffering
                    if buffer_BET[i] >= config.init - config.epsilon:
                        #buffer_BET[i] = config.B
                        play_BET[i] = 1

                # MT
                if RB_allocations_MT[i] != 0:
                    delta_buffer_MT[i], rx_bits_MT[i], requests_MT[i], Nactive_users_MT = client.buffer_update(user_CQI[i], requests_MT[i], Nactive_users_MT, RB_allocations_MT[i], rx_bits_MT[i], t)
                    buffer_MT[i] += delta_buffer_MT[i]
                    
                    # Buffer max. capacity; Check if there is enough content for playback after buffering
                    if buffer_MT[i] >= config.init - config.epsilon:
                        #buffer_MT[i] = config.B
                        play_MT[i] = 1

                # PF
                if RB_allocations_PF[i] != 0:
                    delta_buffer_PF[i], rx_bits_PF[i], requests_PF[i], Nactive_users_PF = client.buffer_update(user_CQI[i], requests_PF[i], Nactive_users_PF, RB_allocations_PF[i], rx_bits_PF[i], t)
                    buffer_PF[i] += delta_buffer_PF[i]

                    # Buffer max. capacity; Check if there is enough content for playback after buffering
                    if buffer_PF[i] >= config.init - config.epsilon:
                        #buffer_PF[i] = config.B
                        play_PF[i] = 1

                # Buffering event
                # RR
                if play_RR[i] == 0:
                    if t >= init_list[i]:
                        if not requests_RR[i] or (requests_RR[i] and requests_RR[i][-1]['reply_bits'] == 0):
                            # Initial buffering - Request every tile with the lowest quality or if there is space - Request every tile with the lowest quality
                            requests_RR[i] = client.request_LQ(requests_RR[i], t)
                            #requests_RR[i] = client.request_LQ_QAAD(requests_RR[i], t)
                            Nactive_users_RR += 1
                        
                        else:
                            t_rx_bits_RR[i] += 1

                # Normal video playback
                else:
                    # There is space for a new segment and every request has been completly replied
                    if requests_RR[i][-1]['reply_bits'] == 0:
                        if config.B - buffer_RR[i] >= config.S:
                            # Request segment with rate adaptation (RA)
                            #requests_RR[i] = client.request_RA_BFA(requests_RR[i], t, t_dur_stalls_RR[i]+init_list[i], client.throughput_estimation(requests_RR[i]), salient360_dataset, i, sim, U)
                            #requests_RR[i] = client.request_RA_BQA1(requests_RR[i], t, t_dur_stalls_RR[i]+init_list[i], client.throughput_estimation(requests_RR[i]), salient360_dataset, i, buffer_RR[i], sim, U, 1.6*10**3)
                            requests_RR[i] = client.request_RA_BQA2(requests_RR[i], t, t_dur_stalls_RR[i]+init_list[i], client.throughput_estimation(requests_RR[i], init_list[i]), salient360_dataset, i, buffer_RR[i], sim, U, 1.8*10**3, 1.8*10**3)
                            #requests_RR[i] = client.request_RA_QAAD(requests_RR[i], t, t_dur_stalls_RR[i]+init_list[i], client.throughput_estimation(requests_RR[i]), salient360_dataset, i, buffer_RR[i], sim, U, 0.5*10**3, 1.9*10**3)
                            Nactive_users_RR += 1
                    
                    else:
                        t_rx_bits_RR[i] += 1

                    # Client watches TTI seconds of video
                    buffer_RR[i] -= config.TTI

                    # Client suffers a stall event
                    if buffer_RR[i] <= 0:
                        buffer_RR[i] = 0
                        play_RR[i] = 0

                # BET
                if play_BET[i] == 0:
                    if t >= init_list[i]:
                        if not requests_BET[i] or (requests_BET[i] and requests_BET[i][-1]['reply_bits'] == 0):
                            # Initial buffering - Request every tile with the lowest quality or if there is space - Request every tile with the lowest quality
                            requests_BET[i] = client.request_LQ(requests_BET[i], t)
                            #requests_BET[i] = client.request_LQ_QAAD(requests_BET[i], t)
                            Nactive_users_BET += 1
                        
                        else:
                            t_rx_bits_BET[i] += 1

                # Normal video playback
                else:
                    # There is space for a new segment and every request has been completly replied
                    if requests_BET[i][-1]['reply_bits'] == 0:
                        if config.B - buffer_BET[i] >= config.S:
                            # Request segment with rate adaptation (RA)
                            #requests_BET[i] = client.request_RA_BFA(requests_BET[i], t, t_dur_stalls_BET[i]+init_list[i], client.throughput_estimation(requests_BET[i]), salient360_dataset, i, sim, U)
                            #requests_BET[i] = client.request_RA_BQA1(requests_BET[i], t, t_dur_stalls_BET[i]+init_list[i], client.throughput_estimation(requests_BET[i]), salient360_dataset, i, buffer_BET[i], sim, U, 1.7*10**3)
                            requests_BET[i] = client.request_RA_BQA2(requests_BET[i], t, t_dur_stalls_BET[i]+init_list[i], client.throughput_estimation(requests_BET[i], init_list[i]), salient360_dataset, i, buffer_BET[i], sim, U, 1.8*10**3, 1.8*10**3)
                            #requests_BET[i] = client.request_RA_QAAD(requests_BET[i], t, t_dur_stalls_BET[i]+init_list[i], client.throughput_estimation(requests_BET[i]), salient360_dataset, i, buffer_BET[i], sim, U, 0.5*10**3, 1.9*10**3)
                            Nactive_users_BET += 1
                    
                    else:
                        t_rx_bits_BET[i] += 1

                    # Client watches TTI seconds of video
                    buffer_BET[i] -= config.TTI

                    # Client suffers a stall event
                    if buffer_BET[i] <= 0:
                        buffer_BET[i] = 0
                        play_BET[i] = 0

                # MT
                if play_MT[i] == 0:
                    if t >= init_list[i]:
                        if not requests_MT[i] or (requests_MT[i] and requests_MT[i][-1]['reply_bits'] == 0):
                            # Initial buffering - Request every tile with the lowest quality or if there is space - Request every tile with the lowest quality
                            requests_MT[i] = client.request_LQ(requests_MT[i], t)
                            #requests_MT[i] = client.request_LQ_QAAD(requests_MT[i], t)
                            Nactive_users_MT += 1
                        
                        else:
                            t_rx_bits_MT[i] += 1

                # Normal video playback
                else:
                    # There is space for a new segment and every request has been completly replied
                    if requests_MT[i][-1]['reply_bits'] == 0:
                        if config.B - buffer_MT[i] >= config.S:
                            # Request segment with rate adaptation (RA)
                            #requests_MT[i] = client.request_RA_BFA(requests_MT[i], t, t_dur_stalls_MT[i]+init_list[i], client.throughput_estimation(requests_MT[i]), salient360_dataset, i, sim, U)
                            #requests_MT[i] = client.request_RA_BQA1(requests_MT[i], t, t_dur_stalls_MT[i]+init_list[i], client.throughput_estimation(requests_MT[i]), salient360_dataset, i, buffer_MT[i], sim, U, 1.8*10**3)
                            requests_MT[i] = client.request_RA_BQA2(requests_MT[i], t, t_dur_stalls_MT[i]+init_list[i], client.throughput_estimation(requests_MT[i], init_list[i]), salient360_dataset, i, buffer_MT[i], sim, U, 1.8*10**3, 1.8*10**3)
                            #requests_MT[i] = client.request_RA_QAAD(requests_MT[i], t, t_dur_stalls_MT[i]+init_list[i], client.throughput_estimation(requests_MT[i]), salient360_dataset, i, buffer_MT[i], sim, U, 0.5*10**3, 1.9*10**3)
                            Nactive_users_MT += 1
                    
                    else:
                        t_rx_bits_MT[i] += 1

                    # Client watches TTI seconds of video
                    buffer_MT[i] -= config.TTI

                    # Client suffers a stall event
                    if buffer_MT[i] <= 0:
                        buffer_MT[i] = 0
                        play_MT[i] = 0

                # PF
                if play_PF[i] == 0:
                    if t >= init_list[i]:
                        if not requests_PF[i] or (requests_PF[i] and requests_PF[i][-1]['reply_bits'] == 0):
                            # Initial buffering - Request every tile with the lowest quality or if there is space - Request every tile with the lowest quality
                            requests_PF[i] = client.request_LQ(requests_PF[i], t)
                            #requests_PF[i] = client.request_LQ_QAAD(requests_PF[i], t)
                            Nactive_users_PF += 1
                        
                        else:
                            t_rx_bits_PF[i] += 1

                # Normal video playback
                else:
                    # There is space for a new segment and every request has been completly replied
                    if requests_PF[i][-1]['reply_bits'] == 0:
                        if config.B - buffer_PF[i] >= config.S:
                            # Request segment with rate adaptation (RA)
                            #requests_PF[i] = client.request_RA_BFA(requests_PF[i], t, t_dur_stalls_PF[i]+init_list[i], client.throughput_estimation(requests_PF[i]), salient360_dataset, i, sim, U)
                            #requests_PF[i] = client.request_RA_BQA1(requests_PF[i], t, t_dur_stalls_PF[i]+init_list[i], client.throughput_estimation(requests_PF[i]), salient360_dataset, i, buffer_PF[i], sim, U, 1.9*10**3)
                            requests_PF[i] = client.request_RA_BQA2(requests_PF[i], t, t_dur_stalls_PF[i]+init_list[i], client.throughput_estimation(requests_PF[i], init_list[i]), salient360_dataset, i, buffer_PF[i], sim, U, 1.8*10**3, 1.8*10**3)
                            #requests_PF[i] = client.request_RA_QAAD(requests_PF[i], t, t_dur_stalls_PF[i]+init_list[i], client.throughput_estimation(requests_PF[i]), salient360_dataset, i, buffer_PF[i], sim, U, 1.5*10**3, 1.0*10**3)
                            Nactive_users_PF += 1
                    
                    else:
                        t_rx_bits_PF[i] += 1

                    # Client watches TTI seconds of video
                    buffer_PF[i] -= config.TTI

                    # Client suffers a stall event
                    if buffer_PF[i] <= 0:
                        buffer_PF[i] = 0
                        play_PF[i] = 0

                # Update QoE inputs
                if t >= init_list[i]:
                    cnt_milisegments_RR[i], cnt_stalls_RR[i], perceived_stall_RR[i], dur_stalls_RR[i], t_dur_stalls_RR[i], sum_ql_RR[i], sum_ql_sq_RR[i], flg_qoe_RR[i], flg_qoe_init_RR[i], flg_start_QoE_RR[i]  = qoe_model.update_QoE(cnt_milisegments_RR[i], cnt_stalls_RR[i], perceived_stall_RR[i], dur_stalls_RR[i], t_dur_stalls_RR[i], sum_ql_RR[i], sum_ql_sq_RR[i], play_RR[i], flg_qoe_RR[i], flg_qoe_init_RR[i], flg_start_QoE_RR[i], init_list[i], requests_RR[i], salient360_dataset, i, t, sim, U)
                    cnt_milisegments_BET[i], cnt_stalls_BET[i], perceived_stall_BET[i], dur_stalls_BET[i], t_dur_stalls_BET[i], sum_ql_BET[i], sum_ql_sq_BET[i], flg_qoe_BET[i], flg_qoe_init_BET[i], flg_start_QoE_BET[i]  = qoe_model.update_QoE(cnt_milisegments_BET[i], cnt_stalls_BET[i], perceived_stall_BET[i], dur_stalls_BET[i], t_dur_stalls_BET[i], sum_ql_BET[i], sum_ql_sq_BET[i], play_BET[i], flg_qoe_BET[i], flg_qoe_init_BET[i], flg_start_QoE_BET[i], init_list[i], requests_BET[i], salient360_dataset, i, t, sim, U)
                    cnt_milisegments_MT[i], cnt_stalls_MT[i], perceived_stall_MT[i], dur_stalls_MT[i], t_dur_stalls_MT[i], sum_ql_MT[i], sum_ql_sq_MT[i], flg_qoe_MT[i], flg_qoe_init_MT[i], flg_start_QoE_MT[i]  = qoe_model.update_QoE(cnt_milisegments_MT[i], cnt_stalls_MT[i], perceived_stall_MT[i], dur_stalls_MT[i], t_dur_stalls_MT[i], sum_ql_MT[i], sum_ql_sq_MT[i], play_MT[i], flg_qoe_MT[i], flg_qoe_init_MT[i], flg_start_QoE_MT[i], init_list[i], requests_MT[i], salient360_dataset, i, t, sim, U)
                    cnt_milisegments_PF[i], cnt_stalls_PF[i], perceived_stall_PF[i], dur_stalls_PF[i], t_dur_stalls_PF[i], sum_ql_PF[i], sum_ql_sq_PF[i], flg_qoe_PF[i], flg_qoe_init_PF[i], flg_start_QoE_PF[i]  = qoe_model.update_QoE(cnt_milisegments_PF[i], cnt_stalls_PF[i], perceived_stall_PF[i], dur_stalls_PF[i], t_dur_stalls_PF[i], sum_ql_PF[i], sum_ql_sq_PF[i], play_PF[i], flg_qoe_PF[i], flg_qoe_init_PF[i], flg_start_QoE_PF[i], init_list[i], requests_PF[i], salient360_dataset, i, t, sim, U)

                # Report CQI
                if not t % 5:
                    reported_CQI[i] = user_CQI[i]

            # SERVER SIDE
            RB_allocations_RR = np.zeros(U, dtype=int)
            RB_allocations_BET = np.zeros(U, dtype=int)
            RB_allocations_MT = np.zeros(U, dtype=int)
            RB_allocations_PF = np.zeros(U, dtype=int)

            # Allocate each Kth RB
            metric_RR = np.negative(np.ones(U, dtype=float))
            metric_BET = np.negative(np.ones(U, dtype=float))
            metric_MT = np.negative(np.ones(U, dtype=float))
            metric_PF = np.negative(np.ones(U, dtype=float))

            for i in range(U):
                if t >= init_list[i]:

                    avgBuffer_RR[i], cntBuffer_RR[i] = client.average(avgBuffer_RR[i], cntBuffer_RR[i], buffer_RR[i])
                    avgBuffer_BET[i], cntBuffer_BET[i] = client.average(avgBuffer_BET[i], cntBuffer_BET[i], buffer_BET[i])
                    avgBuffer_MT[i], cntBuffer_MT[i] = client.average(avgBuffer_MT[i], cntBuffer_MT[i], buffer_MT[i])
                    avgBuffer_PF[i], cntBuffer_PF[i] = client.average(avgBuffer_PF[i], cntBuffer_PF[i], buffer_PF[i])

                    """metric_RR[i] = server.compute_metric_newPF(requests_RR[i], rx_bits_RR[i], t_rx_bits_RR[i], reported_CQI[i])
                    metric_BET[i] = server.compute_metric_newPF(requests_BET[i], rx_bits_BET[i], t_rx_bits_BET[i], reported_CQI[i])
                    metric_MT[i] = server.compute_metric_newPF(requests_MT[i], rx_bits_MT[i], t_rx_bits_MT[i], reported_CQI[i])
                    metric_PF[i] = server.compute_metric_newPF(requests_PF[i], rx_bits_PF[i], t_rx_bits_PF[i], reported_CQI[i])"""

                    """metric_RR[i] = server.compute_metric_newRR(requests_RR[i], last_reply_RR[i], t)
                    metric_BET[i] = server.compute_metric_newBET(requests_BET[i], rx_bits_BET[i], t_rx_bits_BET[i])
                    metric_MT[i] = server.compute_metric_newMT(requests_MT[i], reported_CQI[i])
                    metric_PF[i] = server.compute_metric_newPF(requests_PF[i], rx_bits_PF[i], t_rx_bits_PF[i], reported_CQI[i], 0, 1)"""

                    metric_RR[i] = server.compute_metric_newAlgorithm2(requests_RR[i], rx_bits_RR[i], t_rx_bits_RR[i], buffer_RR[i])
                    metric_BET[i] = server.compute_metric_newAlgorithm3(requests_BET[i], reported_CQI[i], avg_quality_BET[i])
                    metric_MT[i] = server.compute_metric_newAlgorithm4(requests_MT[i], rx_bits_MT[i], t_rx_bits_MT[i], reported_CQI[i], buffer_MT[i], avgBuffer_MT[i])
                    metric_PF[i] = server.compute_metric_newAlgorithm5(requests_PF[i], buffer_PF[i], avgBuffer_PF[i])

                    """metric_RR[i] = server.compute_metric_newBET(requests_RR[i], rx_bits_RR[i], t_rx_bits_RR[i])
                    metric_BET[i] = server.compute_metric_newAlgorithm(requests_BET[i], rx_bits_BET[i], t_rx_bits_BET[i], reported_CQI[i], U, 10)
                    metric_MT[i] = server.compute_metric_newAlgorithm(requests_MT[i], rx_bits_MT[i], t_rx_bits_MT[i], reported_CQI[i], U, 5)
                    metric_PF[i] = server.compute_metric_newMT(requests_PF[i], reported_CQI[i])"""

                    """metric_RR[i] = server.compute_metric_FRED(requests_RR[i], reported_CQI[i], buffer_RR[i], 0.5*10**3, t)
                    metric_BET[i] = server.compute_metric_FRED(requests_BET[i], reported_CQI[i], buffer_BET[i], 0, t)
                    metric_MT[i] = server.compute_metric_newAlgorithm2(requests_MT[i], rx_bits_MT[i], t_rx_bits_MT[i], reported_CQI[i], buffer_MT[i], 0.5*10**3, t)
                    metric_PF[i] = server.compute_metric_newAlgorithm2(requests_PF[i], rx_bits_PF[i], t_rx_bits_PF[i], reported_CQI[i], buffer_PF[i], 0, t)"""


            
            last_reply_RR, RB_allocations_RR, total_RB_allocations_RR = server.newAllocation(requests_RR, reported_CQI, metric_RR, RB_allocations_RR, total_RB_allocations_RR, last_reply_RR, Nactive_users_RR, U, t)
            last_reply_BET, RB_allocations_BET, total_RB_allocations_BET = server.newAllocation(requests_BET, reported_CQI, metric_BET, RB_allocations_BET, total_RB_allocations_BET, last_reply_BET, Nactive_users_BET, U, t)
            last_reply_MT, RB_allocations_MT, total_RB_allocations_MT = server.newAllocation(requests_MT, reported_CQI, metric_MT, RB_allocations_MT, total_RB_allocations_MT, last_reply_MT, Nactive_users_MT, U, t)
            last_reply_PF, RB_allocations_PF, total_RB_allocations_PF = server.newAllocation(requests_PF, reported_CQI, metric_PF, RB_allocations_PF, total_RB_allocations_PF, last_reply_PF, Nactive_users_PF, U, t)

            """for k in range(config.K):
                # Initialize metrics/RB_allocations arrays
                metric_RR = np.negative(np.ones(U, dtype=float))
                metric_BET = np.negative(np.ones(U, dtype=float))
                metric_MT = np.negative(np.ones(U, dtype=float))
                metric_PF = np.negative(np.ones(U, dtype=float))
                
                # Compute each user metric
                for i in range(U):
                    metric_RR[i] = server.compute_metric_RR(requests_RR[i], last_reply_RR[i], t)
                    metric_BET[i] = server.compute_metric_RR(requests_BET[i], last_reply_BET[i], t)
                    metric_MT[i] = server.compute_metric_RR(requests_MT[i], last_reply_MT[i], t)
                    metric_PF[i] = server.compute_metric_RR(requests_PF[i], last_reply_PF[i], t)

                    metric_RR[i] = server.compute_metric_PF(requests_RR[i], rx_bits_RR[i], t, reported_CQI[i], RB_allocations_RR[i], 1, 1)
                    metric_BET[i] = server.compute_metric_PF(requests_BET[i], rx_bits_BET[i], t, reported_CQI[i], RB_allocations_BET[i], 1, 1)
                    metric_MT[i] = server.compute_metric_PF(requests_MT[i], rx_bits_MT[i], t, reported_CQI[i], RB_allocations_MT[i], 1, 1)
                    metric_PF[i] = server.compute_metric_PF(requests_PF[i], rx_bits_PF[i], t, reported_CQI[i], RB_allocations_PF[i], 1, 1)

                    metric_RR[i] = server.compute_metric_RR(requests_RR[i], last_reply_RR[i], t)
                    metric_BET[i] = server.compute_metric_BET(requests_BET[i], rx_bits_BET[i], t_rx_bits_BET[i], reported_CQI[i], RB_allocations_BET[i])
                    metric_MT[i] = server.compute_metric_PF(requests_MT[i], rx_bits_MT[i], t, reported_CQI[i], RB_allocations_MT[i], 1, 0)
                    metric_PF[i] = server.compute_metric_PF(requests_PF[i], rx_bits_PF[i], t, reported_CQI[i], RB_allocations_PF[i], 1, 1)
            
                # Allocate 1 RB to 1 user
                last_reply_RR, RB_allocations_RR, total_RB_allocations_RR = server.allocation(metric_RR, RB_allocations_RR, total_RB_allocations_RR, last_reply_RR, float(t) + float(k)/1000.0)
                last_reply_BET, RB_allocations_BET, total_RB_allocations_BET = server.allocation(metric_BET, RB_allocations_BET, total_RB_allocations_BET, last_reply_BET, float(t) + float(k)/1000.0)
                last_reply_MT, RB_allocations_MT, total_RB_allocations_MT = server.allocation(metric_MT, RB_allocations_MT, total_RB_allocations_MT, last_reply_MT, float(t) + float(k)/1000.0)
                last_reply_PF, RB_allocations_PF, total_RB_allocations_PF = server.allocation(metric_PF, RB_allocations_PF, total_RB_allocations_PF, last_reply_PF, float(t) + float(k)/1000.0)"""

            # Update running status
            if not t % 2500:
                print "Progress (", str(U), "):", float(t/1000.0), "\t", "[seconds of video]"

        # Compute and store QoE values
        print total_RB_allocations_BET
        for i in range(U):
            print "#1"
            qoe_RR[i] = qoe_model.compute_QoE(i, cnt_milisegments_RR[i], cnt_stalls_RR[i], sum_ql_RR[i], sum_ql_sq_RR[i], t_dur_stalls_RR[i])
            print "#2"
            qoe_BET[i] = qoe_model.compute_QoE(i, cnt_milisegments_BET[i], cnt_stalls_BET[i], sum_ql_BET[i], sum_ql_sq_BET[i], t_dur_stalls_BET[i])
            print "#3"
            qoe_MT[i] = qoe_model.compute_QoE(i, cnt_milisegments_MT[i], cnt_stalls_MT[i], sum_ql_MT[i], sum_ql_sq_MT[i], t_dur_stalls_MT[i])
            print "#4"
            qoe_PF[i] = qoe_model.compute_QoE(i, cnt_milisegments_PF[i], cnt_stalls_PF[i], sum_ql_PF[i], sum_ql_sq_PF[i], t_dur_stalls_PF[i])

            qoe_worksheet.write(i+1, len(config.U)*0+idx+1, qoe_RR[i])
            qoe_worksheet.write(i+1, len(config.U)*1+idx+1, qoe_BET[i])
            qoe_worksheet.write(i+1, len(config.U)*2+idx+1, qoe_MT[i])
            qoe_worksheet.write(i+1, len(config.U)*3+idx+1, qoe_PF[i])

            #qoe_worksheet.write(i, 1, qoe_RR[i])
            #qoe_worksheet.write(i, idx+2, sum_ql_RR[i])
            #qoe_worksheet.write(i, idx+3, sum_ql_sq_RR[i])
            #qoe_worksheet.write(i, idx+4, len(requests_RR[i]))
            #qoe_worksheet.write(i, idx+5, cnt_stalls_RR[i])
            #qoe_worksheet.write(i, idx+6, t_dur_stalls_RR[i])
            #qoe_worksheet.write(i, idx+7, t_dur_stalls_RR[i]-dur_stalls_RR[i])

        qoe_worksheet.write(config.U[-1]+2, len(config.U)*0+idx+1, sum(i >= 3 for i in qoe_RR)/float(U))
        qoe_worksheet.write(config.U[-1]+3, len(config.U)*0+idx+1, sum(i >= 4 for i in qoe_RR)/float(U))
        qoe_worksheet.write(config.U[-1]+4, len(config.U)*0+idx+1, sum(i < 2 for i in qoe_RR)/float(U))

        qoe_worksheet.write(config.U[-1]+2, len(config.U)*1+idx+1, sum(i >= 3 for i in qoe_BET)/float(U))
        qoe_worksheet.write(config.U[-1]+3, len(config.U)*1+idx+1, sum(i >= 4 for i in qoe_BET)/float(U))
        qoe_worksheet.write(config.U[-1]+4, len(config.U)*1+idx+1, sum(i < 2 for i in qoe_BET)/float(U))

        qoe_worksheet.write(config.U[-1]+2, len(config.U)*2+idx+1, sum(i >= 3 for i in qoe_MT)/float(U))
        qoe_worksheet.write(config.U[-1]+3, len(config.U)*2+idx+1, sum(i >= 4 for i in qoe_MT)/float(U))
        qoe_worksheet.write(config.U[-1]+4, len(config.U)*2+idx+1, sum(i < 2 for i in qoe_MT)/float(U))

        qoe_worksheet.write(config.U[-1]+2, len(config.U)*3+idx+1, sum(i >= 3 for i in qoe_PF)/float(U))
        qoe_worksheet.write(config.U[-1]+3, len(config.U)*3+idx+1, sum(i >= 4 for i in qoe_PF)/float(U))
        qoe_worksheet.write(config.U[-1]+4, len(config.U)*3+idx+1, sum(i < 2 for i in qoe_PF)/float(U))


    qoe_workbook.close()

    t_final = datetime.datetime.now()
    print(t_final)
    print(t_final-t_init)