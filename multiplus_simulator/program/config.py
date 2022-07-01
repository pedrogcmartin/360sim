#################################################################################
#                                                                               #
#   Scheduling Algorithms for 360º Video Streaming over 5G Networks Simulator   #
#                                                                               #
#   Developed by: Pedro Martin                                                  #
#                                                                               #
################################################################################# 
 
# Simulation total time duration
T = 60*10**3

# TTI length
TTI = 1

# Number of users (máx.: 200 users)

#U = [1, 2, 5, 10, 20, 50, 100]
#U = [1, 5, 10, 15, 85, 90, 95, 100]
#U = [25, 30, 35, 45, 50, 55, 65, 70, 75]
#U = [10, 20, 30, 40, 50, 60, 70, 80, 100]
U = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
#U = [65]
#U = [40, 45]
#U = [10, 20, 30, 40, 50, 60, 70, 80, 100]
#U = [60, 75]
#U = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
#U = [5]
#U = [25, 42, 44, 46, 48, 55, 85, 90, 95]
#U = [1, 2, 5, 10]
#U = [30]
#U = [1, 2, 5, 10]

# Number of simulations per scenario
Sim = 5

# Buffer size (3 s)
B = 3*10**3

Bmin = 1.63*10**3
Bmax = 1.63*10**3

# Inital playout buffer length
init = 3*10**3
epsilon = 0.01

# Estimation throughput parameters
w = 0.875
theta = 0.020*10**3

# Available RB for allocation per TTI
K = 11

# Total number of video segments
Ns = 65*10**30

# Numerology
mu = 2

# Segment length (ms)
S = 1*10**3

# Number of samples for throughput estimation
St = 3

# Tiling Scheme (horizontal)
Nx = 6
# Tiling Scheme (vertical)
Ny = 4

# MIMO Gain
G = 1

# 15 CQI efficiencies
eff_CQI = [0.1523, 0.3370, 0.8770, 1.4766, 1.9141, 2.4063, 2.7305, 3.3223, 3.9023, 4.5234, 5.1152, 5.5547, 6.2266, 6.9141, 7.4063]

# chairliftride video bitrates per tile (assuming 6x4 tiling scheme)
#q = [45834, 70834, 91667, 125000, 175000, 241667]

# Turtle video bitrates per tile (assuming 6x4 tiling scheme)
#filename = '16_Turtle_fixations.csv'
#q = [11572, 15551, 20898, 28083, 37739, 50715]

# UnderwaterPark video bitrates per tile (assuming 6x4 tiling scheme)
filename = '17_UnderwaterPark_fixations.csv'

q = [16250, 20833, 27917, 37500, 54167, 74167, 94583]

q_qaad = [390000, 408332, 463328, 499992, 528328, 613336, 670008, 708340, 823336, 900000, 966668, 1166672, 1300008, 1380008, 1620008, 1780008, 1861672, 2106664, 2269992]
q_qaad_idx = [[1, 1, 1], [2, 1, 1], [2, 2, 1], [2, 2, 2], [3, 2, 2], [3, 3, 2], [3, 3, 3], [4, 3, 3], [4, 4, 3], [4, 4, 4], [5, 4, 4], [5, 5, 4], [5, 5, 5], [6, 5, 5], [6, 6, 5], [6, 6, 6], [7, 6, 6], [7, 7, 6], [7, 7, 7]]

QAAD_mu = 1.8*10**3
QAAD_sigma = 0.5*10**3

gamma = 60

"""for i in range(len(q)):
    a.append(q[i]*24)
    try:
        a.append(q[i+1]*4+q[i]*20)
        a.append(q[i+1]*16+q[i]*8)
    except:
        break

print(a)"""

"""for i in range(len(q)):
    a.append([i+1, i+1, i+1])
    try:
        a.append([i+2, i+1, i+1])
        a.append([i+2, i+2, i+1])
    except:
        break

print(a)"""