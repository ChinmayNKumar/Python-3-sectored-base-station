import numpy as np
import numpy.random as npr
import math

#Project submitted by Chinmay Nagesh Kumar

#Default parameters (length of road: 6 km, no. of users: 160, HOm = 3dB)

#Base station parameters

f = [860, 865] #Frequency for alpha and beta sectors
hb = 50 #Height of basestation
ptx = 43 #Transmitted Power
L = 2 #Line loss
gtx = 15 #Transmitter Gain
nch_alpha = 15 #No. of available channels for alpha
nch_beta = 15 #No. of available channels for beta
eirp = ptx + gtx - L #EIRP

#Mobile parameters

hm = 1.5 #Height of mobile
hom = 3 #Handoff margin
rsl_thresh = -102 #Mobile Rx threshold

#Creating a uniform distribution of 160 or 320 users

users = npr.uniform(0, 6, size=160) #Generating 160 users distributed uniformly along the length of the road
userID = list(range(1,161)) #Generating user IDs for 160 users
direction = npr.random_integers(0, 1, size=160)
x = np.column_stack((users, direction)) #2-D array containing initial location of user and direction
user_dict = dict(zip(userID, x)) #This line zips the user ID with the location and direction of the user. And then, the dict command creates a key-value relationship between userid and x

#Initializing rsl values
rsl_alpha = 0
rsl_beta = 0
rsl_server = 0

#Counts the total no. of call attempts  
call_count = 0

n=1 #Keeps track of the no. of hours elapsed

#Defining lists for statistics

droppedcall_ssa = [] #Dropped calls due to Signal strength for sector alpha
droppedcall_ssb = [] #Dropped calls due to Signal strength for sector beta
blockedcall_capacitya = [] #Blocked calls due to capacity for sector alpha
blockedcall_capacityb = [] #Blocked calls due to capacity for sector beta
activecalls_a = {} #Active calls for sector alpha
activecalls_b = {} #Active calls for sector beta
successful_callsa = [] #Successful calls for sector alpha
successful_callsb = [] #Successful calls for sector beta
handoff_attempta = [] #Handoff attempts for Sector alpha
handoff_attemptb = [] #Handoff attempts for sector beta
handoff_successa = [] #Successful handoffs out of sector alpha
handoff_successb = [] #Successful handoffs out of sector beta
handoff_failurea = [] #Handoff failures out of sector alpha
handoff_failureb = [] #Handoff failures out of sector beta
call_length = {} #Call length dict


#Function definition to calculate Propagation loss due to Okumura-Hata Model

def hata(loc, f):
    
    global hb #Referencing the global object hb
    
    d = math.sqrt(((loc - 3)*(loc - 3)) + 0.0004) #Calculating the distance between BS and mobile using distance formula

    #Using Hata model for a small city:
    
    hata_pl = (69.55  +  26.16*math.log10(f) - 13.82*math.log10(hb) + (44.9 - 6.55*math.log10(hb))*math.log10(d) - ((1.1*math.log10(f) - 0.7)*1.5 - (1.56*math.log10(f) - 0.8)))
    
    return hata_pl

#Function definition for Shadowing

#Generating 600 samples of shadowing values

shadow_dict = {}
shadow_values = npr.normal(0, 2, 600)
shadow_keys = list(range(1, 601))
shadow_dict = dict(zip(shadow_keys, shadow_values))

def shadowing(loc):

    global shadow_dict #Referncing global object shadow_dict

    return shadow_dict[math.floor((loc*100))+1]   #This computes the shadowing interval and finds the corresponding values from the dict


#Function definition for Fading

def fading():

    mu = 0 #Mean = 0
    sigma = 1 #Standard deviation = 1

    #Creating 2 normal distributions of 10 samples with the above mean and Std. deviation
    x = npr.normal(mu, sigma, 10)
    y = npr.normal(mu, sigma, 10)

    #Creating array 'z' of complex Gaussian random values using 'x' and 'y'
    z = x + y*(1j)

    #Finding the magnitude 'mag' of z
    mag = np.abs(z)
    mag = 10*np.log10(mag)
    mag1 = np.delete(mag,np.argmin(mag))
    fade = np.min(mag1)
    
    return fade

