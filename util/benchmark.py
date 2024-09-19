# we want to benchmark our AI engines and give a final score based on a weighted total

# the categories are as follows:
# 1. overall word accuracy (75%)
# 2. minimum character accuracy (15%)
# 3. time taken to process all students (10%)

import time

time_start = 0
num_students = 0

def start_benchmark():
    global time_start, num_students
    time_start = time.time()
    num_students = 0
    
def banchmark_started():
    return time_start != 0

def add_student():
    global num_students
    num_students += 1

def get_final_score(word_accuracy, char_accuracy):
    # calculate the time taken to process all students
    time_end = time.time()
    time_taken = time_end - time_start
    
    time_per_student = time_taken / num_students
    
    time_taken = 1 / (time_taken * 100)
    
    print(f'Time per student: {round(time_per_student, 3)}s')
    print(f'Calculated time taken: {round(time_taken, 3)}')
    
    return ((word_accuracy * 0.75) + (char_accuracy * 0.15) + (time_taken * 0.10)) * 10.0