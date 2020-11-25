import argparse
from os import path
import queue
from threading import Thread


#parsing and validation of argument from command line
parser = argparse.ArgumentParser()

def positive_integer(value):
    intvalue = int(value)
    if intvalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive integer value" % value)
    return intvalue

parser.add_argument("-i", "--input", help="path of input file")
parser.add_argument("-o", "--output", help="path of output file")
parser.add_argument("-t", "--thread", type=positive_integer, default=1, help="thread value (default=1)")
args = parser.parse_args()
thread = args.thread
enclosure_queue = queue.Queue() #initialize queue

if not args.input:
    parser.error('Please specify path for an input file with the -i option')

if not args.output:
    parser.error('Please specify path for an output file with the -o option')


#check if input file exists
if path.exists(args.input):
    with open(args.input, 'r') as file:
        input_file = file.read()
else:
    print("Error: Input file or path of input file does not exist.")
    exit()

#check if output file path exists and output file is a file using try catch
#if no error found create file
output = args.output
try:
    #create file
    f = open(output, "w")
except OSError as e:
    print(e)
    exit()

#create matrix function from input file
def create_matrix(input_file):
    #count total number of rows and columns in input file
    read_input = input_file.splitlines()
    no_rows=len(read_input)
    no_cols=len(read_input[0])

    matrix = [['' for _ in range(no_cols)] for _ in range(no_rows)]
    i=0
    for line in read_input:
        j=0
        for c in line:
            matrix[i][j]=c
            j = j+1
        i= i+1

    return matrix

#create starting cellular matrix
starting_cellular = create_matrix(input_file)

#total number of row and col in matrix
no_rows = len(starting_cellular)
no_cols = len(starting_cellular[0])

#temporary matrix for saving each steps simulation
temp_matrix = [['' for _ in range(no_cols)] for _ in range(no_rows)]


# convert matrix to string
def matrix_to_string(matrix):
    s = ""

    for i in range(len(matrix)):
        for j,val in enumerate(matrix[i]):
            s += val
        s+='\n'

    return s

def simulation(q):
    while True:
        result = q.get()
        i = result[0]
        j = result[1]
        global temp_matrix, starting_cellular
        val = starting_cellular[i][j]
        next_val = ''

        # finding neighors coordinates in matrix
        row_down = (i + 1) % no_rows
        col_right = (j + 1) % no_cols

        if i - 1 < 0:
            row_up = no_rows - 1
        else:
            row_up = i - 1 % no_rows

        if j - 1 < 0:
            col_left = no_cols - 1
        else:
            col_left = j - 1 % no_cols

        neighbors_row = [row_up, i, row_down]
        neighbors_col = [col_left, j, col_right]

        count_alive = 0
        for r in neighbors_row:
            for c in neighbors_col:
                if r == i and c == j:
                    continue
                if starting_cellular[r][c] == 'O':
                    count_alive = count_alive + 1

        if val == 'O':
            if count_alive in [2, 3, 4]:
                next_val = 'O'
            else:
                next_val= '.'
        elif val == '.':
            if count_alive > 0 and count_alive % 2 == 0:
                next_val = 'O'
            else:
                next_val = '.'

        temp_matrix[i][j] = next_val
        q.task_done()

#simulator function
def start_simulator():
    global temp_matrix, starting_cellular, thread, enclosure_queue
    # print the project status
    print("Project :: R#\n")
    print("Reading imput from file %s \n" % args.input)

    #print status simulating
    print("Simulating...\n")

    print("Time Step #0")
    print(input_file)
    print('\n')

    # create thread
    for _ in range(thread):
        thread_sim = Thread(target=simulation, args=(enclosure_queue,))
        thread_sim.setDaemon(True)
        thread_sim.start()


    #simulate next 100 steps by checking each cells and its neighbors
    for iteration in range(100):
        for i in range(no_rows):
            for j in range(no_cols):
                enclosure_queue.put([i,j]) #add to queue

        enclosure_queue.join()

        print("Time Step #%d" %(iteration+1))
        print(matrix_to_string(temp_matrix))
        starting_cellular = temp_matrix.copy()
        temp_matrix = [['' for _ in range(no_cols)] for _ in range(no_rows)]

    print("Simulation Complete")
    f = open(output,'w')
    f.write(matrix_to_string(starting_cellular))
    print('The final result is stored in output file %s' % output)

#proceed if no error found
start_simulator()
