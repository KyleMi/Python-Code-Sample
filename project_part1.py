import numpy as np

def read_file(filename):
	fl = open(filename)
	flg = 0
	#graph = Graph()
	arc_dic = {}
	var_time = {}
	values_ls = []
	ddl_constraint = 0
	unary_inclusive ={}
	unary_exclusive = {}
	binary_equal = {}
	binary_n_equal = {}
	binary_n_sim = []
	for line in fl:
		line = line.rstrip()
		if "#" in line and "variables" in line:
			flg = 1
		elif "#" in line and "values" in line:
			flg = 2 
		elif "#" in line and "deadline" in line:
			flg = 3
		elif "#" in line and "unary inclusive" in line:
			flg = 4 
		elif "#" in line and "unary exclusive" in line:
			flg = 5
		elif "#" in line and "binary equals" in line:
			flg = 6 
		elif "#" in line and "binary not equals" in line:
			flg = 7 
		elif "#" in line and "binary not simultaneous" in line:
			flg = 8

		if "#" in line:
			continue
		#variables
		if flg == 1:
			temp = line.split(" ")
			# node = Variable(temp[0])
			# node.set_time = int(temp[1])
			
			var_time[temp[0]] = int(temp[1])
		#values
		elif flg == 2:
			values_ls.append(line)
		elif flg == 3:
			ddl_constraint = int(line)
		elif flg == 4:
			temp = line.split(" ")
			unary_inclusive[temp[0]] = temp[1:]
		elif flg == 5:
			temp = line.split(" ")
			unary_exclusive[temp[0]] = temp[1:]
		elif flg == 6:
			temp = line.split(" ")
			if temp[0] not in binary_equal:
				binary_equal[temp[0]] = [temp[1]]
			else:
				binary_equal[temp[0]].append(temp[1])
			if temp[1] not in binary_equal:
				binary_equal[temp[1]] = [temp[0]]
			else:
				binary_equal[temp[1]].append(temp[0])

		elif flg == 7:
			temp = line.split(" ")
			if temp[0] not in binary_n_equal:
				binary_n_equal[temp[0]] = [temp[1]]
			else:
				binary_n_equal[temp[0]].append(temp[1])
			if temp[1] not in binary_n_equal:
				binary_n_equal[temp[1]] = [temp[0]]
			else:
				binary_n_equal[temp[1]].append(temp[0])
		elif flg == 8:
			temp = line.split(" ")
			temp_dic = {}
			temp_dic[temp[0]] = temp[2]
			temp_dic[temp[1]] = temp[3]
			binary_n_sim.append(temp_dic)

	for key in var_time:
		if key in unary_inclusive:
			arc_dic[key] = unary_inclusive[key]
		else:
			arc_dic[key] = values_ls
		if key in unary_exclusive:
			arc_dic[key] = [item for item in values_ls if item not in unary_exclusive[key]]

	return values_ls,var_time,arc_dic,ddl_constraint,binary_equal,binary_n_equal,binary_n_sim

def build_constrain_mtx(values_ls,arc_dic,binary_equal,binary_n_equal,binary_n_sim):
	result = {}
	#C
	for key1 in arc_dic:
		temp = {}
		#A
		for key2 in arc_dic:
			if key1 == key2:
				continue
			matrix = []
			#row  C value == q
			for r_value in values_ls:
				#row  C value == q
				#column G value == p
				row = []
				for c_value in values_ls:
					if r_value not in arc_dic[key1] or c_value not in arc_dic[key2]:
						row.append(0)
						continue
					#binary equal C G
					if key1 in binary_equal and key2 in binary_equal[key1]:
						if r_value != c_value:
							row.append(0)
							continue
					#bianry not equal C G
					if key1 in binary_n_equal and key2 in binary_n_equal[key1]:
						if r_value == c_value:
							row.append(0)
							continue
					flg = False
					# if key1 and key2 not satisfies one not simultaneous case add 0
					
					for not_sim_case in binary_n_sim:
						if key1 in not_sim_case and key2 in not_sim_case:
							if r_value == not_sim_case[key1] and c_value == not_sim_case[key2]:
								row.append(0)
								flg = True
								break
					if flg == False:
						row.append(1)
				matrix.append(row)
			temp[key2] = matrix
		result[key1] = temp
	return result

