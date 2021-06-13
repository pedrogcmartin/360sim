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
def buffer_update(user, requests, RB_allocations, rx_bits, t):
    i = buffer = bits = 0

    CQI_idx = get_CQI(user, t)

    # Compute number of streamed bits
    bits = int(round(RB_allocations*1000*config.G*12*14*(2**config.mu)*config.eff_CQI[CQI_idx-1]*0.72/1000))
    rx_bits += float(bits)/(10**6)

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

    rx_bits -= float(bits)/(10**6)
            
    return buffer, rx_bits, requests


# Get CQI index from cqis file for a given user
def get_CQI(user, t):
    j = 0

    f = open("cqis-events/cqi_event-"+str(user+1)+".txt", "r")

    for x in f:
        cqi_parameters = [float(y) for y in x.split(" ") if x.strip()]
        if cqi_parameters[0]*1000 > t:
            break
        j += 1

    CQI_idx = int([float(k) for k in linecache.getline("cqis-events/cqi_event-"+str(user+1)+".txt", j).split(" ") if linecache.getline("cqis-events/cqi_event-"+str(user+1)+".txt", j).strip()][1])

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


# Computes the estimated throughput perceived by the client's device
def throughput_estimation(requests):
    j = throughput = 0

    for j, i in reversed(list(enumerate(requests))):
        if i['reply_bits'] == 0:
            break

    for i in range(config.St):
        throughput += (1/float(config.St))*1000*requests[j-i]['bitrate']/(requests[j-i]['reply_time']-requests[j-i]['request_time'])

    throughput = throughput*(config.S/1000)

    return throughput


# When in buffering event client requests 3s of video (3 segments of 1s) with lowest quality
def request_LQ(requests, t):
    if t == 0:
        requests = [{'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[0], 'tiles':[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'reply_bits':config.Nx*config.Ny*config.q[0], 'reply_time':0, 'estimated_throughput':0}]

    else:
        requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[0], 'tiles':[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'reply_bits':config.Nx*config.Ny*config.q[0], 'reply_time':0, 'estimated_throughput':0})
    
    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[0], 'tiles':[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'reply_bits':config.Nx*config.Ny*config.q[0], 'reply_time':0, 'estimated_throughput':0})
    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[0], 'tiles':[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'reply_bits':config.Nx*config.Ny*config.q[0], 'reply_time':0, 'estimated_throughput':0})

    return requests


# Rate adpatation segment request
def request_RA(requests, t, t_dur_stalls, throughput, dataset, U):
    delta_budget = 0

    requests.append({'request_time':t, 'bitrate':config.Nx*config.Ny*config.q[0], 'tiles':[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'reply_bits':config.Nx*config.Ny*config.q[0], 'reply_time':0, 'estimated_throughput':throughput})

    budget = throughput - config.Nx*config.Ny*config.q[0]

    tiles = weighted_tiles(dataset, U, t-t_dur_stalls)
    
    for idx, current_q in enumerate(config.q[1:]):
        for current_tile in tiles:
            delta_budget = current_q - config.q[idx]
            if budget >= delta_budget:
                requests[-1]['tiles'][current_tile] += 1
                requests[-1]['bitrate'] += delta_budget
                budget -= delta_budget

    requests[-1]['reply_bits'] = requests[-1]['bitrate']

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