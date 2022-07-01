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
import linecache
import csv
import random
import math

#########################
#                       #
#       Functions       #
#                       #
#########################

# Open salient 360 dataset
def open_file():
	with open(config.filename, 'r') as csvfile:
	    reader = csv.reader(csvfile, delimiter=',')
	    return list(reader)

def average(prev_mean, cnt, ipt):
    cnt += 1.0
    return prev_mean + (ipt-prev_mean)/cnt, cnt

# Updates the buffer occupancy level
def buffer_update(CQI_idx, requests, Nactive_users, RB_allocations, rx_bits, t):
    i = 0
    buffer = bits = 0.0

    # Compute number of streamed bits
    bits = int(round(RB_allocations*1000*config.G*12*14*(2**config.mu)*config.eff_CQI[CQI_idx-1]*0.83*(config.TTI*10**-3)))
    rx_bits += float(bits)/(10**6)

    # Update buffer and request status
    while bits > 0:
        if i >= len(requests):
            break

        if requests[i]['reply_bits'] > 0:
            if requests[i]['reply_bits'] > bits:
                requests[i]['reply_bits'] -= bits
                buffer += float(config.S)*bits/requests[i]['bitrate']
                bits = 0.0
            
            else:
                buffer += float(config.S)*requests[i]['reply_bits']/requests[i]['bitrate']
                bits -= requests[i]['reply_bits']
                requests[i]['reply_bits'] = 0
                requests[i]['reply_time'] = t
                if i >= 2:
                    Nactive_users -= 1

        i += 1

    rx_bits -= float(bits)/(10**6)
            
    return buffer, rx_bits, requests, Nactive_users


# Get CQI index from cqis file for a given user
def get_CQI(user, t, sim, U):
    j = 0

    random.seed((sim+1)*10**6+U*10**3+(user+1))
    #random.seed((sim+1)*10**3+(user+1))

    ID = random.randint(1, 200)

    #ID = 1

    if t == 0:
        print "User (CQI):", user+1, '\t->', ID

    f = open("cqis-events/cqi_event-"+str(ID)+".txt", "r")

    for x in f:
        cqi_parameters = [float(y) for y in x.split(" ") if x.strip()]
        if cqi_parameters[0]*1000 > t:
            break
        j += 1

    CQI_idx = int([float(k) for k in linecache.getline("cqis-events/cqi_event-"+str(ID)+".txt", j).split(" ") if linecache.getline("cqis-events/cqi_event-"+str(ID)+".txt", j).strip()][1])

    f.close()

    return CQI_idx


# Get correct user's entry for the salient 360 dataset
def mirror(ipt):
    if ipt > 20000:
        cnt = int(ipt/20000)
        if cnt % 2 == 0:
            return (int(ipt/200) % 100)
        else:
            return 99 - int((ipt-20000*cnt)/200)
        
    else:
        return int(ipt/200) % 100


# Get viewport center longitude at request time
def get_longitude(dataset, user, t, sim, U):
    random.seed((sim+1)*10**6+U*10**3+(user+1))
    #random.seed((sim+1)*10**3+(user+1))

    ID = random.randint(0, 56)

    #ID = 1

    return float(dataset[(mirror(t)+1)+ID*100][1])*(180.0/math.pi)


# Generate weighted tiling sequence
def generate_tiling_sequence(viewport_tiles, adjacent_tiles, outer_tiles):
    random.shuffle(viewport_tiles)
    random.shuffle(adjacent_tiles)
    random.shuffle(outer_tiles)
    tiles = viewport_tiles
    tiles.extend(adjacent_tiles)
    tiles.extend(outer_tiles)

    return tiles


