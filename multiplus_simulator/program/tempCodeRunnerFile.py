def get_CQI(user, t, sim):
    j = 0

    random.seed((1+sim)*1000+(1+user))
    ID = random.randint(1, 200)

    #print 'a', ID

    #ID = user+1

    f = open("cqis-events/cqi_event-"+str(ID)+".txt", "r")

    for x in f:
        cqi_parameters = [float(y) for y in x.split(" ") if x.strip()]
        if cqi_parameters[0]*1000 > t:
            break
        j += 1

    CQI_idx = int([float(k) for k in linecache.getline("cqis-events/cqi_event-"+str(ID)+".txt", j).split(" ") if linecache.getline("cqis-events/cqi_event-"+str(ID)+".txt", j).strip()][1])

    f.close()

    return CQI_idx