#Calculation of Antenna discrimination loss
antenna_discloss = [] #This list will contain the returned values from antenna_discrimation function. These will then be subtracted from the EIRP locally.

#Reading from the antenna pattern file

fobj = open("C:\\Users\\Chinmay\\Documents\\Python_Scripts\\Project\\antenna_pattern.txt","r")
all_lines = fobj.readlines()
fobj.close()

antenna_dict = {} #Dict will contain antenna angles and their corresponding losses

#The following loop creates a dictionary containing antenna angles and their corresponding losses. This is being done outside the function to reduce execution time

for j in range(360):

        temp_line = all_lines[j].splitlines() #Split the 'j'th line base on newline character 
        temp_line = temp_line[0].split('\t') #Now we have two elements in a list containing the angle and loss
        angle = float(temp_line[0]) #Converting both to float before appending to the dictionary
        loss = float(temp_line[1])
        antenna_dict[angle] = loss 
        
def antenna_discrimination(loc):

    #Define the unit vectors in the direction of the boresight
    unit_a = (0, 1)
    unit_b = (math.sqrt(3)/2, -0.5)

    #List containing the antenna loss values to be returned at the end
    ans = []

    #Calculate del x, del y to compute angle off boresight
    del_xy = (20 , (loc*1000) - 3000)

    #Calculate theta for alpha and beta
    
    theta_alpha = (math.acos(np.dot(del_xy, unit_a)/(np.linalg.norm(del_xy)*1)))*180/math.pi
    theta_beta = (math.acos(np.dot(del_xy, unit_b)/(np.linalg.norm(del_xy)*1)))*180/math.pi

    theta_alpha = float (round (theta_alpha))
    theta_beta = float (round (theta_beta))

    global antenna_dict     
    
    ans = [antenna_dict[theta_alpha],antenna_dict[theta_beta]]

    return ans

#Defining a function for printing statistics at the end of each hour

def print_statistics():
    
    print("No. of channels currently in use for sector Alpha: ", 15-nch_alpha)
    print("\nNo. of channels currently in use for sector Beta: ", 15-nch_beta)
    print("\nTotal no. of call attempts at the end of the hour: ", call_count)
    print("\nNo. of Dropped calls due to signal strength for sector alpha: ", len(droppedcall_ssa))
    print("\nNo. of Dropped calls due to signal strength for sector beta: ", len(droppedcall_ssb))   
    print("\nNo. of Blocked calls due to capacity for sector alpha: ", len(blockedcall_capacitya))
    print("\nNo. of Blocked calls due to capacity for sector beta: ", len(blockedcall_capacityb))
    print("\nNo. of Active calls for sector alpha at the end of the hour: ", len(activecalls_a))
    print("\nNo. of Active calls for sector beta at the end of the hour: ", len(activecalls_b))
    print("\nNo. of Successful calls for sector alpha: ", len(successful_callsa))
    print("\nNo. of Successful calls for sector beta: ", len(successful_callsb))
    print("\nNo. of Handoff attempts for Sector alpha: ", len(handoff_attempta))
    print("\nNo. of Handoff attempts for Sector beta: ", len(handoff_attemptb) )
    print("\nNo. of Successful handoffs out of sector alpha: ",len(handoff_successa))
    print("\nNo. of Successful handoffs out of sector beta: ", len(handoff_successb))
    print("\nNo. of Handoff failures out of sector alpha: ", len(handoff_failurea))
    print("\nNo. of Handoff failures out of sector beta: ", len(handoff_failureb))


#Time loop begins..
    
