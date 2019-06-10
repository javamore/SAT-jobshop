from z3 import *
import itertools

jobs = []
jobs.append([(4,  15),  (5,  31),  (1,  87),  (2,  57),  (0,  77),  (3,  85)])
jobs.append([(5,  82),  (2,  22),  (4,  10),  (3,  70),  (1,  49),  (0,  40)])
jobs.append([(1,  91),  (2,  17),  (3,  62),  (5,  75),  (0,  47),  (4,  11)])
jobs.append([(4,  71),  (1,  90),  (3,  75),  (0,  64),  (2,  94),  (5,  15)])
jobs.append([(1,  70),  (5,  93),  (0,  77),  (2,  29),  (4,  58),  (3,  93)])
jobs.append([(0,  87),  (1,  63),  (4,  26),  (5,   6),  (2,  82),  (3,  27)])
machines=6
makespan = Int('makespan')
        
sol = Optimize()
sol.add(makespan > 0)
 
tasks_machines = [[] for i in range(machines)]
jobs_list = []

#  items can not overlap:
def no_items_overlap (s, lst):
    for pair in itertools.combinations(lst, r = 2):
        no_interval_overlap(s, (pair[0][1], pair[0][2]), (pair[1][1], pair[1][2]))

#  intervals can not overlap:
def no_interval_overlap (s, i1, i2):
    (i1_begin, i1_end) = i1
    (i2_begin, i2_end) = i2
    s.add(Or(i1_begin >= i2_end, i1_end <= i2_begin))
    
for job in range(len(jobs)):
    former_task_end = None
    jobs_list_tmp = []

    for t in jobs[job]:
        machine = t[0]
        time_used = t[1]
        #set  variables:
        begin = Int('j_%d_task_%d_%d_begin' % (job, machine, time_used))
        end = Int('j_%d_task_%d_%d_end' % (job, machine, time_used))
        
        #check whether it is avaliable to add tasks
        if (begin,end) not in tasks_machines[machine]:
            tasks_machines[machine].append((job,begin,end))

        #check whether it is avaliable to add jobs        
        if (begin,end) not in jobs_list_tmp:
            jobs_list_tmp.append((job,begin,end))

        # task start from time >= 0
        sol.add(begin >= 0)

        # no task end after makespan:
        sol.add(end <= makespan)

        # end time is fixed with begin time:
        sol.add(end == begin+time_used)

        # no task begin before the last task end:
        if former_task_end != None:
            sol.add(begin >= former_task_end)
        former_task_end = end
    jobs_list.append(jobs_list_tmp)

# no tasks overlap on machines:
for tasks_for_machine in tasks_machines:
    no_items_overlap(sol, tasks_for_machine)
        
# no tasks overlap on each jobs:
for jobs_list_tmp in jobs_list:
    no_items_overlap(sol, jobs_list_tmp)


min = sol.minimize(makespan)

#unknown = CheckSatResult(Z3_L_UNDEF)
if sol.check() == unknown:
    print ("the result is unknown")
    exit(0)

#sat = CheckSatResult(Z3_L_TRUE)
#unsat = CheckSatResult(Z3_L_FALSE)
elif sol.check() == unsat:
    print ("the result is unsat")
    exit(0)

#sol.lower is to check&ensure result returned by maximize/minimize 
sol.lower(min)

#m_sol is to return optimized machine using schedule
m_sol = sol.model()

result = []

# construct Gantt chart:
ms_long = m_sol[makespan].as_long()
for machine in range(machines):
    st = [None for i in range(ms_long)]
    for task in tasks_machines[machine]:
        job = task[0]
        begin = m_sol[task[1]].as_long()
        end = m_sol[task[2]].as_long()
        for i in range(begin,end):
            st[i] = job
    ss = ""
    for i,t in enumerate(st):
        #'*' means not used at that time
        ss = ss+("*" if t == None else str(st[i]))
    result.append(ss)

print ("Machines Used :")
for m_sol in range(len(result)):
    print (m_sol)
print ("")

print ("Below is the optimal schedule:")
for time_unit in range(len(result[0])):
    print ("Time = %3d:        " % (time_unit))
    for m_sol in range(len(result)):
        print (result[m_sol][time_unit], end = "\t")
        print ("")
    print (" ")