# Selects and weights tiles according to current viewport
def weighted_tiles(dataset, user, t, sim, U):
    idx_longs = [0, 30, 90, 150, 210, 270, 330, 360]
    tiles_atribution = [[[6, 11, 12, 17], [0, 1, 4, 5, 7, 10, 13, 16, 18, 19, 22, 23], [2, 3, 8, 9, 14, 15, 20, 21]], [[6, 7, 12, 13], [0, 1, 2, 8, 14, 18, 19, 20, 5, 11, 17, 23], [3, 4, 9, 10, 15, 16, 21, 22]], [[7, 8, 13, 14], [0, 1, 2, 3, 6, 9, 12, 15, 18, 19, 20, 21], [4, 5, 10, 11, 16, 17, 22, 23]], [[8, 9, 14, 15], [1, 2, 3, 4, 7, 10, 13, 16, 19, 20, 21, 22], [0, 5, 6, 11, 12, 17, 18, 23]], [[9, 10, 15, 16], [2, 3, 4, 5, 8, 11, 14, 17, 20, 21, 22, 23], [0, 1, 6, 7, 12, 13, 18, 19]], [[10, 11, 16, 17], [3, 4, 5, 9, 15, 21, 22, 23, 0, 6, 12, 18], [1, 2, 7, 8, 13, 14, 19, 20]],[[6, 11, 12, 17], [0, 1, 4, 5, 7, 10, 13, 16, 18, 19, 22, 23], [2, 3, 8, 9, 14, 15, 20, 21]]]

    teta_o = get_longitude(dataset, user, t, sim, U)

    if teta_o < 0:
        teta_o += 360

    elif teta_o >= 360:
	    teta_o -= 360

    teta_idx = min(idx_longs, key=lambda x:abs(x-teta_o))
    idx = idx_longs.index(teta_idx)
    if teta_idx > teta_o:
        idx -= 1
        teta_idx = idx_longs[idx]

    return generate_tiling_sequence(tiles_atribution[idx][0], tiles_atribution[idx][1], tiles_atribution[idx][2])


def estimate_throughput(previous_throughput, K_bits, t, buffer, first_U):
    est_throughput = 0.0

    if first_U:
        est_throughput = K_bits*(10**6)*1000.0/config.theta
        first_U = False
    
    else:
        est_throughput = config.w * previous_throughput + (1 - config.w) * K_bits*(10**6)*1000.0/config.theta

    #print 'time:', t, '\tpreviousU:', previous_throughput, '\testU:', est_throughput, '\tKbits:', K_bits*10**6, '\tbuffer:', buffer, '\n'

    return est_throughput, first_U


# Computes the estimated throughput perceived by the client's device
def throughput_estimation(requests, init_t):
    j = throughput = 0

    for j, i in reversed(list(enumerate(requests))):
        if i['reply_bits'] == 0:
            break

    for i in range(config.St):
        if requests[j-i]['request_time'] == init_t and requests[j-i]['reply_time']-requests[j-i-1]['reply_time'] > 0:
            throughput += (1/float(config.St))*1000*requests[j-i]['bitrate']/(requests[j-i]['reply_time']-requests[j-i-1]['reply_time'])

        else:
            throughput += (1/float(config.St))*1000*requests[j-i]['bitrate']/(requests[j-i]['reply_time']-requests[j-i]['request_time'])

    throughput = throughput*(float(config.S)/1000.0)

    return throughput


# When in buffering event client requests 3s of video (3 segments of 1s) with lowest quality
def request_LQ(requests, t):
    x = 1

    if t <= 1*10**3:
        requests = [{'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[x-1], 'tiles':[x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x], 'reply_bits':config.Nx*config.Ny*config.q[x-1], 'reply_time':0, 'estimated_throughput':0}]

    else:
        requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[x-1], 'tiles':[x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x], 'reply_bits':config.Nx*config.Ny*config.q[x-1], 'reply_time':0, 'estimated_throughput':0})
    
    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[x-1], 'tiles':[x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x], 'reply_bits':config.Nx*config.Ny*config.q[x-1], 'reply_time':0, 'estimated_throughput':0})
    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[x-1], 'tiles':[x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x], 'reply_bits':config.Nx*config.Ny*config.q[x-1], 'reply_time':0, 'estimated_throughput':0})

    return requests