def BACKTRACKING_SEARCH(csp,values_ls,arc_dic,binary_equal,binary_n_equal,binary_n_sim):
    return BACKTRACK([],csp,values_ls,arc_dic,binary_equal,binary_n_equal,binary_n_sim)

def BACKTRACK(assignment,csp,values_ls,arc_dic,binary_equal,binary_n_equal,binary_n_sim):
    
    if len(assignment)==len(csp):
        return assignment
    var=select_unassigned_variable(assignment,csp,arc_dic,binary_equal,binary_n_equal,binary_n_sim)
    print('we selected variable',var)
    for value in order_domain_values(var,assignment,csp):
        print('we selected value',values_ls[value])
        if check_consistent(var,value,assignment,csp):
            assignment.append([var,value])
            #print('BT assignment is ',assignment)
            inference=ARC(assignment,csp,var,value )
            if inference!='failure':
                #assignment.append(inference)
                result=BACKTRACK(assignment,csp,values_ls,arc_dic,binary_equal,binary_n_equal,binary_n_sim)
                if result!='failure':
                    return result
                
            assignment.pop(-1)
            print('Even the variable',var,'with value',value,'is legal itself,\
                  we cannot get a solution with this assignment, so we need to \
                  backtrack')
        #assignment.remove(inference)
    return 'failure'

def select_unassigned_variable(assignment,csp,arc_dic,binary_equal,binary_n_equal,binary_n_sim):
    unassigned_var=list(csp.keys())
    for var in assignment:
        unassigned_var.remove(var[0])
    remaining_value=[]
    for var in unassigned_var:
        remaining=check_availability(var,assignment,csp)
        remaining_value.append(sum(remaining))
    #print(remaining_value)
    
    if remaining_value.count(min(remaining_value))>1:
        same_MRV_variable=[]
        degree=[]
        count_constrain=cnt_constraint(assignment,arc_dic,binary_equal,binary_n_equal,binary_n_sim)
        for i in range(remaining_value.count(min(remaining_value))):
            same_MRV_index=remaining_value.index(min(remaining_value))
            remaining_value.remove(remaining_value[same_MRV_index])
            same_MRV_variable.append(unassigned_var[same_MRV_index])
            unassigned_var.pop(same_MRV_index)
            degree.append(count_constrain[same_MRV_variable[-1]])
        sorteddegree,sortedvariable=l2s_sortfunction(degree,same_MRV_variable)
        #print('###########################')
        #print(sorteddegree,sortedvariable)
        return sortedvariable[0]
    else:
        return unassigned_var[remaining_value.index(min(remaining_value))]

def check_availability(var,assignment,csp):
    remaining=np.ones(len(csp[var][list(csp[var].keys())[0]]))
    unassignment=list(csp[var].keys())
    # check remaining value from assignment 
    for assigned_var in assignment:
        remaining2=[]
        if var==assigned_var[0]:
            alreadyassigned=np.zeros(len(csp[var][list(csp[var].keys())[0]]))
            alreadyassigned[int(assigned_var[1])]=alreadyassigned[int(assigned_var[1])]+1
            return alreadyassigned
        if assigned_var[0] in unassignment:
            unassignment.remove(assigned_var[0])
        if assigned_var[0] in csp[var].keys():
           
            for i in range(len(csp[var][assigned_var[0]])):
                remaining2.append(csp[var][assigned_var[0]][i][assigned_var[1]])
            remaining=remaining*np.array(remaining2)
        #check remaining value from unassignment
    for unassign_var in unassignment:
        remaining2=[]            
        for i in range(len(csp[var][list(csp[var].keys())[0]])):
            if sum(csp[var][unassign_var][i])>0:
                remaining2.append(1)
            else:
                remaining2.append(0)
        remaining=remaining*np.array(remaining2)    
    return remaining

