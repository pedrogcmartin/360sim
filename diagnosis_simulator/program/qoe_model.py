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
import client
import math

q_max = len(config.q)

#########################
#                       #
#       Functions       #
#                       #
#########################

# Compute QoE Value
def compute_QoE(cnt_stalls, sum_ql, sum_ql_sq, t_dur_stalls):
    # If the video was not displayed
    if sum_ql == 0:
        return 0

    # If the video was displayed
    else:

        # compute stalls average duration
        try:
            avg_stall = (float(t_dur_stalls)/1000.0)/float(cnt_stalls)

        except ZeroDivisionError:
            avg_stall = float(t_dur_stalls)/1000.0

        # compute average VP quality
        avg_quality = sum_ql/(config.T-t_dur_stalls)

        # compute quality standard deviation
        sig_quality = math.sqrt(abs((sum_ql_sq-2*avg_quality*sum_ql+(config.T-t_dur_stalls)*avg_quality**2)/(config.T-t_dur_stalls)))

        try:
            qoe = max(5.67*(avg_quality/float(q_max))-6.72*(sig_quality/float(q_max))+0.17-4.95*((7.0/8.0)*max((math.log(float(cnt_stalls)/(float(config.T)/1000.0))/6)+1, 0)+(1.0/8.0)*min(avg_stall, 15)/15.0), 0)

        except (ValueError, ZeroDivisionError):
            qoe = max(5.67*(avg_quality/float(q_max))-6.72*(sig_quality/float(q_max))+0.17-4.95*(1.0/8.0)*min(avg_stall, 15)/15.0, 0)

        return qoe


# Update QoE value
def update_QoE(cnt_stalls, perceived_stall, dur_stalls, t_dur_stalls, sum_ql, sum_ql_sq, play, flg_qoe, flg_qoe_init, requests, dataset, U, t):
    if flg_qoe and play == 0:
        perceived_stall = 0
        flg_qoe = False

    elif not flg_qoe and play == 1:
        flg_qoe = flg_qoe_init = True

    if not flg_qoe_init:
        dur_stalls -= 1

    if play == 0:
        dur_stalls += 1
        t_dur_stalls += 1
        if perceived_stall != -1:
            perceived_stall += 1
            if perceived_stall >= 150:
                perceived_stall = -1
                cnt_stalls += 1

    # compute quality statistics
    else:
        # get current viewport quality
        vp_tiles = get_vp_tiles(client.get_longitude(dataset, U, t))
        ql = get_vp_quality(requests, vp_tiles, t, t_dur_stalls)
        sum_ql += ql
        sum_ql_sq += ql**2

    return cnt_stalls, perceived_stall, dur_stalls, t_dur_stalls, sum_ql, sum_ql_sq, flg_qoe, flg_qoe_init


# Get viewport tiles
def get_vp_tiles(teta_o):
    if teta_o < 0:
        teta_o += 360

    elif teta_o >= 360:
        teta_o -= 360

    teta_VP = 110

    tiles_longs = [0, 60, 120, 180, 240, 300, 360]

    tiles_attributions1 = [[11, 17, 6, 12], [6, 12, 7, 13], [7, 13, 8, 14], [8, 14, 9, 15], [9, 15, 10, 16], [10, 16, 11, 17], [11, 17, 6, 12]]
    tiles_attributions2 = [[10, 16, 6, 12, 11, 17], [11, 17, 7, 13, 6, 12], [6, 12, 8, 14, 7, 13], [7, 13, 9, 15, 8, 14], [8, 14, 10, 16, 9, 15], [9, 15, 11, 17, 10, 16], [10, 16, 6, 12, 11, 17]]

    tiles_weights = [0, 0, 0]

    tiles_scheme = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    teta_L = teta_o-0.5*teta_VP
    teta_R = teta_o+0.5*teta_VP

    teta_RL = min(tiles_longs, key=lambda x:abs(x-teta_L))
    idx = tiles_longs.index(teta_RL)
    if teta_RL < teta_L:
        idx += 1
        teta_RL = tiles_longs[idx]

    teta_LR = min(tiles_longs, key=lambda x:abs(x-teta_R))
    idx = tiles_longs.index(teta_LR)
    if teta_LR > teta_R:
        idx -= 1
        teta_LR = tiles_longs[idx]

    if teta_LR == teta_RL:
        tiles_weights[0] = (teta_RL-teta_L)/(2*teta_VP) # Left tiles
        tiles_weights[1] = (teta_R-teta_LR)/(2*teta_VP) # Right tiles
        tiles_weights[2] = 0                            # Middle tiles

        tiles_scheme[tiles_attributions1[idx][0]] = tiles_weights[0]
        tiles_scheme[tiles_attributions1[idx][1]] = tiles_weights[0]
        tiles_scheme[tiles_attributions1[idx][2]] = tiles_weights[1]
        tiles_scheme[tiles_attributions1[idx][3]] = tiles_weights[1]

    else:
        tiles_weights[0] = (teta_RL-teta_L)/(2*teta_VP) # Left tiles
        tiles_weights[1] = (teta_R-teta_LR)/(2*teta_VP) # Right tiles
        tiles_weights[2] = 60/(2*teta_VP)               # Middle tiles

        tiles_scheme[tiles_attributions2[idx][0]] = tiles_weights[0]
        tiles_scheme[tiles_attributions2[idx][1]] = tiles_weights[0]
        tiles_scheme[tiles_attributions2[idx][2]] = tiles_weights[1]
        tiles_scheme[tiles_attributions2[idx][3]] = tiles_weights[1]
        tiles_scheme[tiles_attributions2[idx][4]] = tiles_weights[2]
        tiles_scheme[tiles_attributions2[idx][5]] = tiles_weights[2]

    return tiles_scheme


# Get current viewport quality
def get_vp_quality(requests, vp_tiles, t, t_stall):
    i = idx = quality = 0

    idx = int((t-t_stall)/1000)
    for i in range(24):
        quality += requests[idx]['tiles'][i]*vp_tiles[i]

    return quality