# Rate adpatation segment request
def request_RA_BFA(requests, t, t_dur_stalls, throughput, dataset, user, sim, U):
    delta_budget = 0

    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[0], 'tiles':[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'reply_bits':config.Nx*config.Ny*config.q[0], 'reply_time':0, 'estimated_throughput':throughput})

    budget = throughput - config.Nx*config.Ny*config.q[0]

    tiles = weighted_tiles(dataset, user, t-t_dur_stalls, sim, U)

    for idx, current_q in enumerate(config.q[1:]):
        for current_tile in tiles:
            delta_budget = current_q - config.q[idx]
            if budget >= delta_budget:
                requests[-1]['tiles'][current_tile] += 1
                requests[-1]['bitrate'] += delta_budget
                budget -= delta_budget

    requests[-1]['reply_bits'] = requests[-1]['bitrate']

    return requests



def request_RA_BQA1(requests, t, t_dur_stalls, throughput, dataset, user, buffer, sim, U, Bmax):
    delta_budget = 0

    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[0], 'tiles':[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'reply_bits':config.Nx*config.Ny*config.q[0], 'reply_time':0, 'estimated_throughput':throughput})

    if buffer > Bmax:
        throughput = throughput*buffer/Bmax
        #print 'b', 'time', t, 'throughput:', throughput, 'budget', budget, 'buffer', buffer, 'Bmax', config.Bmax

    budget = throughput - config.Nx*config.Ny*config.q[0]

    tiles = weighted_tiles(dataset, user, t-t_dur_stalls, sim, U)
    
    for idx, current_q in enumerate(config.q[1:]):
        for current_tile in tiles:
            delta_budget = current_q - config.q[idx]
            if budget >= delta_budget:
                requests[-1]['tiles'][current_tile] += 1
                requests[-1]['bitrate'] += delta_budget
                budget -= delta_budget
                
    requests[-1]['reply_bits'] = requests[-1]['bitrate']

    return requests



def request_RA_BQA2(requests, t, t_dur_stalls, throughput, dataset, user, buffer, sim, U, Bmin, Bmax):
    delta_budget = 0

    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[0], 'tiles':[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'reply_bits':config.Nx*config.Ny*config.q[0], 'reply_time':0, 'estimated_throughput':throughput})

    if buffer < Bmin:
        throughput = throughput*buffer/Bmin
        #print 'a', 'time', t, 'throughput:', throughput, 'budget', budget, 'buffer', buffer, 'Bmin', config.Bmin

    elif buffer > Bmax:
        throughput = throughput*buffer/Bmax
        #print 'b', 'time', t, 'throughput:', throughput, 'budget', budget, 'buffer', buffer, 'Bmax', config.Bmax

    budget = throughput - config.Nx*config.Ny*config.q[0]

    tiles = weighted_tiles(dataset, user, t-t_dur_stalls, sim, U)
    
    for idx, current_q in enumerate(config.q[1:]):
        for current_tile in tiles:
            delta_budget = current_q - config.q[idx]
            if budget >= delta_budget:
                requests[-1]['tiles'][current_tile] += 1
                requests[-1]['bitrate'] += delta_budget
                budget -= delta_budget
                
    requests[-1]['reply_bits'] = requests[-1]['bitrate']

    return requests


# When in buffering event client requests 3s of video (3 segments of 1s) with lowest quality
def request_LQ_QAAD(requests, t):
    x = 1
    y = (x-1)/3+1

    if t == 0:
        requests = [{'request_time':t, 'bitrate':config.q_qaad[x-1], 'tiles':[y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y], 'reply_bits':config.q_qaad[x-1], 'reply_time':0, 'estimated_throughput':0}]

    else:
        requests.append({'request_time':t, 'bitrate':config.q_qaad[x-1], 'tiles':[y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y], 'reply_bits':config.q_qaad[x-1], 'reply_time':0, 'estimated_throughput':0})
    
    requests.append({'request_time':t, 'bitrate':config.q_qaad[x-1], 'tiles':[y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y], 'reply_bits':config.q_qaad[x-1], 'reply_time':0, 'estimated_throughput':0})
    requests.append({'request_time':t, 'bitrate':config.q_qaad[x-1], 'tiles':[y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y], 'reply_bits':config.q_qaad[x-1], 'reply_time':0, 'estimated_throughput':0})

    return requests


