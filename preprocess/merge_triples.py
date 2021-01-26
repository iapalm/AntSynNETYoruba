'''
Created on Nov 20, 2020

@author: iapalm
'''

import argparse

def main(syn_file, ant_file, output_file):
    with open(output_file, "w+", encoding="utf8") as fout:
        for i, f in enumerate((syn_file, ant_file)):
            with open(f, "r", encoding="utf8") as fin:
                for line in fin:
                    fout.write("\t".join((str(i), line)))
    print("Done!")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--synfile', type=str, required=True)
    parser.add_argument('--antfile', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    args = parser.parse_args()
    
    main(args.synfile, args.antfile, args.output)