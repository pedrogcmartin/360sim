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

# Updates the buffer occupancy level
def buffer_update(CQI_idx, requests, RB_allocations, rx_bits, K_bits, t):
    i = buffer = bits = 0

    # Compute number of streamed bits
    #bits = int(round(RB_allocations*1000*config.G*12*14*(2**config.mu)*config.eff_CQI[CQI_idx-1]*0.72/1000))
    bits = int(round(RB_allocations*1000*config.G*12*7*2*config.eff_CQI[CQI_idx-1]*0.75/1000))
    rx_bits += float(bits)
    K_bits += float(bits)

    # Update buffer and request status
    while bits > 0:
        if i >= len(requests):
            break

        if requests[i]['reply_bits'] > 0:
            if requests[i]['reply_bits'] > bits:
                requests[i]['reply_bits'] -= bits
                buffer += float(config.S)*bits/requests[i]['bitrate']
                bits = 0
            
            else:
                buffer += float(config.S)*requests[i]['reply_bits']/requests[i]['bitrate']
                bits -= requests[i]['reply_bits']
                requests[i]['reply_bits'] = 0
                requests[i]['reply_time'] = t

        i += 1

    rx_bits -= float(bits)
    K_bits -= float(bits)
            
    return buffer, rx_bits, K_bits, requests


# Get CQI index from cqis file for a given user
def get_CQI(user, t, sim):
    j = 0

    random.seed((1+sim)*1000+(1+user))
    ID = random.randint(1, 200)

    ID = user+1

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
def get_longitude(dataset, U, t):
	return float(dataset[(mirror(t)+1)+(U%57)*100][1])


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
def weighted_tiles(dataset, U, t):
    idx_longs = [0, 30, 90, 150, 210, 270, 330, 360]
    tiles_atribution = [[[6, 11, 12, 17], [0, 1, 4, 5, 7, 10, 13, 16, 18, 19, 22, 23], [2, 3, 8, 9, 14, 15, 20, 21]], [[6, 7, 12, 13], [0, 1, 2, 8, 14, 18, 19, 20, 5, 11, 17, 23], [3, 4, 9, 10, 15, 16, 21, 22]], [[7, 8, 13, 14], [0, 1, 2, 3, 6, 9, 12, 15, 18, 19, 20, 21], [4, 5, 10, 11, 16, 17, 22, 23]], [[8, 9, 14, 15], [1, 2, 3, 4, 7, 10, 13, 16, 19, 20, 21, 22], [0, 5, 6, 11, 12, 17, 18, 23]], [[9, 10, 15, 16], [2, 3, 4, 5, 8, 11, 14, 17, 20, 21, 22, 23], [0, 1, 6, 7, 12, 13, 18, 19]], [[10, 11, 16, 17], [3, 4, 5, 9, 15, 21, 22, 23, 0, 6, 12, 18], [1, 2, 7, 8, 13, 14, 19, 20]],[[6, 11, 12, 17], [0, 1, 4, 5, 7, 10, 13, 16, 18, 19, 22, 23], [2, 3, 8, 9, 14, 15, 20, 21]]]

    teta_o = get_longitude(dataset, U, t)

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


def estimate_throughput(previous_throughput, K_bits, t, buffer):
    est_throughput = 0.0

    if t == 300:
        est_throughput = K_bits*1000.0/config.theta
    
    else:
        est_throughput = config.w * previous_throughput + (1 - config.w) * K_bits*1000.0/config.theta

    #print t, previous_throughput, est_throughput, K_bits, buffer, '\n'

    return est_throughput


# Computes the estimated throughput perceived by the client's device
def throughput_estimation(requests):
    j = throughput = 0

    for j, i in reversed(list(enumerate(requests))):
        if i['reply_bits'] == 0:
            break

    #if user == 0:
    #    print '\n'
    for i in range(config.St):
        throughput += (1/float(config.St))*1000*requests[j-i]['bitrate']/(requests[j-i]['reply_time']-requests[j-i-1]['reply_time'])

    throughput = throughput*(config.S/1000)

    return throughput


