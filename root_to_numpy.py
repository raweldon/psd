''' Functions for dealing with ttrees'''
import os
import ROOT
import root_numpy
import copy
import numpy as np

def get_ttree(database_dir,run_database,run,root_dir,prefix):
    # get start and stop files
    f = open(database_dir + run_database)
    flag = True
    while flag == True:
        line = f.readline()
        tmp = line.strip()
        if not tmp or tmp[0] != '@':
            continue
        tmp = tmp[1:-1]
        if tmp == run:
            while tmp[0] != '}':
                line = f.readline()
                tmp = line.strip()
                tmp1 = line[0:line.find('=')]
                if tmp1 == 'start':
                    start = line[line.find('=')+1:-1]
                    #print 'start = ', start
                elif tmp1 == 'stop':
                    stop = line[line.find('=')+1:-1]
                    #print 'stop = ', stop
                else:
                    flag = False

    # get files for parsing
    ttrees = os.listdir(root_dir)
    ttrees = sorted(ttrees, key=lambda item: (int(item.partition(' ')[0])
                          if item[0].isdigit() else float('inf'), item))
    print 'get_ttrees.py files to be parsed: '
    flag = True
    i = 0
    data=[]
    while flag == True:
        if ttrees[i] == prefix+start+'.root':
            while ttrees[i] != prefix+stop+'.root':
                print '  ' + str(ttrees[i])
                data.append(ttrees[i])
                i += 1
            print '  ' + str(ttrees[i])
            data.append(prefix+stop+'.root')
            flag = False
        i += 1
    return data

def remove_rec_field(data, name):
    # removes field from record array
    names = list(data.dtype.names) 
    if name in names:
        names.remove(name)
    return data[names] 
  
def sort_array_by_time(data):
    abs_time = data['trig_offset'] + data['trig_time']
    idx = abs_time.argsort()
    data = data[idx]
    return data

def root_to_numpy(root_dir, root_filename, raw_trace):
    ''' convert root file to numpy array and sorts by time
        set raw_trace == True if working with traces
    '''
    root_file = ROOT.TFile(root_dir+root_filename) 
    tree = root_file.Get('event_tree')        
    entries = tree.GetEntries()
    print '\nLOADING DATA'
    print 'Events:', entries
    max_entries = 500000
    lower_bound = [x*max_entries for x in range(int(entries/max_entries))]
    
    if len(lower_bound) == 0:
        lower_bound = [0]
        
    upper_bound = [x+max_entries - 1 for x in lower_bound]
    upper_bound[-1] = entries
    bounds = zip(lower_bound, upper_bound)
        
    array = np.array([])
    for i,bound in enumerate(bounds):
        print bound
        low, high = bound
        if raw_trace == False:    
            array2 = root_numpy.root2array(root_dir+root_filename, 
                                          branches=['det_no', 'phmax', 'qs', 'ql',
                                                    'trig_time', 'trig_offset',
                                                    'blk_transfer_id', 'overlap',
                                                    'in_window', 'saturated', 'baseline',
                                                    'evno'],start=low, stop=high).view(np.recarray)
        else:
            array2 = root_numpy.root2array(root_dir+root_filename, 
                                          branches=['det_no', 'phmax', 'qs', 'ql',
                                                    'trig_time', 'trig_offset',
                                                    'blk_transfer_id', 'overlap',
                                                    'in_window', 'saturated', 'baseline',
                                                    'evno', 'raw_trace_length', 'raw_trace'],start=low, stop=high).view(np.recarray)

        if array.shape[0] == 0:
            array = copy.deepcopy(array2)
        else:
            array = np.concatenate((array, array2))

    print 'array loaded'
    root_file.Close()
    root_file.Clear()

    array = sort_array_by_time(array)
    print 'array sorted by time'
    return array

