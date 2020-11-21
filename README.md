## Distinguishing Antonyms and Synonyms in a Pattern-based Neural Network
Kim Anh Nguyen, nguyenkh@ims.uni-stuttgart.de

Code for paper [Distinguishing Antonyms and Synonyms in a Pattern-based Neural Network](http://www.ims.uni-stuttgart.de/institut/mitarbeiter/anhnk/papers/eacl2017/ant_syn_net.pdf) (EACL 2017).

### Ian's Notes

#### Installation + setup
1. Create an anaconda environment
2. Conda requirements:
- `conda install theano` then `conda install -c mila-udem pygpu` NOTE: these *cannot* be installed via pip - the pip wheel is outdated
- Install [CUDA 10.1](https://developer.nvidia.com/cuda-10.1-download-archive-base)
- Restart your computer (or otherwise ensure `CUDA_PATH` is set)
- `conda install numpy scipy mkl-service libpython m2w64-toolchain nose sphinx`
3. Download GLoVe word embeddings and unzip (I downloaded the Wiki embeddings from https://nlp.stanford.edu/projects/glove/, it's about 1 GB when unzipped)
4. Clone the repo and proceed to the next section

####To train using their original method:
1. Create a directory for the corpus you want to train on
2. Copy the text file of the corpus you want to use into the project directory
3. `python preprocess/parse_corpus.py -input path_to/your_text_file.txt -pos NN` (`pos` can be `NN` for noun pairs, `JJ` for adjective pairs, or `VB` for verb pairs)
- This will produce a `path_to/your_text_file.txt_POS_parsed.txt` file with all of the tokens and paths
4. `cd path_to; sort -u your_text_file_POS_parsed.txt | cut -f3 -d$'\t' > paths`
5. `awk -F$'\t' '{a[$1]++; if (a[$1] == 5) print $1}' paths > frequent_paths`
- Modify the 5 to whatever threshold you want
6. `cd ..`
6. `python preprocess/create_resources.py -input path_to/your_text_file_POS_parsed.txt -freq path_to/frequent_paths -prefix path_to/your_text_file`
7. `python train_ant_syn_net.py -corpus path_to/your_text_file -data dataset/POS-pairs -emb glove.6B/glove.6B.50d.txt -model 0 -iter 10`
- This runs 10 epochs of training.  Set `POS` to `NN`, `JJ`, or `VB`, depending on what you chose earlier.

####To train using our new method:
1. Create a directory for the corpus you want to train on
2. Copy the text files (one for synonyms, one for antonyms) of the *triples* you want to use into the project directory
- See the `kjv_yor` directory for an example
3. `python preprocess\merge_triples.py --synfile kjv_yor/en-synonym-sentences.txt --antfile kjv_yor/en-antonym-sentences.txt --output kjv_yor/en-all-sentences.txt` to merge the files into one
4. `python preprocess/parse_corpus.py -input kjv_yor/en-all-sentences.txt -triples True -dataset kjv_yor/pairs`
5. `cd kjv_yor; sort -u en-all-sentences.txt_triples_parsed.txt | cut -f3 -d$'\t'`
6. `awk -F$'\t' '{a[$1]++; if (a[$1] == 1) print $1}' paths > frequent_paths`
7. `cd ..`
8. `python preprocess/create_resources.py -input kjv_yor/en-all-sentences.txt_triples_parsed.txt -freq kjv_yor/frequent_paths -prefix kjv_yor/en-all-sentences.txt`
9.  `python train_ant_syn_net.py -corpus kjv_yor/en-all-sentences.txt -data kjv_yor/pairs -emb glove.6B/glove.6B.50d.txt -model 0 -iter 10`
10. Watch it train!


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
