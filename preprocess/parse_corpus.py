import spacy
import networkx as nx
import argparse
import gzip
import numpy as np
from ufal.udpipe import Model, Pipeline, ProcessingError
import conllu

MAX_PATH_LEN = 11

def main():
    """
    Creates simple paths between target pairs in the dataset.
    :param: -input: a plain-text corpus file
    :param: -pos: part-of-speech of word class which is used to induce patterns (NN | JJ | VB)
            NN: for noun pairs
            JJ: for adjective pairs
            VN: for verb pairs
    Usage: python parse_corpus.py -input <corpus_file> -pos <part-of-speech>
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-input', type=str)
    parser.add_argument('-pos', required=False, type=str)
    parser.add_argument('-dataset', required=False, type=str)
    parser.add_argument('-triples', type=bool)
    parser.add_argument('-lang', type=str)
    args = parser.parse_args()
    
    if args.triples and args.pos is not None:
        raise ValueError("POS argument ignored when parsing triple files")
    elif not args.triples and args.pos is None:
        raise ValueError("POS argument required when parsing regular corpus")
    
    if args.dataset and args.pos is not None:
        raise ValueError("Dataset argument ignored when parsing regular corpus")
    elif not args.triples and args.pos is None:
        raise ValueError("Dataset argument required when parsing triple files")
    
    if args.lang == 'en':
        if args.triples is False:
            nlp = spacy.load("en_core_web_sm")
            with open(args.input, 'rb') as fin:
                with open(args.input  + '_' + args.pos + '_parsed.txt', 'wb') as fout:
                    para_num = 0
                    # Read each paragraph in corpus
                    for paragraph in fin:
                        # Check empty paragraph
                        paragraph = paragraph.strip()
                        if len(paragraph) == 0: continue
                        para_num += 1
                        print('Processing para: %d' %para_num)
                        # Parse each sentence
                        parsed_para = nlp(paragraph.decode("utf-8"))
                        for sent in parsed_para.sents:
                            simple_paths = parse_sentence(sent, args.pos)
                            if len(simple_paths) > 0:
                                fout.write('\n'.join(['\t'.join(path) for path in simple_paths]).encode('utf-8')) 
            print('Parsing done.........!')
        else:
            nlp = spacy.load("en_core_web_sm")
            dataset = []
            with open(args.input, 'rb') as fin:
                with open(args.input  + '_triples_parsed.txt', 'wb') as fout:
                    para_num = 0
                    # Read each paragraph in corpus
                    for triple in fin:
                        # Check empty paragraph
                        triple = triple.decode("utf-8").strip().split("\t")
                        if len(triple) == 0: continue
                        is_ant, word1, word2, sentence = triple
                        para_num += 1
                        print('Processing para: %d' %para_num)
                        # Parse each sentence
                        dataset.append('\t'.join((word1, word2, is_ant)))
                        parsed_para = nlp(sentence)
                        for pos in ("NN", "JJ", "VB"):
                            for sent in parsed_para.sents:
                                simple_paths = parse_sentence(sent, pos)
                                if len(simple_paths) > 0:
                                    fout.write('\n'.join(['\t'.join(path) for path in simple_paths]).encode('utf-8'))
                
                
            np.random.shuffle(dataset)
            train_data = dataset[:int(len(dataset) * 0.7)]
            val_data = dataset[int(len(dataset) * 0.7):int(len(dataset) * 0.85)]
            test_data = dataset[int(len(dataset) * 0.85):]
            for data, data_file in ((train_data, args.dataset + '.train'), (val_data, args.dataset + '.val'), (test_data, args.dataset + '.test')):
                with open(data_file, 'w+') as fout:
                    for triple in data:
                        fout.write(triple + "\n")
    else:
        # yoruba
        model = Model.load('yoruba.udpipe')

        pipeline = Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
        error = ProcessingError()

        dataset = []
        with open(args.input, 'rb') as fin:
            with open(args.input  + '_triples_parsed.txt', 'wb') as fout:
                para_num = 0
                # Read each paragraph in corpus
                for triple in fin:
                    # Check empty paragraph
                    triple = triple.decode("utf-8").strip().split("\t")
                    if len(triple) == 0: continue
                    is_ant, word1, word2, sentence = triple
                    para_num += 1
                    print('Processing para: %d' %para_num)
                    # Parse each sentence
                    dataset.append('\t'.join((word1, word2, is_ant)))
                    parsed_para = pipeline.process(sentence, error)
                    parsed_para = conllu.parse(parsed_para)
                    
                    for pos in ("NOUN", "ADJ", "VERB"):
                        simple_paths = parse_sentence_yo(parsed_para, pos)
                        if len(simple_paths) > 0:
                            fout.write(('\n'.join(['\t'.join(path) for path in simple_paths]) + '\n').encode('utf-8'))
            
        np.random.shuffle(dataset)
        train_data = dataset[:int(len(dataset) * 0.7)]
        val_data = dataset[int(len(dataset) * 0.7):int(len(dataset) * 0.85)]
        test_data = dataset[int(len(dataset) * 0.85):]
        for data, data_file in ((train_data, args.dataset + '.train'), (val_data, args.dataset + '.val'), (test_data, args.dataset + '.test')):
            with open(data_file, 'w+', encoding='utf8') as fout:
                for triple in data:
                    fout.write(triple + "\n")
            
            
        print('Parsing done.........!')
        

def parse_sentence(sent, pos):
    """
    Returns simple paths of pairs corresponding to POS
    :sent: one sentence
    :pos: part-of-speech is used to induce patterns (NN | JJ | VB)
    """
    tokens = []
    edges = {}
    nodes = []
    pos_dict = {}
    dep_dict = {}
    # Get POS tokens
    for token in sent:
        # Adds the index of token to avoid representing many tokens by only one node
        token_with_idx = '#'.join([token_to_lemma(token), str(token.idx)])
        if token.tag_[:2] == pos and len(token.string.strip()) > 2:
            tokens.append(token_with_idx) 
            
        pos_dict[token_with_idx] = token.pos_       
        # Builds edges and nodes for graph
        node = '#'.join([token_to_lemma(token), str(token.idx)])
        head_node = '#'.join([token_to_lemma(token.head), str(token.head.idx)])
        if token.dep_ != 'ROOT': 
            edges[(head_node, node)] = token.dep_ 
            dep_dict[token_with_idx] = token.dep_  
        else:
            dep_dict[node] = 'ROOT'
            
        nodes.append(node)
        
    # Creates word pairs across word classes
    word_pairs = [(tokens[x], tokens[y]) for x in range(len(tokens)-1) 
                  for y in range(x+1,len(tokens))]
    # Finds dependency paths of word pairs
    simple_paths = build_simple_paths(word_pairs, edges, nodes, pos_dict, dep_dict)
    
    return simple_paths

def parse_sentence_yo(parse_data, pos):
    """
    Returns simple paths of pairs corresponding to POS
    :parse_data: results of conllu parse
    :pos: part-of-speech is used to induce patterns (NN | JJ | VB)
    """
    tokens = []
    edges = {}
    nodes = []
    pos_dict = {}
    dep_dict = {}
    
    token_list = parse_data[0]
    # Get POS tokens
    for token in token_list:
        # Adds the index of token to avoid representing many tokens by only one node
        token_with_idx = '#'.join([token['lemma'], str(token['id'])])
        if token['upos'] == pos and len(token['form'].strip()) >= 2:
            tokens.append(token_with_idx) 
            
        pos_dict[token_with_idx] = token['upos']
        # Builds edges and nodes for graph
        node = '#'.join([token['lemma'], str(token['id'])])
        
        if token['deprel'] != 'root':
            if token['head'] is None:
                continue
            head_token = [x for x in token_list if x['id'] == token['head']][0]
            head_node = '#'.join([head_token['lemma'], str(head_token['id'])])
        
            edges[(head_node, node)] = token['deprel']
            dep_dict[token_with_idx] = token['deprel']
        else:
            dep_dict[node] = 'ROOT'
            
        nodes.append(node)
        
    # Creates word pairs across word classes
    word_pairs = [(tokens[x], tokens[y]) for x in range(len(tokens)-1) 
                  for y in range(x+1,len(tokens))]
    # Finds dependency paths of word pairs
    simple_paths = build_simple_paths(word_pairs, edges, nodes, pos_dict, dep_dict)
    
    return simple_paths

def build_simple_paths(word_pairs, edges, nodes, pos_dict, dep_dict):
    """
    Finds the paths of all word pairs in a sentence. Firstly, checks (x,y) or (y,x) in list of target pairs. 
    If 'Yes', finds paths from x to y (y to x).
    :param word_pairs: contains all word pairs in a sentence
    :param edges: edges of the dependency tree in a sentence, using to build graph
    :param nodes: nodes of the dependency tree in a sentence (according to tokens), using to build graph
    :return: list of paths of all word pairs.
    """
    simple_paths = []
    for (x,y) in word_pairs:
        x_token, y_token = x.split('#')[0], y.split('#')[0]
        if x_token != y_token:
            x_to_y_paths = simple_path((x, y), edges, nodes, pos_dict, dep_dict)
            simple_paths.extend([x_token, y_token, ':::'.join(path)] for path in x_to_y_paths if len(path) > 0)
            y_to_x_paths = simple_path((y, x), edges, nodes, pos_dict, dep_dict)
            simple_paths.extend([y_token, x_token, ':::'.join(path)] for path in y_to_x_paths if len(path) > 0)

    return simple_paths

def simple_path(xy, edges, nodes, pos_dict, dep_dict):
    """
    Returns the simple dependency paths between x and y, using the simple paths \
    in the graph of dependency tree.
    :param edges: the edges of the graph
    :param nodes: the nodes of the graph
    :return: the simple paths between x and y in which each node is normalized by lemma/pos/dep/dist
    """
    x, y = xy
    # Gets edges without indices from edges
    edges_with_idx = [k for k in edges.keys()]
    # Builds graph
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges_with_idx)
    # Finds paths from x to y and paths from y to x
    x_to_y_paths = [path for path in nx.all_simple_paths(G,source=x, target=y)]
    y_to_x_paths = [path for path in nx.all_simple_paths(G,source=y, target=x)]
    # Normalizes simple paths
    normalized_simple_paths = []
    for path in x_to_y_paths:
        _paths = simple_path_normalization(path, edges, pos_dict, dep_dict)
        if _paths is not None:
            normalized_simple_paths.append(_paths)
    for path in y_to_x_paths:
        _paths = simple_path_normalization(path, edges, pos_dict, dep_dict)
        if _paths is not None:
            normalized_simple_paths.append(_paths)
    
    return normalized_simple_paths

def simple_path_normalization(path, edges, pos_dict, dep_dict):
    """
    Returns the simple path from x to y
    """
    path_len = len(path)
    if path_len <= MAX_PATH_LEN:
        if path_len == 2:
            x_token, y_token = path[0], path[1]
            if (path[0],path[1]) in edges:
                x_to_y_path = ['X/' + pos_dict[x_token] + '/' + dep_dict[x_token] + '/' + str(0), 
                               'Y/' + pos_dict[y_token] + '/' + dep_dict[y_token] + '/' + str(1)]
            else:
                x_to_y_path = ['X/' + pos_dict[x_token] + '/' + dep_dict[x_token] + '/' + str(1), 
                               'Y/' + pos_dict[y_token] + '/' + dep_dict[y_token] + '/' + str(0)]
        else:
            dist = relative_distance(path, edges)
            x_to_y_path = []
            for idx in range(path_len):
                idx_token = path[idx]
                if idx == 0:
                    source_node = 'X/' + pos_dict[idx_token] + '/' + dep_dict[idx_token] + '/' + str(dist[idx])
                    x_to_y_path.extend([source_node])
                elif idx == path_len - 1:
                    target_node = 'Y/' + pos_dict[idx_token] + '/' + dep_dict[idx_token] + '/' + str(dist[idx])
                    x_to_y_path.extend([target_node])
                else:
                    lemma = idx_token.split('#')[0]
                    node = lemma + '/' + pos_dict[idx_token] + '/' + \
                            dep_dict[idx_token] + '/' + str(dist[idx])
                    x_to_y_path.extend([node])           
        return x_to_y_path if len(x_to_y_path) > 0 else None
    else:
        return None

def relative_distance(path, edges):
    """
    Returns the relative distance between the ancestor node and others
    """
    root_idx = -1
    dist = []
    for idx in range(len(path)-1):
        current_node = path[idx]        
        next_node = path[idx+1]
        if (current_node,next_node) in edges:
            root_idx = idx
            break
    if root_idx == -1:
        for i in range(len(path)):
            dist.append(len(path) - i - 1)
    else:
        for i in range(len(path)):
            dist.append(abs(root_idx-i))
    return dist

def token_to_string(token):
    """
    Converts the token to string representation
    :param token:
    :return: lower string representation of the token
    """
    if not isinstance(token, spacy.tokens.token.Token):
        return ' '.join([t.string.strip().lower() for t in token])
    else:
        return token.string.strip().lower()

def token_to_lemma(token):
    """
    Converts the token to string representation
    :param token: the token
    :return: string representation of the token
    """
    if not isinstance(token, spacy.tokens.token.Token):
        return token_to_string(token)
    else:
        return token.lemma_.strip().lower()

if __name__=='__main__':
    main()   
                    
