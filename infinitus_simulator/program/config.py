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
#U = [35]
#U = [95]
U = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
#U = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
#U = [60]
#U = [1, 2, 5, 10, 20, 50]

# Number of simulations per scenario
Sim = 1

# Buffer size (3 s)
B = 3*10**3

# Available RB for allocation per TTI
K = 18

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
eff_CQI = [0.1523, 0.3370, 0.8770, 1.4766, 1.9141, 2.4063, 2.7305, 3.3223, 3.9023, 4.5234, 5.1152, 5.5547, 6.2266, 6.9141, 7.4063]

# chairliftride video bitrates per tile (assuming 6x4 tiling scheme)
#q = [45834, 70834, 91667, 125000, 175000, 241667]

# Turtle video bitrates per tile (assuming 6x4 tiling scheme)
#filename = '16_Turtle_fixations.csv'
#q = [11572, 15551, 20898, 28083, 37739, 50715]

# UnderwaterPark video bitrates per tile (assuming 6x4 tiling scheme)
filename = '17_UnderwaterPark_fixations.csv'
q = [23848, 31621, 41926, 55590, 73707, 97729]
#q = [23848, 27735, 31621, 36774, 41926, 48758, 55590, 64649, 73707, 85718, 97729]