def order_domain_values(var,assignment,csp):
    possible_value=check_availability(var,assignment,csp)
    value_number=[]
    for i in range(len(possible_value)):
        if possible_value[i]==1:
            value_number.append(i)
    flexibility=[]
    for value in value_number:
        f=0
        assignment.append([var,value])
        for keys in list(csp[var].keys()):
            f=f+sum(check_availability(var,assignment,csp))
        flexibility.append(f)
        assignment.pop(-1)
    flexibility,value_number=l2s_sortfunction(flexibility,value_number)
    return list(value_number)

def l2s_sortfunction(g,queue):
    i=0
    while i<len(queue)-1:
        if g[i]<g[i+1]:
            g[i],g[i+1]=g[i+1],g[i]
            queue[i],queue[i+1]=queue[i+1],queue[i]
            i=0
        else:
            i+=1
    return g,queue

def check_consistent(var,value,assignment,csp):
    legal_value=check_availability(var,assignment,csp)
    value_number=[]
    for i in range(len(legal_value)):
        if legal_value[i]==1:
            value_number.append(i)
    if value in value_number:
        return 1
    else:
        return 0


def ARC(assignment,csp,var,value ):
    queue=[]
    for keys in list(csp.keys()):
        for subkeys in list(csp[keys].keys()):
            queue.append([keys,subkeys])
    #print(queue[0])
    Domain={}
    for Xi in list(csp.keys()):
        Di=[]
        
        for i in range(len(check_availability(Xi,assignment,csp))):
            if check_availability(Xi,assignment,csp)[i]==1:
                Di.append(i)
        Domain[Xi]=Di
        #print(Domain)
    while len(queue)>0:
        Xi,Xj=queue.pop(0)
        if REVISE(assignment,csp,Xi,Xj,Domain[Xi]) :
            if len(Domain[Xi])==0 :
                print('?????????????')
                return 'failure'                
            for Xk in list(csp[Xi].keys()):
                queue.insert(0,[Xk,Xi])
    return 'true'
#[['SA', 0], ['NT', 2]]
def  REVISE(assignment,csp,Xi,Xj,Di):
    revised=0
    for value in Di:
        assignment.append([Xi,value])
        if sum(check_availability(Xj,assignment,csp))==0:
            Di.remove(value)
            revised=1
#            print(Xi,'is',value,'and there is no value legal for ',Xj)
        assignment.pop(-1)
    return revised

def number2value(values_ls,result):
    for i in range(len(result)):
        result[i][1]=values_ls[result[i][1]]
    return result


def cnt_constraint(assignment,arc_dic,binary_equal,binary_n_equal,binary_n_sim):
    flag=0
    if len(assignment) == 0:
        assignment.append([0,0])
        flag=1
    assigned_ls = [v[0] for v in assignment]
    result = {}
    for var in arc_dic:
        if var in assigned_ls:
            continue
        var_degree = 0
        if var in binary_equal:
            var_degree += len(binary_equal[var]) - len(intersection(binary_equal[var],assigned_ls))
        if var in binary_n_equal:
            var_degree += len(binary_n_equal[var]) - len(intersection(binary_n_equal[var],assigned_ls))
        for case in binary_n_sim:
            if var in case:
                temp = list(case.keys())
                temp.remove(var)
                if temp[0] not in assigned_ls:
                    var_degree += 1
        result[var] = var_degree
    if flag== 1:
        assignment.remove([0,0])
    return result

def intersection(ls1, ls2): 
    result = [value for value in ls1 if value in ls2] 
    return result

def main():
    fn = "input2.txt"
    values_ls,var_time,arc_dic,deadline,binary_equal,binary_n_equal,binary_n_sim = read_file(fn)
    csp=build_constrain_mtx(values_ls,arc_dic,binary_equal,binary_n_equal,binary_n_sim)
    #BACKTRACKING_SEARCH(csp)
    result=BACKTRACKING_SEARCH(csp,values_ls,arc_dic,binary_equal,binary_n_equal,binary_n_sim)
    if result!='failure':
        result=number2value(values_ls,result)
    print(result)

if __name__ == "__main__":
	main()