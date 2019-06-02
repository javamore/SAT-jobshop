from z3 import *
import itertools


jobs = []
jobs.append([(0, 3), (1, 2), (2, 2)])
jobs.append([(2, 2), (0, 2)])
machines=3

makespan = Int('makespan')

#  tasks can not overlap on machines:
def no_overlap_tasks_machine():
    for tasks_for_machine in tasks_for_machines:
        no_interval_overlap_machine(s, tasks_for_machine)
        
#  tasks can not overlap in each jobs:
def no_overlap_tasks_jobs():
    for jobs_list_tmp in jobs_list:
        no_interval_overlap_jobs(s, jobs_list_tmp)

#  intervals can not overlap:
def no_interval_overlap (s, i1, i2):
    (i1_begin, i1_end) = i1
    (i2_begin, i2_end) = i2
    s.add(Or(i2_begin >= i1_end, i1_begin >= i2_end))
    
#  items can not overlap:
def no_items_overlap (s, lst):
    for pair in itertools.combinations(lst, r = 2):
        no_interval_overlap(s, (pair[0][1], pair[0][2]), (pair[1][1], pair[1][2]))

        
sol = Optimize()
sol.add(makespan > 0) 


tasks_for_machines = [[] for i in range(machines)]

jobs_list = []


for job in range(len(jobs)):
    former_task_end = None
    jobs_list_tmp = []

    for t in jobs[job]:
        machine = t[0]
        time_used = t[1]

        #variables:
        begin = Int('j_%d_task_%d_%d_begin' % (job, machine, time_used))
        end = Int('j_%d_task_%d_%d_end' % (job, machine, time_used))

        if (begin,end) not in tasks_for_machines[machine]:
            tasks_for_machines[machine].append((job,begin,end))
        if (begin,end) not in jobs_list_tmp:
            jobs_list_tmp.append((job,begin,end))

        # task start from time >= 0
        sol.add(begin >= 0)

        # end time is fixed with begin time:
        sol.add(end == begin+time_used)

        # no task must end after makespan:
        sol.add(end <= makespan)

        # no task begin before the last task end:
        if former_task_end != None:
            sol.add(begin >= former_task_end)
        former_task_end = end

    jobs_list.append(jobs_list_tmp)


h = sol.minimize(makespan)

if sol.check() == unsat:
    print ("unsat")
    exit(0)
sol.lower(h)
m = sol.model()

result = []

# construct Gantt chart:
ms_long = m[makespan].as_long()
for machine in range(machines):
    st = [None for i in range(ms_long)]
    for task in tasks_for_machines[machine]:
        job = task[0]
        begin = m[task[1]].as_long()
        end = m[task[2]].as_long()
        # fill text string with this job number:
        for i in range(begin,end):
            st[i] = job
    ss = ""
    for i,t in enumerate(st):
        ss = ss+("." if t == None else str(st[i]))
    result.append(ss)

print ("Machines Used :")
for m in range(len(result)):
    print (m)
print ("")
print ("Below is the optimal makespan:")

for time_unit in range(len(result[0])):
    print ("Time Schedule =%3d:        " % (time_unit))
    for m in range(len(result)):
        print (result[m][time_unit], end = "\t")
    print (" ")
