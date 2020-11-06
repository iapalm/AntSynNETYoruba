import pickle
import argparse
from collections import defaultdict
from itertools import count

def main():
    """
    Creates the resource from triplets file
    Usage:
        create_resource.py -input <triplets_file> -freq <frequent_paths_file> -prefix <resource_prefix>

        <triplets_file> = the file that contains text triplets, formated as X \tY \t path
        <frequent_paths_file> = the file containing the frequent paths. It could be created by using 
        the triplet files as follows:
        sort -u <triplets_file> | cut -f3 -d$'\t' > paths
        awk -F$'\t' '{a[$1]++; if (a[$1] == 5) print $1}' paths > frequent_paths
        <resource_prefix> = the file names' prefix for the resource files
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-input', type=str)
    parser.add_argument('-freq', type=str)
    parser.add_argument('-prefix', type=str)
    args = parser.parse_args()
    
    triplets_file = args.input
    frequent_paths_file = args.freq
    resource_prefix = args.prefix
    
    # Load the frequent paths
    with open(frequent_paths_file, 'r') as f:
        frequent_paths = set([line.strip() for line in f])
    print(frequent_paths)
    print('The number of frequent paths: %d' %len(frequent_paths))
    
    paths = list(set(frequent_paths))
    lcount = count(0)
    rcount = count(0)
    left = defaultdict(lambda: next(lcount))
    right = defaultdict(lambda: next(rcount))
    # Load the corpus
    with open(triplets_file, 'rb') as f:
        for line in f:
            line = line.decode("utf-8")
            if len(line.strip().split('\t'))==3:
                l, r, p = line.strip().split('\t')
                left[l]
                right[r]
    print('Read triples successfully!')
          
    entities = list(set(left.keys()).union(set(right.keys())))
    term_to_id = { t : i for i, t in enumerate(entities) }
    path_to_id = { p : i for i, p in enumerate(paths) }

    # Terms
    term_to_id_db = {}
    id_to_term_db = {}
    
    for term, id in term_to_id.items():
        id, term = str(id), str(term)
        term_to_id_db[term] = id
        id_to_term_db[id] = term
    
    pickle.dump(term_to_id_db, open(resource_prefix + '_term_to_id.p', 'wb'))
    pickle.dump(id_to_term_db, open(resource_prefix + '_id_to_term.p', 'wb'))       
    print('Created term databases...')

    # Paths
    path_to_id_db = {}
    id_to_path_db = {}
    
    for path, id in path_to_id.items():
        id, path = str(id), str(path)
        path_to_id_db[path] = id
        id_to_path_db[id] = path
        
    pickle.dump(path_to_id_db, open(resource_prefix + '_path_to_id.p', 'wb'))
    pickle.dump(id_to_path_db, open(resource_prefix + '_id_to_path.p', 'wb'))
    print('Created path databases...')
    
    # Relations
    patterns_db = {}
    num_line = 0

    # Load the triplets file
    edges = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
    print('Creating patterns.... ')
    paths = set(paths)
    with open(triplets_file) as f:
        for line in f:
            try:
                x, y, path = line.strip().split('\t')
            except:
                print(line)
                continue

            # Frequent path
            if path in paths:
                x_id, y_id, path_id = term_to_id.get(x, -1), term_to_id.get(y, -1), path_to_id.get(path, -1)
                if x_id > -1 and y_id > -1 and path_id > -1:
                    edges[x_id][y_id][path_id] += 1

            num_line += 1
            if num_line % 1000000 == 0:
                print('Processed ', num_line, ' lines.')

    for x in edges.keys():
        for y in edges[x].keys():
            patterns_db[str(x) + '###' + str(y)] = ','.join(
                [':'.join((str(p), str(val))) for (p, val) in edges[x][y].items()])
    
    pickle.dump(patterns_db, open(resource_prefix + '_patterns.p', 'wb'))
    print('Done.............!')

if __name__ == '__main__':
    main()
