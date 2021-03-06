#################################################################################
#                                                                               #
#   Scheduling Algorithms for 360º Video Streaming over 5G Networks Simulator   #
#                                                                               #
#   Developed by: Pedro Martin                                                  #
#                                                                               #
################################################################################# 
 
# Simulation total time duration
T = 70*10**3
# T = 180*10**3

# TTI length
TTI = 1

# Estimation throughput parameters
w = 0.875
theta = 0.3*10**3

# Number of users (máx.: 200 users)

#U = [1, 2, 5, 10, 20, 50, 100]
#U = [1, 5, 10, 15, 85, 90, 95, 100]
#U = [25, 30, 35, 45, 50, 55, 65, 70, 75]

#U = [45, 50, 52, 54, 55, 56, 57, 58]
U = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
U = [1]
#U = [36, 37, 38, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49, 51, 52, 53, 54, 56, 57, 58, 59]
#U = [38, 42, 45, 48, 53, 56, 58]
#U = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
#U = [35, 45, 75, 85, 95]
#U = [1]
#U = [1, 2, 5, 10]
#U = [30]
#U = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
#U = [1, 2, 5, 10, 20, 50]

# Number of simulations per scenario
Sim = 1

# Buffer size (3 s)
B = 3*10**30
Bmin = 1.8*10**3
Bmax = 1.8*10**3
Binit = 3*10**3
# B = 3*10

# Available RB for allocation per TTI
K = 5

# Total number of video segments
Ns = 65*10**30

# Numerology
mu = 2

# Segment length (ms)
S = 1*1000

# Number of samples for throughput estimation
St = 3

# Tiling Scheme (horizontal)
Nx = 6
# Tiling Scheme (vertical)
Ny = 4

# MIMO Gain
G = 0.95

# 15 CQI efficiencies
#eff_CQI = [0.1523, 0.3370, 0.8770, 1.4766, 1.9141, 2.4063, 2.7305, 3.3223, 3.9023, 4.5234, 5.1152, 5.5547, 6.2266, 6.9141, 7.4063]
eff_CQI = [0.1523, 0.2344, 0.3770, 0.6016, 0.8770, 1.1758, 1.4766, 1.9141, 2.4063, 2.7305, 3.3223, 3.9023, 4.5234, 5.1152, 5.5547]

# chairliftride video bitrates per tile (assuming 6x4 tiling scheme)
#q = [45834, 70834, 91667, 125000, 175000, 241667]

# Turtle video bitrates per tile (assuming 6x4 tiling scheme)
#filename = '16_Turtle_fixations.csv'
#q = [11572, 15551, 20898, 28083, 37739, 50715]

# UnderwaterPark video bitrates per tile (assuming 6x4 tiling scheme)
#filename = '17_UnderwaterPark_fixations.csv'
#q = [23848, 31621, 41926, 55590, 73707, 97729]

#q = [0.2*10**6, 0.25*10**6, 0.3*10**6, 0.4*10**6, 0.5*10**6, 0.7*10**6, 0.9*10**6, 1.2*10**6, 1.5*10**6, 2.0*10**6, 2.5*10**6, 3.0*10**6, 4.0*10**6, 5.0*10**6, 6.0*10**6]
#q = [8333, 10417, 12500, 16667, 20833, 29167, 37500, 50000, 62500, 83333, 104167, 125000, 166667, 208333, 250000]
#q = [16250, 20833, 27917, 37500, 54167, 74167, 94583]


#Corresponds to: [0.15, 0.30, 0.45, 0.60, 0.75, 0.90, 1.05, 1.20, 1.35, 1.50, 1.65, 1.80, 1.95, 2.10, 2.25, 2.40] Mbps
#q = [6250, 12500, 18750, 25000, 31250, 37500, 43750, 50000, 56250, 62500, 68750, 75000, 81250, 87500, 93750, 100000]

#Corresponds to: [4000000, 6000000, 8000000, 10000000, 12000000]
#q = [166667, 250000, 333333, 416667, 500000]

#q = [8333, 10417, 12500, 16667, 20833, 29167, 37500, 50000, 62500, 83333, 104167, 125000, 166667, 208333, 250000, (8*10**6)/(24), (10*10**6)/(24), (12*10**6)/(24)]

#q = [833.3333333333334, 1666.6666666666667, 2500.0, 3333.3333333333335, 4166.666666666667, 5000.0, 5833.333333333333, 6666.666666666667, 7500.0, 8333.333333333334, 9166.666666666666, 10000.0, 10833.333333333334, 11666.666666666666, 12500.0, 13333.333333333334, 14166.666666666666, 15000.0, 15833.333333333334, 16666.666666666668, 17500.0, 18333.333333333332, 19166.666666666668, 20000.0, 20833.333333333332, 21666.666666666668, 22500.0, 23333.333333333332, 24166.666666666668, 25000.0, 25833.333333333332, 26666.666666666668, 27500.0, 28333.333333333332, 38888.88889]#, 29166.666666666668, 33333.333333333333333]

#q = [833.3333333333334, 5000.0, 9166.666666666666, 13333.333333333334, 17500.0, 21666.666666666668, 25833.333333333332]

# QAAD tests qualities
q = [int(400*(10**3)/(6*4)), int(500*(10**3)/(6*4)), int(600*(10**3)/(6*4)), int(800*(10**3)/(6*4)), int(1000*(10**3)/(6*4)), int(1200*(10**3)/(6*4)), int(1500*(10**3)/(6*4)), int(2000*(10**3)/(6*4))]

QAAD_mu = 10*10**3
QAAD_sigma = 3*10**3