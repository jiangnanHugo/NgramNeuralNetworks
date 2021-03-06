import numpy as np
from nltk.collocations import ngrams

from io_utils.load_data.load_yelp import read_train_data, read_test_data
from io_utils.load_vector_model import read_glove_model


def get_bigram_review_vector(text, model, average=True, kernel=(1, 1)):
    bigrams = ngrams(text, 2)
    vector = np.zeros(model.vector_size)
    count = 0
    for bigram in bigrams:
        bigram_vector = np.zeros(model.vector_size)
        if bigram[0] in model:
            bigram_vector += model[bigram[0]] * kernel[0]
        if bigram[1] in model:
            bigram_vector += model[bigram[1]] * kernel[1]
        count += 1
        vector += bigram_vector
    if average and count > 0:
        vector /= count
    return vector


def get_reviews_vectors(documents, model, average=True, kernel=(1, 1)):
    for i in xrange(len(documents)):
        documents[i] = get_bigram_review_vector(documents[i], model, average, kernel=kernel)
    return documents


def get_naive_bigram_vectors(average=True, int_label=True, dim=300, kernel=(1, 1)):
    model = read_glove_model(dim=dim)
    train_x, train_y, validate_x, validate_y = read_train_data(int_label=int_label)
    test_x, test_y = read_test_data(int_label=int_label)
    print "getting bigram word vectors for documents..."
    train_x = get_reviews_vectors(train_x, model, average=average, kernel=kernel)
    validate_x = get_reviews_vectors(validate_x, model, average=average, kernel=kernel)
    test_x = get_reviews_vectors(test_x, model, average=average, kernel=kernel)
    return train_x, train_y, validate_x, validate_y, test_x, test_y


if __name__ == '__main__':
    train_x, train_y, validate_x, validate_y, test_x, test_y = get_naive_bigram_vectors()
    print test_x[0]
    print np.asarray(test_x).shape
    print test_y
