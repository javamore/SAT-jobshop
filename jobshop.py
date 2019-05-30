from z3 import *
import itertools

jobs=[]

""
# from https://developers.google.com/optimization/scheduling/job_shop
jobs.append([(0, 3), (1, 2), (2, 2)])
jobs.append([(0, 2), (2, 1), (1, 4)])
jobs.append([(1, 4), (2, 3)])
machines=3
makespan=11


"""
# from http://support.sas.com/documentation/cdl/en/orcpug/63973/HTML/default/viewer.htm#orcpug_clp_sect048.htm
jobs.append([(2,  44),  (3,   5),  (5,  58),  (4,  97),  (0,   9),  (7,  84),  (8,  77),  (9,  96),  (1,  58),  (6,  89)])
jobs.append([(4,  15),  (7,  31),  (1,  87),  (8,  57),  (0,  77),  (3,  85),  (2,  81),  (5,  39),  (9,  73),  (6,  21)])
jobs.append([(9,  82),  (6,  22),  (4,  10),  (3,  70),  (1,  49),  (0,  40),  (8,  34),  (2,  48),  (7,  80),  (5,  71)])
jobs.append([(1,  91),  (2,  17),  (7,  62),  (5,  75),  (8,  47),  (4,  11),  (3,   7),  (6,  72),  (9,  35),  (0,  55)])
jobs.append([(6,  71),  (1,  90),  (3,  75),  (0,  64),  (2,  94),  (8,  15),  (4,  12),  (7,  67),  (9,  20),  (5,  50)])
jobs.append([(7,  70),  (5,  93),  (8,  77),  (2,  29),  (4,  58),  (6,  93),  (3,  68),  (1,  57),  (9,   7),  (0,  52)])
jobs.append([(6,  87),  (1,  63),  (4,  26),  (5,   6),  (2,  82),  (3,  27),  (7,  56),  (8,  48),  (9,  36),  (0,  95)])
jobs.append([(0,  36),  (5,  15),  (8,  41),  (9,  78),  (3,  76),  (6,  84),  (4,  30),  (7,  76),  (2,  36),  (1,   8)])
jobs.append([(5,  88),  (2,  81),  (3,  13),  (6,  82),  (4,  54),  (7,  13),  (8,  29),  (9,  40),  (1,  78),  (0,  75)])
jobs.append([(9,  88),  (4,  54),  (6,  64),  (7,  32),  (0,  52),  (2,   6),  (8,  54),  (5,  82),  (3,   6),  (1,  26)])

machines=10
makespan=842
”“”

#"""
makespan = Int('makespan')

# two intervals must not overlap with each other:
def must_not_overlap (s, i1, i2):
    (i1_begin, i1_end)=i1
    (i2_begin, i2_end)=i2
    s.add(Or(i2_begin>=i1_end, i1_begin>=i2_end))

def all_items_in_list_must_not_overlap_each_other(s, lst):
    # enumerate all pairs using Python itertools:
    for pair in itertools.combinations(lst, r=2):
        must_not_overlap(s, (pair[0][1], pair[0][2]), (pair[1][1], pair[1][2]))

s = Optimize()
s.add(makespan>0) 

# this is placeholder for tasks, to be indexed by machine number:
tasks_for_machines=[[] for i in range(machines)]

# this is placeholder for jobs, to be indexed by job number:
jobs_array=[]

for job in range(len(jobs)):
    prev_task_end=None
    jobs_array_tmp=[]
    for t in jobs[job]:
        machine=t[0]
        duration=t[1]
        # declare Z3 variables:
        begin=Int('j_%d_task_%d_%d_begin' % (job, machine, duration))
        end=Int('j_%d_task_%d_%d_end' % (job, machine, duration))
        # add variables...
        if (begin,end) not in tasks_for_machines[machine]:
            tasks_for_machines[machine].append((job,begin,end))
        if (begin,end) not in jobs_array_tmp:
            jobs_array_tmp.append((job,begin,end))
        # each task must start at time >= 0
        s.add(begin>=0)
        # end time is fixed with begin time:
        s.add(end==begin+duration)
        # no task must end after makespan:
        s.add(end<=makespan)
        # no task must begin before the end of the last task:
        if prev_task_end!=None:
            s.add(begin>=prev_task_end)
        prev_task_end=end
    jobs_array.append(jobs_array_tmp)

# all tasks on each machine must not overlap each other:
for tasks_for_machine in tasks_for_machines:
    all_items_in_list_must_not_overlap_each_other(s, tasks_for_machine)

# all tasks in each job must not overlap each other:
for jobs_array_tmp in jobs_array:
    all_items_in_list_must_not_overlap_each_other(s, jobs_array_tmp)

h = s.minimize(makespan)

if s.check()==unsat:
    print ("unsat")
    exit(0)
s.lower(h)
m=s.model()

text_result=[]

# construct Gantt chart:
ms_long = m[makespan].as_long()
for machine in range(machines):
    st=[None for i in range(ms_long)]
    for task in tasks_for_machines[machine]:
        job=task[0]
        begin=m[task[1]].as_long()
        end=m[task[2]].as_long()
        # fill text string with this job number:
        for i in range(begin,end):
            st[i]=job
    ss=""
    for i,t in enumerate(st):
        ss=ss+("." if t==None else str(st[i]))
    text_result.append(ss)

# we need this juggling to rotate Gantt chart...


print ("machines :",)
for m in range(len(text_result)):
    print (m,)
print ("")
print ("---------")

for time_unit in range(len(text_result[0])):
    print ("time = %3d    :" % (time_unit),)
    for m in range(len(text_result)):
        print (text_result[m][time_unit],)
    print ("")