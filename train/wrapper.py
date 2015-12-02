from ngram_net import train_ngram_conv_net
from sklearn.cross_validation import train_test_split
from path import Path
from neural_network.non_linear import *
from doc_embedding import *
from io_utils.load_data import *
import numpy as np


def wrapper(data=SST_SENT_POL):
    train_x, train_y, validate_x, validate_y, test_x, test_y = read_matrices_pickle(google=True, data=data, cv=False)
    dim = train_x[0].shape[1]
    print "input data shape", train_x[0].shape
    n_out = len(np.unique(test_y))
    shuffle_indices = np.random.permutation(train_x.shape[0])
    datasets = (train_x[shuffle_indices], train_y[shuffle_indices], validate_x, validate_y, test_x, test_y)
    test_accuracy = train_ngram_conv_net(
        datasets=datasets,
        n_epochs=10,
        ngrams=(2, 2),
        dim=dim,
        ngram_bias=False,
        multi_kernel=True,
        concat_out=False,
        n_kernels=(4, 4),
        use_bias=True,
        lr_rate=0.015,
        dropout=True,
        dropout_rate=0.5,
        n_hidden=400,
        n_out=n_out,
        ngram_activation=leaky_relu,
        activation=leaky_relu,
        batch_size=50,
        update_rule='adagrad'
    )
    return test_accuracy


def wrapper_kaggle(validate_ratio=0.2):
    train_x, train_y, test_x = read_matrices_kaggle_pickle()
    train_x, validate_x, train_y, validate_y = train_test_split(train_x, train_y, test_size=validate_ratio,
                                                                random_state=42, stratify=train_y)
    dim = train_x[0].shape[1]
    n_out = len(np.unique(validate_y))
    datasets = (train_x, train_y, validate_x, validate_y, test_x)

    best_prediction = train_ngram_conv_net(
        datasets=datasets,
        ngrams=(1, 2, 3),
        use_bias=True,
        n_epochs=40,
        ngram_bias=False,
        dim=dim,
        lr_rate=0.05,
        n_out=n_out,
        dropout=True,
        dropout_rate=0.5,
        n_hidden=200,
        activation=leaky_relu,
        ngram_activation=leaky_relu,
        batch_size=100,
        update_rule='adagrad',
        no_test_y=True
    )

    import csv
    save_path = Path('C:/Users/Song/Course/571/hw3/kaggle_result.csv')
    with open(save_path, 'wb') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['PhraseId', 'Sentiment'])
        phrase_ids = np.arange(156061, 222353)
        for phrase_id, sentiment in zip(phrase_ids, best_prediction):
            writer.writerow([phrase_id, sentiment])

if __name__ == '__main__':
    wrapper()