# Rate adpatation segment request (QAAD algorithm)
def request_RA_QAAD(requests, t, t_dur_stalls, throughput, dataset, user, buffer, sim, U, sigma, mu):
    x = 1

    requests.append({'request_time':t, 'bitrate':config.q_qaad[x-1], 'tiles':[x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x], 'reply_bits':config.q_qaad[x-1], 'reply_time':0, 'estimated_throughput':throughput})

    l_best = min(config.q_qaad, key=lambda x:abs(x-throughput))
    l_best_idx = config.q_qaad.index(l_best)
    if l_best > throughput:
        l_best_idx -= 1
        l_best = config.q_qaad[l_best_idx]

    l_prev = requests[-2]['bitrate']
    l_prev_idx = config.q_qaad.index(l_prev)

    #print "time:", t, "throughput:", throughput, "l_best_idx:", l_best_idx+1, "l_best:", l_best, "l_prev_idx:", l_prev_idx+1, "l_prev:", l_prev

    if l_best_idx == l_prev_idx:
        l_next_idx = l_prev_idx
    
    elif l_best_idx > l_prev_idx:
        if buffer > mu:
            l_next_idx = l_prev_idx + 1
        
        else:
            l_next_idx = l_prev_idx
    
    else:
        k = t_qaad = n_qaad = 0
        while n_qaad < 1 and k < l_prev_idx:
            t_qaad = ((buffer-sigma)/1000.0)/(1-throughput/config.q_qaad[l_prev_idx-k])
            #print "tQAAD:", t_qaad, "buffer:", buffer, "throughput:", throughput, "b(lprev-k):", config.q_qaad[l_prev_idx-k]
            if t_qaad < 0 and buffer > sigma:
                k += 1
                break
            n_qaad = (t_qaad*throughput)/((config.S/1000.0)*config.q_qaad[l_prev_idx-k])
            #print "nQAAD:", n_qaad
            k += 1
            #print "k:", k
            """print "buffer:", buffer, "throughput:", throughput
            print "n_qaad:", n_qaad, "t_qaad:", t_qaad, "k:", k
            print"""
        
        l_next_idx = l_prev_idx - (k-1)

    #print "l_next:", l_next_idx+1, config.q_qaad[l_next_idx]
    #print

    tiles = weighted_tiles(dataset, user, t-t_dur_stalls, sim, U)

    for current_tile in tiles[:4]:
        requests[-1]['tiles'][current_tile] = config.q_qaad_idx[l_next_idx][0]
    
    for current_tile in tiles[4:16]:
        requests[-1]['tiles'][current_tile] = config.q_qaad_idx[l_next_idx][1]
    
    for current_tile in tiles[16:24]:
        requests[-1]['tiles'][current_tile] = config.q_qaad_idx[l_next_idx][2]
                
    requests[-1]['reply_bits'] = requests[-1]['bitrate'] = config.q_qaad[l_next_idx]

    #print "time:", t/1000.0, "buffer:", buffer, "#requests:", len(requests)-1, "throughput:", throughput, "l_best:", l_best_idx+1, "l_prev:", l_prev_idx+1, "l_next:", l_next_idx+1
    #print "time:", t, "buffer:", buffer, "#requests:", len(requests)-1, "throughput:", throughput, "l_best_idx:", l_best_idx+1, "l_best:", l_best, "l_prev_idx:", l_prev_idx+1, "l_prev:", l_prev, "Last_bitrate:", requests[-2]['bitrate'], "l_next_idx:", l_next_idx+1, "l_next:", config.q_qaad[l_next_idx]

    return requests