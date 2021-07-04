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
import random
import numpy as np

#########################
#                       #
#       Functions       #
#                       #
#########################


# Computes the user's metric (Scheduler: Round Robin)
def compute_metric_RR(request, last_reply, t):
    if request[-1]['reply_bits'] > 0:
        m = t - last_reply

    else:
        m = -1

    return m


# Computes the user's metric (Scheduler: Blind Equal Throughput)
def compute_metric_BET(request, rx_bits, t, CQI_idx, RB):
    if request[-1]['reply_bits'] > 0:
        #avg_throughput = (rx_bits+(int(round(RB*1000*config.G*12*14*(2**config.mu)*config.eff_CQI[CQI_idx-1]*0.72))/(10**6))*10**-3)/(t+1)
        avg_throughput = (rx_bits*10**6+int(round(RB*1000*config.G*12*7*2*config.eff_CQI[CQI_idx-1]*0.75))*10**-3)/(t+1)
        #avg_throughput = rx_bits*10**6/(t+1) + int(round(RB*1000*config.G*12*7*2*config.eff_CQI[CQI_idx-1]*0.75))
        m = 1/(avg_throughput+1)

    else:
        m = -1

    return m


# Computes the user's metric (Scheduler: Blind Equal Throughput)
def compute_metric_PF(request, rx_bits, t, CQI_idx, RB, alpha, beta):
    # Fairness parameters
    # BET: alpha=0; beta=1
    # MT:  alpha=1; beta=0
    # PF:  alpha=1; beta=1

    if request[-1]['reply_bits'] > 0:
        achieved_throughput = int(round(1*1000*config.G*12*7*2*config.eff_CQI[CQI_idx-1]*0.75))
        avg_throughput = (rx_bits*10**6+int(round(RB*1000*config.G*12*7*2*config.eff_CQI[CQI_idx-1]*0.75))*10**-3)/(t+1)
        #avg_throughput = rx_bits*10**6/(t+1) + int(round(RB*1000*config.G*12*7*2*config.eff_CQI[CQI_idx-1]*0.75))
        m = (achieved_throughput ** alpha)/((avg_throughput+1) ** beta)

    else:
        m = -1

    return m


# Allocates 1 RB according to metric results
def allocation(metrics, RB_allocations, total_RB_allocations, last_reply, t):
    max_list = np.zeros(0)
    
    maximum = max(metrics)

    if maximum != -1:
        idx = np.where(metrics == maximum)
        #print t, last_reply, idx[0], '\n'
        if len(idx[0]) == 1:
            idx = idx[0][0]

        else:
            # Round-Robin when exists more than one maximum
            for i in idx[0]:
                max_list = np.append(max_list, t-last_reply[i])

            maximum = max(max_list)
            idx1 = np.where(max_list == maximum)
            idx = idx[0][random.choice(idx1[0])]

        RB_allocations[idx] += 1
        total_RB_allocations[idx] += 1
        last_reply[idx] = t

    return last_reply, RB_allocations, total_RB_allocations

# Allocates RBs uniformly according to the number of users with requests (RR)
def allocation_RR(requests, RB_allocations, total_RB_allocations, U):
    cnt_users = 0
    id_list = []

    for i in range(U):
        if requests[i][-1]['reply_bits'] >= 0:
            cnt_users += 1
            id_list.append(i)

    if cnt_users <= config.K:
        for i in id_list:
            RB_allocations[i] = int(config.K/cnt_users)
            total_RB_allocations[i] += int(config.K/cnt_users)

    else:
        lucky_user = random.choice(id_list)
        RB_allocations[lucky_user] = config.K
        total_RB_allocations[lucky_user] = config.K

    return RB_allocations, total_RB_allocations