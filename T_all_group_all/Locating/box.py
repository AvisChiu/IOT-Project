import numpy as np
import threading
import math
import time
from scipy import spatial,stats
import database

db_connect = database.DatabaseConnect()
db_connect.start()

a=14
b=8
c=3
gap=0.1

p_table=[]

print("Initializing P-table")

for x in np.arange(0,a,gap):
	for y in np.arange(0,b,gap):
		for z in np.arange(0,c,gap):
			q=[0,0,0,0]
			q[0] = math.sqrt(x*x+y*y+z*z)
			q[1] = math.sqrt((a-x)*(a-x)+(b-y)*(b-y)+z*z)
			q[2] = math.sqrt((a-x)*(a-x)+y*y+(c-z)*(c-z))
			q[3] = math.sqrt(x*x+(b-y)*(b-y)+(c-z)*(c-z))
			
			p_v = np.array(q)
			p = np.array([x,y,z])
			
			p_table.append({'p': p,'v': p_v})
			
			
#print(p_table)
print("Finished")

def find_thread(dist_dict,dist_lock):
	#global p_table
	while True:
		dist_lock.acquire()
		distance_data = dist_dict.copy()
		dist_lock.release()
		#print("[THRE]	"+str(distance_data))
		#time.sleep(10)
		
		#init data
		q_list=[0,0,0,0]
		q_list[0]=distance_data.get("00:11:32:9D:30:3A")
		q_list[1]=distance_data.get("8C:3B:AD:21:FF:66")
		q_list[2]=distance_data.get("00:11:32:9D:2B:30")
		q_list[3]=distance_data.get("8C:3B:AD:22:02:66")
		
		data_check=True
		
		for x in q_list:
			if x is None:
				data_check=False
				break
		
		if data_check:
			q=np.array(q_list)
			find(q)
		
		else:
			time.sleep(5)
		

def find(q):
	global p_table
	max_score=0
	max_index=-1
	for index, p_data in enumerate(p_table):
		current_score=1 - spatial.distance.cosine(q,p_data['v'])
		if current_score > max_score:
			max_score = current_score
			max_index = index
	
	print(" ")
	print(q)
	print(str(p_table[max_index]['p'])+"	"+str(max_score)+" "+str(p_table[max_index]['v']))
	
	result_point = p_table[max_index]['p']
	
	db_connect.add_loc(float(result_point[0]),float(result_point[1]),float(result_point[2]),'box')
	print(" ")
	
	return max_index
	
def find_test(q):
	global p_table
	p_score=np.zeros(len(p_table))
	for index, p_data in enumerate(p_table):
		#print(str(index)+" "+str(p_data['p']))
		p_score[index]= 1 - spatial.distance.cosine(q,p_data['v'])

	print(p_score)
	#p_rank = stats.rankdata(p_score)
	#
	p_rank = p_score.argsort()[::-1][:10]
	print(p_rank)
	
	for index in p_rank:
		print(str(p_score[index])+" "+str(p_table[index]['p'])+" "+str(p_table[index]['v']))
	


def find_part(q,p_table,s_index,e_index,result_list):
	max_score=0
	max_index=-1
	for index in range(s_index,e_index):
		current_score=1 - spatial.distance.cosine(q,p_table[index]['v'])
		if current_score > max_score:
			max_score = current_score
			max_index = index
	
	result_list.append([max_score,max_index])

def find_multithread(q,p_table,t):
	result_list = []
	thread_list = []
	table_length=len(p_table)
	for i in range(t):
		s_index=math.floor(i*table_length/t)
		e_index=math.floor((i+1)*table_length/t)
		#print("S "+str(s_index)+" E "+str(e_index))
		
		thread_list.append(threading.Thread(target = find_part, args = (q,p_table,s_index,e_index,result_list,)))
		thread_list[i].start()
	
	for i in range(t):
		thread_list[i].join()
	
	max_result = max(result_list)
	max_score = max_result[0]
	max_index = max_result[1]
	print(str(max_score)+" "+str(p_table[max_index]['p'])+" "+str(p_table[max_index]['v']))
	
	return max_result[1]


#test_data=np.array([1,3,3,1])
#find_test(test_data)
#t1 = time.time()
#find(test_data)
#t2 = time.time()
#find_multithread(test_data,p_table,4)
#t3 = time.time()
#print("S "+str(t2-t1)+" M "+str(t3-t2))

#loc = np.array([0.0,0.0,2.9])
#print(p_table[loc])
