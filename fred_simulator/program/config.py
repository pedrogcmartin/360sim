#################################################################################
#                                                                               #
#   Scheduling Algorithms for 360º Video Streaming over 5G Networks Simulator   #
#                                                                               #
#   Developed by: Pedro Martin                                                  #
#                                                                               #
################################################################################# 
 
# Simulation total time duration
T = 60*10**3
# T = 180*10**3

# TTI length
TTI = 1

# Number of users (máx.: 200 users)

#U = [1, 2, 5, 10, 20, 50, 100]
#U = [1, 5, 10, 15, 85, 90, 95, 100]
#U = [25, 30, 35, 45, 50, 55, 65, 70, 75]

#U = [45, 50, 52, 54, 55, 56, 57, 58]
U = [20, 30, 40, 50, 60, 70, 80, 90]
U = [25, 45, 85, 95, 100]
U = [55]
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
Sim = 3

# Buffer size (3 s)
B = 3*10**10
# B = 3*10

# Available RB for allocation per TTI
K = 100

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
G = 1

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

q = [8334, 10417, 12500, 16667, 20834, 29167, 37500, 50000, 62500, 83334, 104167, 125000, 166667, 208334, 250000]

# QAAD tests qualities
#q = [int(400*(10**3)/(6*4)), int(500*(10**3)/(6*4)), int(600*(10**3)/(6*4)), int(800*(10**3)/(6*4)), int(1000*(10**3)/(6*4)), int(1200*(10**3)/(6*4)), int(1500*(10**3)/(6*4)), int(2000*(10**3)/(6*4))]