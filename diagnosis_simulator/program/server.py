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
import math

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
        avg_throughput = float(rx_bits*10**6+int(round(RB*1000*config.G*12*14*(2**config.mu)*config.eff_CQI[CQI_idx-1]*0.83))*10**-3)/float(t+1)
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
        achieved_throughput = 1*1000*config.G*12*14*(2**config.mu)*config.eff_CQI[CQI_idx-1]*0.72
        #avg_throughput = (rx_bits*10**6)/float(t+1) + RB*1000*config.G*12*14*(2**config.mu)*config.eff_CQI[CQI_idx-1]*0.72
        avg_throughput = float(rx_bits*10**6+int(round(RB*1000*config.G*12*14*(2**config.mu)*config.eff_CQI[CQI_idx-1]*0.83))*10**-3)/float(t+1)
        m = (achieved_throughput ** alpha)/((avg_throughput+1) ** beta)

    else:
        m = -1

    return m


# Computes the user's metric (Scheduler: Round Robin)
def compute_metric_newRR(request, last_reply, t):
    if request[-1]['reply_bits'] > 0:
        m = t - last_reply

    else:
        m = -1

    return m


# Computes the user's metric (Scheduler: Blind Equal Throughput)
def compute_metric_newBET(request, rx_bits, t_rx_bits, buffer):
    if request[-1]['reply_bits'] > 0:
        avg_throughput = buffer*(rx_bits*10**6)*1000.0/float(t_rx_bits)

        if np.isnan(avg_throughput):
            avg_throughput = 0.0

        try:
            m = 1.0/avg_throughput

        except:
            m = float('inf')

    else:
        m = -1

    return m


# Computes the user's metric (Scheduler: Blind Equal Throughput)
def compute_metric_newMT(request, CQI_idx):
    if request[-1]['reply_bits'] > 0:
        achieved_throughput = 1*1000*config.G*12*14*(2**config.mu)*config.eff_CQI[CQI_idx-1]*0.83

        m = achieved_throughput

    else:
        m = -1

    return m


# Computes the user's metric (Scheduler: Blind Equal Throughput)
def compute_metric_newPF(request, rx_bits, t_rx_bits, CQI_idx, exp):
    # Fairness parameters
    # BET: alpha=0; beta=1
    # MT:  alpha=1; beta=0
    # PF:  alpha=1; beta=1

    if request[-1]['reply_bits'] > 0:
        achieved_throughput = (1*1000*config.G*12*14*(2**config.mu)*config.eff_CQI[CQI_idx-1]*0.83)**exp
        avg_throughput = ((rx_bits*10**6)*1000.0/float(t_rx_bits))**(1-exp)

        if np.isnan(avg_throughput):
            avg_throughput = 0.0

        try:
            m = achieved_throughput/avg_throughput

        except:
            m = float('inf')

    else:
        m = -1

    return m


# Computes the user's metric (Scheduler: Blind Equal Throughput)
def compute_metric_newAlgorithm(request, rx_bits, t_rx_bits, CQI_idx, U, rho):
    # Fairness parameters
    # BET: alpha=0; beta=1
    # MT:  alpha=1; beta=0
    # PF:  alpha=1; beta=1

    if request[-1]['reply_bits'] > 0:
        exp = min(1, max(0, float(U-config.gamma)/rho))

        achieved_throughput = (1*1000*config.G*12*14*(2**config.mu)*config.eff_CQI[CQI_idx-1]*0.83)**exp
        avg_throughput = ((rx_bits*10**6)*1000.0/float(t_rx_bits))**(1-exp)

        if np.isnan(avg_throughput):
            avg_throughput = 0.0

        try:
            m = achieved_throughput/avg_throughput

        except:
            m = float('inf')

    else:
        m = -1

    return m


# Computes the user's metric (Scheduler: Blind Equal Throughput)
def compute_metric_FRED(request, CQI_idx, buffer, level, t):
    # Fairness parameters
    # BET: alpha=0; beta=1
    # MT:  alpha=1; beta=0
    # PF:  alpha=1; beta=1

    if request[-1]['reply_bits'] > 0:
        achieved_throughput = config.K*1000*config.G*12*14*(2**config.mu)*config.eff_CQI[CQI_idx-1]*0.83
        nominator = (achieved_throughput/request[-1]['bitrate']) - 1
        denominator = buffer*10**-3

        try:
            m = nominator/denominator
            #print t, "a", m

            if buffer < level and t > 5*10**3:
                m = 1000.0/buffer
                #print t, "b", m

        except:
            m = float('inf')

    else:
        m = -1

    return m


# Computes the user's metric (Scheduler: Blind Equal Throughput)
def compute_metric_newAlgorithm2(request, rx_bits, t_rx_bits, CQI_idx, buffer, level, t):
    # Fairness parameters
    # BET: alpha=0; beta=1
    # MT:  alpha=1; beta=0
    # PF:  alpha=1; beta=1

    if request[-1]['reply_bits'] > 0:
        achieved_throughput = 1*1000*config.G*12*14*(2**config.mu)*config.eff_CQI[CQI_idx-1]*0.83
        avg_throughput = (rx_bits*10**6)*1000.0/float(t_rx_bits)

        if np.isnan(avg_throughput):
            avg_throughput = 0.0

        try:
            m = achieved_throughput/avg_throughput
            #print t, "a", m

            if buffer < level and t > 5*10**3:
                m = 1.0/(buffer*10**6)
                #print t, "b", m

        except:
            m = float('inf')

    else:
        m = -1

    return m


# Allocates 1 RB according to metric results
def newAllocation(requests, CQI_idx, metrics, RB_allocations, total_RB_allocations, last_reply, Nactive_users, t):
    RB = 0
    bits = 0.0
    total = config.K
    
    maximum = np.max(metrics)

    if maximum != -1:
        idx = np.where(metrics == maximum)
        if t < 0*10**3:
            RB_allocations[idx[0][0]] += math.ceil(Nactive_users*config.K/config.U)
            total_RB_allocations[idx[0][0]] += math.ceil(Nactive_users*config.K/config.U)
            last_reply[idx[0][0]] = float(t)

        else:
            for i in range(len(idx[0])):
                bits = requests[idx[0][i]][-1]['reply_bits']
                U = 1*1000*config.G*12*14*(2**config.mu)*config.eff_CQI[CQI_idx[idx[0][i]]-1]*0.83
                RB = math.ceil(bits*1000.0/U)

                if total - RB < 0:
                    RB_allocations[idx[0][i]] += total
                    total_RB_allocations[idx[0][i]] += total
                    last_reply[idx[0][i]] = float(t)
                    break

                else:
                    total -= RB
                    RB_allocations[idx[0][i]] += RB
                    total_RB_allocations[idx[0][i]] += RB
                    last_reply[idx[0][i]] = float(t)

    return last_reply, RB_allocations, total_RB_allocations


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

        RB_allocations[idx] += config.K
        total_RB_allocations[idx] += config.K
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