# When in buffering event client requests 3s of video (3 segments of 1s) with lowest quality
def request_LQ(requests, t):
    x = 1

    if t == 0:
        requests = [{'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[x-1], 'tiles':[x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x], 'reply_bits':config.Nx*config.Ny*config.q[x-1], 'reply_time':0, 'estimated_throughput':0}]

    else:
        requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[x-1], 'tiles':[x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x], 'reply_bits':config.Nx*config.Ny*config.q[x-1], 'reply_time':0, 'estimated_throughput':0})
    
    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[x-1], 'tiles':[x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x], 'reply_bits':config.Nx*config.Ny*config.q[x-1], 'reply_time':0, 'estimated_throughput':0})
    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[x-1], 'tiles':[x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x], 'reply_bits':config.Nx*config.Ny*config.q[x-1], 'reply_time':0, 'estimated_throughput':0})
    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[x-1], 'tiles':[x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x], 'reply_bits':config.Nx*config.Ny*config.q[x-1], 'reply_time':0, 'estimated_throughput':0})
    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[x-1], 'tiles':[x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x], 'reply_bits':config.Nx*config.Ny*config.q[x-1], 'reply_time':0, 'estimated_throughput':0})
    
    """if t == 0:
        requests = [{'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[0], 'tiles':[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'reply_bits':config.Nx*config.Ny*config.q[0], 'reply_time':0, 'estimated_throughput':0}]

    else:
        requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[0], 'tiles':[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'reply_bits':config.Nx*config.Ny*config.q[0], 'reply_time':0, 'estimated_throughput':0})
    
    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[0], 'tiles':[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'reply_bits':config.Nx*config.Ny*config.q[0], 'reply_time':0, 'estimated_throughput':0})
    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[0], 'tiles':[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'reply_bits':config.Nx*config.Ny*config.q[0], 'reply_time':0, 'estimated_throughput':0})
    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[0], 'tiles':[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'reply_bits':config.Nx*config.Ny*config.q[0], 'reply_time':0, 'estimated_throughput':0})
    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[0], 'tiles':[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'reply_bits':config.Nx*config.Ny*config.q[0], 'reply_time':0, 'estimated_throughput':0})"""

    return requests


# Rate adpatation segment request
def request_RA(requests, t, t_dur_stalls, throughput, buffer):
    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[0], 'tiles':[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'reply_bits':config.Nx*config.Ny*config.q[0], 'reply_time':0, 'estimated_throughput':throughput})

    budget = throughput# - config.Nx*config.Ny*config.q[0]

    if buffer < config.Bmin:
        #budget = budget
        budget = budget*buffer/config.Bmin
        #print 'a', 'time', t, 'throughput:', throughput, 'budget', budget, 'buffer', buffer, 'Bmin', config.Bmin

    elif buffer > config.Bmax:
        budget = budget*buffer/config.Bmax
        #print 'b', 'time', t, 'throughput:', throughput, 'budget', budget, 'buffer', buffer, 'Bmax', config.Bmax

    #tiles = weighted_tiles(dataset, U, t-t_dur_stalls)

    """if t <= 60000:
        for tile in range(24):
            requests[-1]['tiles'][tile] = 7
        
        requests[-1]['bitrate'] = 6*4*config.q[6]

    else:
        for tile in range(24):
            requests[-1]['tiles'][tile] = 3
        
        requests[-1]['bitrate'] = 6*4*config.q[2]"""

    for current_q in config.q[1:]:
        if config.Nx*config.Ny*current_q <= budget:
            #budget -= config.Nx*config.Ny*current_q
            requests[-1]['bitrate'] = config.Nx*config.Ny*current_q
            for tile in range(24):
                requests[-1]['tiles'][tile] += 1


    """for current_q in config.q[1:]:
        for current_tile in tiles:
            if current_q <= budget:
                requests[-1]['tiles'][current_tile] += 1
                requests[-1]['bitrate'] += current_q
                budget -= current_q"""

    requests[-1]['reply_bits'] = requests[-1]['bitrate']

    #ql = (1.0/4.0)*(float(requests[-1]['tiles'][tiles[0]])+float(requests[-1]['tiles'][tiles[1]])+float(requests[-1]['tiles'][tiles[2]])+float(requests[-1]['tiles'][tiles[3]]))
    #print t, U, ql, requests[-1]['tiles'][tiles[0]], requests[-1]['tiles'][tiles[1]], requests[-1]['tiles'][tiles[2]], requests[-1]['tiles'][tiles[3]]
    #sum_ql += ql
    #sum_ql_sq += ql**2

    return requests#, sum_ql, sum_ql_sq


