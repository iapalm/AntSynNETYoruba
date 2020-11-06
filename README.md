## Distinguishing Antonyms and Synonyms in a Pattern-based Neural Network
Kim Anh Nguyen, nguyenkh@ims.uni-stuttgart.de

Code for paper [Distinguishing Antonyms and Synonyms in a Pattern-based Neural Network](http://www.ims.uni-stuttgart.de/institut/mitarbeiter/anhnk/papers/eacl2017/ant_syn_net.pdf) (EACL 2017).

### Prerequisite
1. [NetworkX](https://networkx.github.io): for creating the tree
2. [spaCy](https://spacy.io): for parsing
3. Theano

### Preprocessing
- Step 1: parse the corpus to create the patterns (```preprocess/parse_corpus.py```)
- Step 2: create the resources which is used to train the model (```preprocess/create_resources.py```)

### Training models

```python train_ant_syn_net.py -corpus <corpus_prefix> -data <dataset_prefix> -emb <embeddings_file> -model <model_name> -iter <iteration>```

in which:
- ```<corpus_prefix>```: the prefix of corpus
- ```<dataset_prefix>```: the prefix of dataset
- ```<embeddings_file>```: the embeddings file
- ```<model_name>```: 1 for training the combined model or 0 for training the pattern-based model
- ```<iteration>```: the number of epoch

### Ian's Notes

How to set the repo up:
1. Clone repo
2. Download GLoVe word embeddings and unzip (I downloaded the Wiki embeddings from https://nlp.stanford.edu/projects/glove/, it's about 1 GB when unzipped)
3. Copy the text file of the corpus you want to use into the project directory
4. `python preprocess/parse_corpus.py -input kjv_medium.txt -pos NN` (`pos` can be NN for noun pairs, JJ for adjective pairs, or VN for verb pairs)
5. `sort -u corpus_NN_parsed.txt | cut -f3 -d$'\t' > paths`
6. `awk -F$'\t' '{a[$1]++; if (a[$1] == 5) print $1}' paths > frequent_paths`
7. `python preprocess\create_dataset.py -input corpus_NN_parsed.txt`
8. `python train_ant_syn_net.py -corpus corpus -data dataset/noun-pairs -emb glove.6B/glove.6B.50d.txt -model 0 -iter 10`





### Reference
```
@InProceedings{nguyen:2017:ant_syn_net
  author    = {Nguyen, Kim Anh and Schulte im Walde, Sabine and Vu, Ngoc Thang},
  title     = {Distinguishing Antonyms and Synonyms in a Pattern-based Neural Network},
  booktitle = {Proceedings of the 15th Conference of the European Chapter of the Association for Computational Linguistics (EACL)},
  year      = {2017},
  address = {Valencia, Spain},
}
```