for i in range ((3600*6)+1):

    #User loop begins...
        
    for j in list(user_dict.keys()):

        #USERS WITH AN ACTIVE CALL  <<<<< SECTION 1 >>>>>
        
        active_a = list(activecalls_a.keys())
        active_b = list(activecalls_b.keys())
                
        if j in active_a + active_b: # + operator concatenates the lists to compare.           

            #Updating user's location based on their direction. We assume that 0 indicates users moving North and 1 indicates users moving South.

            if user_dict[j][1] == 0:
                user_dict[j][0] += 0.015  #If user is moving north, increment distance by 15 m

            elif user_dict[j][1] == 1:
                user_dict[j][0] -= 0.015  #If user is moving south, decrement distance by 15 m

            #Decrementing call length by 1 second

            call_length[j] -= 1           

            #Checking if call is completed
            
            if call_length[j] <= 0:
                
                if j in active_a: #CHeck if serving sector is alpha or beta
                    
                    successful_callsa.append(j) #Adding to the list of successful calls for this sector
                    nch_alpha += 1 #Free a chanel on this sector
                    del activecalls_a[j] #Deleting from the active calls list
                    if (user_dict[j][0] >= 6.0 or user_dict[j][0] <= 0): #If user has moved beyond the ends of the road, remove them
                        del user_dict[j]
                        users = npr.uniform(0, 6, size = 1) #Add a new user to replace the one that was removed
                        direction = npr.random_integers(0, 1, size = 1)
                        x = np.column_stack((users, direction))
                        j = [j]
                        user_dict.update(dict(zip(j, x)))

                elif j in active_b:
                    
                    successful_callsb.append(j)
                    nch_beta += 1
                    del activecalls_b[j]
                    if (user_dict[j][0] >= 6.0 or user_dict[j][0] <= 0): #If user has moved beyond the ends of the road, remove them
                        del user_dict[j]
                        users = npr.uniform(0, 6, size = 1)
                        direction = npr.random_integers(0, 1, size = 1)
                        x = np.column_stack((users, direction))
                        j = [j]
                        user_dict.update(dict(zip(j, x)))

            #Checking if users have moved beyond the ends of the road

            elif (user_dict[j][0] >= 6.0 or user_dict[j][0] <= 0):
                
                if j in active_a:  #If serving sector is alpha:
                    successful_callsa.append(j) #Adding to the list of successful calls for this sector
                    nch_alpha += 1  #Freeing a channel on the old sector
                    del activecalls_a[j] #Deleting from the active calls dict.
                    del user_dict[j] #Deleting the user from the main dict., since they have moved out of the roads

                    #If a user is removed from the main dict, add one more user so that there are always 160 users on the road
                    users = npr.uniform(0, 6, size = 1)
                    direction = npr.random_integers(0, 1, size = 1)
                    x = np.column_stack((users, direction))
                    j = [j]
                    user_dict.update(dict(zip(j, x)))
                    

                elif j in active_b: #If serving sector is beta:
                    successful_callsb.append(j)
                    nch_beta += 1
                    del activecalls_b[j]
                    del user_dict[j]
                    users = npr.uniform(0, 6, size = 1)
                    direction = npr.random_integers(0, 1, size = 1)
                    x = np.column_stack((users, direction))
                    j = [j]
                    user_dict.update(dict(zip(j, x)))

            #If not, then calculate the new RSL values and check for potential handoffs
            elif j in list(user_dict.keys()):        

                    antenna_discloss = antenna_discrimination(user_dict[j][0]) #Antenna discrimination loss values are accepted as a list
                    shadowing_value = shadowing(user_dict[j][0])
                    rsl_alpha = eirp - antenna_discloss[0] - hata(user_dict[j][0], f[0]) - shadowing_value + fading() #RSL from Sector alpha
                    rsl_beta = eirp - antenna_discloss[1] - hata(user_dict[j][0], f[1]) - shadowing_value + fading() #RSL from Sector beta
                    
                    #If RSL of server < Threshold, call drops and handoff is not possible

                    if j in active_a: #Checking if user currently belongs to alpha or beta
                        if rsl_alpha < rsl_thresh:
                            droppedcall_ssa.append(j) #Adding to dropped calls due to signal strength for alpha
                            del activecalls_a[j] #Delete from alpha's active calls
                            nch_alpha += 1 #Free up a channel on alpha
         
                    elif j in active_b:
                        if rsl_beta < rsl_thresh:
                            droppedcall_ssb.append(j)
                            del activecalls_b[j]
                            nch_beta += 1

                    #If RSL of server > Threshold, a handoff is possible

                    if j in active_a: #IF currently serving sector is alpha
                        
                        if rsl_alpha >= rsl_thresh and rsl_beta > rsl_alpha + hom: #Checking the condition for handoff
                        
                                handoff_attempta.append(j) #Adding to handoff attempt for alpha
                                
                                if nch_beta > 0: #If channels are available on beta, proceed with the handoff
                                    activecalls_b[j] = i #Adding to
                                    del activecalls_a[j]
                                    nch_alpha += 1
                                    nch_beta -= 1
                                    handoff_successa.append(j)                                   

                                else: #Else, handoff fails for alpha
                                    handoff_failurea.append(j)

                    elif j in active_b: #IF currently serving sector is beta
                        
                        if rsl_beta >= rsl_thresh and rsl_alpha > rsl_beta + hom: #Checking the condition for handoff and do the same as above for beta
                            
                                handoff_attemptb.append(j)
                                
                                if nch_alpha > 0:
                                    activecalls_a[j] = i
                                    del activecalls_b[j]
                                    nch_beta += 1
                                    nch_alpha -= 1
                                    handoff_successb.append(j)

                                else:
                                    handoff_failureb.append(j)

                                    
                                                    
        #USERS WHO DO NOT HAVE AN ACTIVE CALL:    <<<<< SECTION 2 >>>>>

        else: #For users, who don't have an active call, do the following:

            if npr.random_sample() <= (1/1800):  #User will make a call if Probability < (1/1800)              
                   
                    antenna_discloss = antenna_discrimination(user_dict[j][0]) #Antenna discrimination loss values are accepted as a list
                    shadowing_value = shadowing(user_dict[j][0])
                    rsl_alpha = eirp - antenna_discloss[0] - hata(user_dict[j][0], f[0]) - shadowing_value  + fading() #RSL from Sector alpha
                    rsl_beta = eirp - antenna_discloss[1] - hata(user_dict[j][0], f[1]) - shadowing_value + fading() #RSL from Sector beta
                    rsl_server = max (rsl_alpha, rsl_beta)

                    call_count += 1 #Incrementing the call counter object

                    #Using a boolean to check if rsl_server is alpha or beta
                    
                    if rsl_server == rsl_alpha:
                        test = True
                    elif rsl_server == rsl_beta:
                        test = False

                    if rsl_server < rsl_thresh:
                        
                        #Creating a dict of the user ID and the time to be appended to the dropped calls dict
                        if test:
                            droppedcall_ssa.append(j) #Adding user ID to dropped calls dict for sector alpha
                            
                        else:
                            droppedcall_ssb.append(j) #Adding user ID to dropped calls dict for sector beta
                            
                    #IF RSL Server > Threshold, call can be initiated
                            
                    elif rsl_server >= rsl_thresh:
                        
                        if test: #If RSL Server = RSL Alpha
                            
                            if nch_alpha < 1: #If alpha has no available channels
                                
                                blockedcall_capacitya.append(j) #Adding user ID to blocked calls due to capacity for sector alpha
                                
                                if (rsl_beta >= rsl_thresh and nch_beta > 0): #If beta has availble channels and sufficient signal strength
                                    activecalls_b[j] = i #Adding user ID to active calls of beta dict along with the time
                                    call_length[j] = npr.exponential(180) #Call lengths are distributed exponentially with scale factor of 180
                                    nch_beta -= 1 #Beta uses up a channel
                                    
                                    
                            elif nch_alpha >= 1: #If alpha has available channels, do the same as above for alpha
                                activecalls_a[j]=i
                                call_length[j] = npr.exponential(180)
                                nch_alpha -= 1
                               
                                

                        else: #If RSL Server = RSL Beta
                            
                            if nch_beta < 1: #Follow the same procedure as described above
                                
                                blockedcall_capacityb.append(j)
                                

                                if (rsl_alpha >= rsl_thresh and nch_alpha > 0):
                                    activecalls_a[j] = i
                                    call_length[j] = npr.exponential(180)
                                    nch_alpha -= 1
                                    

                            elif nch_beta >= 1:
                                activecalls_b[j] = i
                                call_length[j] = npr.exponential(180)
                                nch_beta -= 1


        
    if(i == 3600*n): #At the end of each hour, print an hourly report
        print('\n\n\nHOURLY REPORT AFTER',n,'HOUR(S)\n')
        print_statistics()
        n+=1
        