# Rate adpatation segment request (QAAD algorithm)
def request_RA_QAAD(requests, t, throughput, buffer):
    x = 1

    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[x-1], 'tiles':[x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x], 'reply_bits':config.Nx*config.Ny*config.q[x-1], 'reply_time':0, 'estimated_throughput':throughput})

    l_best = min(config.q, key=lambda x:abs(x-throughput/24.0))
    l_best_idx = config.q.index(l_best)
    if l_best > throughput/24.0:
        l_best_idx -= 1
    
    l_best = config.q[l_best_idx]*config.Nx*config.Ny

    l_prev = requests[-2]['bitrate']
    l_prev_idx = config.q.index(l_prev/24.0)

    #print "time:", t, "throughput:", throughput, "l_best_idx:", l_best_idx+1, "l_best:", l_best, "l_prev_idx:", l_prev_idx+1, "l_prev:", l_prev

    if l_best_idx == l_prev_idx:
        l_next_idx = l_prev_idx
    
    elif l_best_idx > l_prev_idx:
        if buffer > config.QAAD_mu:
            l_next_idx = l_prev_idx + 1
        
        else:
            l_next_idx = l_prev_idx
    
    else:
        if l_best_idx < l_prev_idx:
            k = t_qaad = n_qaad = 0
            while n_qaad < 1 and k < l_prev_idx:
                t_qaad = (buffer-float(config.QAAD_sigma))/(1.0-float(throughput)/float(config.q[l_prev_idx-k]*config.Nx*config.Ny))
                #print "tQAAD:", t_qaad, "buffer:", buffer, "throughput:", throughput, "b(lprev-k):", config.q[l_prev_idx-k]*config.Nx*config.Ny
                if t_qaad < 0 and buffer > config.QAAD_sigma:
                    break
                n_qaad = (t_qaad*float(throughput))/(float(config.S)*float(config.q[l_prev_idx-k]*config.Nx*config.Ny))
                #print "nQAAD:", n_qaad
                k += 1
                #print "k:", k
                """print "buffer:", buffer, '\t', "throughput:", throughput
                print "n_qaad:", n_qaad, '\t', "t_qaad:", t_qaad, '\t', "k:", k
                print"""
            
            l_next_idx = l_prev_idx - (k-1)

    for tile in range(24):
        requests[-1]['tiles'][tile] = l_next_idx+1

    requests[-1]['reply_bits'] = requests[-1]['bitrate'] = config.q[l_next_idx]*config.Nx*config.Ny

    #print "l_next:", l_next_idx+1
    #print

    #print "time:", t/1000.0, "buffer:", buffer, "#requests:", len(requests)-1, "throughput:", throughput, "l_best:", l_best_idx+1, "l_prev:", l_prev_idx+1, "l_next:", l_next_idx+1
    #print "time:", t, '\t', "buffer:", buffer, '\t', "#requests:", len(requests)-1, '\t', "throughput:", throughput, '\t', "l_best_idx:", l_best_idx+1, '\t', "l_best:", l_best, '\t', "l_prev_idx:", l_prev_idx+1, '\t', "l_prev:", l_prev, '\t', "Last_bitrate:", requests[-2]['bitrate'], '\t', "l_next_idx:", l_next_idx+1, '\t', "l_next:", config.q[l_next_idx]

    return requests


# Store buffer parameters
def store_buffer(t, i, buffer_worksheet, allocation_worksheet, buffer, play, rx_bits, reported_CQI, metric, total_RB_allocations, RB_allocations):
    buffer_worksheet.write(int(t)+1, 5*i+1, buffer)
    buffer_worksheet.write(int(t)+1, 5*i+2, play)
    buffer_worksheet.write(int(t)+1, 5*i+3, rx_bits*1000/(t+1))
    buffer_worksheet.write(int(t)+1, 5*i+5, int(round(RB_allocations*1000*config.G*12*14*(2**config.mu)*config.eff_CQI[reported_CQI-1]*0.72)))
    allocation_worksheet.write(int(t)+1, 2*i+1, total_RB_allocations)
    allocation_worksheet.write(int(t)+1, 2*i+2, RB_allocations)
    if metric < 0:
        buffer_worksheet.write(int(t)+1, 5*i+4, 0)
    else:
        buffer_worksheet.write(int(t)+1, 5*i+4, metric)