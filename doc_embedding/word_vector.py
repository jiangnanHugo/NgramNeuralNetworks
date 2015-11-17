import cPickle as pkl
import numpy as np
from utils.load_data import *
from utils.load_vector_model import read_glove_model, read_google_model
from path import Path

max_count = 0


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def get_document_matrix(text, model, cutoff=300, uniform=True, scale=0.1, shrink=True):
    matrix = None
    rand_vector = np.random.uniform(-scale, scale, model.vector_size) if uniform \
        else np.random.normal(0, scale, model.vector_size)
    count = 0
    if shrink and len(text) > cutoff:
        shrink_size = int(round(len(text) / float(cutoff) + 0.4))
        word_chunks = chunks(text, shrink_size)
        for chunk in word_chunks:
            avg_vector = np.zeros(model.vector_size)
            for word in chunk:
                word_vector = model[word] if word in model else rand_vector
                avg_vector += word_vector
            avg_vector /= len(chunk)
            if matrix is None:
                matrix = np.asarray([avg_vector])
            else:
                matrix = np.concatenate((matrix, [avg_vector]))
    else:
        for word in text:
            word_vector = model[word] if word in model else rand_vector
            if matrix is None:
                matrix = np.asarray([word_vector])
            else:
                matrix = np.concatenate((matrix, [word_vector]))
            count += 1
            if count >= cutoff:
                break

    if matrix is None:
        return np.zeros((cutoff, model.vector_size))
    length = matrix.shape[0]
    if length < cutoff:
        padding = np.zeros((cutoff - length, model.vector_size))
        matrix = np.concatenate((matrix, padding))
    elif length > cutoff:
        matrix = matrix[:cutoff]
    return matrix


def get_review_vector(text, model, average=True):
    count = 0
    vector = np.zeros(model.vector_size)
    for word in text:
        count += 1
        if word in model:
            vector += model[word]
    if average and len(text) > 0:
        vector /= len(text)
    global max_count
    if count > max_count:
        max_count = count
    return vector


def get_reviews_vectors(documents, model, average=True, aggregate=True, cutoff=300, uniform=True):
    for i in xrange(len(documents)):
        if aggregate:
            documents[i] = get_review_vector(documents[i], model, average)
        else:
            documents[i] = get_document_matrix(documents[i], model, cutoff=cutoff, uniform=uniform)
    return documents


def get_aggregated_vectors(average=True, int_label=True, dim=300):
    model = read_glove_model(dim=dim)
    train_x, train_y, validate_x, validate_y = read_train_data(int_label=int_label)
    test_x, test_y = read_test_data(int_label=int_label)
    print "getting aggregate word vectors for documents..."
    train_x = get_reviews_vectors(train_x, model, average)
    validate_x = get_reviews_vectors(validate_x, model, average)
    test_x = get_reviews_vectors(test_x, model, average)
    return train_x, train_y, validate_x, validate_y, test_x, test_y


def get_document_matrices(google=False, dim=300, cutoff=60, uniform=True, data='rotten', cv=True):
    print "getting concatenated word vectors for documents..."
    model = read_google_model() if google else read_glove_model(dim=dim)
    if cv:
        if data == 'rotten':
            x, y = read_rotten_pickle()
            cutoff = 56
        elif data == 'subj':
            x, y = read_subj_pickle()
        elif data == 'cr':
            x, y = read_cr_pickle()
        elif data == 'mpqa':
            x, y = read_mpqa_pickle()
            cutoff = 20
        else:
            raise NotImplementedError('Not such data set %s', data)
        x = get_reviews_vectors(x, model, aggregate=False, cutoff=cutoff, uniform=uniform)
        x = np.asarray(x)
        y = np.asarray(y)
        return x, y
    else:
        if data == 'imdb':
            train_x, train_y, validate_x, validate_y, test_x, test_y = read_imdb_pickle()
            cutoff = 75
        elif data == 'sst_sent':
            train_x, train_y, validate_x, validate_y, test_x, test_y = read_sst_sent_pickle()
        elif data == 'trec':
            train_x, train_y, validate_x, validate_y, test_x, test_y = read_trec_pickle()
            cutoff = 50
        else:
            raise NotImplementedError('Not such data set %s', data)
        train_x = get_reviews_vectors(train_x, model, aggregate=False, cutoff=cutoff, uniform=uniform)
        validate_x = get_reviews_vectors(validate_x, model, aggregate=False, cutoff=cutoff, uniform=uniform)
        test_x = get_reviews_vectors(test_x, model, aggregate=False, cutoff=cutoff, uniform=uniform)

        train_x = np.asarray(train_x)
        train_y = np.asarray(train_y)
        validate_x = np.asarray(validate_x)
        validate_y = np.asarray(validate_y)
        test_x = np.asarray(test_x)
        test_y = np.asarray(test_y)

        return train_x, train_y, validate_x, validate_y, test_x, test_y


def get_document_matrices_yelp(google=False, int_label=True, dim=50, cutoff=300, uniform=True, for_theano=True):
    model = read_google_model() if google else read_glove_model(dim=dim)
    train_x, train_y, validate_x, validate_y = read_train_data(int_label=int_label)
    test_x, test_y = read_test_data(int_label=int_label)
    print "getting concatenated word vectors for documents..."
    train_x = get_reviews_vectors(train_x, model, aggregate=False, cutoff=cutoff, uniform=uniform)
    validate_x = get_reviews_vectors(validate_x, model, aggregate=False, cutoff=cutoff, uniform=uniform)
    test_x = get_reviews_vectors(test_x, model, aggregate=False, cutoff=cutoff, uniform=uniform)

    if for_theano:
        train_y = np.asarray(train_y) - 1
        validate_y = np.asarray(validate_y) - 1
        test_y = np.asarray(test_y) - 1

    return train_x, train_y, validate_x, validate_y, test_x, test_y


def save_matrices_pickle(google=True, data='rotten', cv=True):
    path = 'D:/data/nlpdata/pickled_data/'
    filename = data + '_google.pkl' if google else data + '_glove.pkl'
    filename = Path(path + filename)
    print 'saving data to %s...' % filename
    f = open(filename, 'wb')
    if cv:
        x, y = get_document_matrices(google=google, dim=300, data=data)
        print len(x)
        pkl.dump((x, y), f, -1)
    else:
        train_x, train_y, validate_x, validate_y, test_x, test_y = get_document_matrices(google=google, data=data, cv=False)
        if data == 'imdb':
            np.savez(f, train_x)
        pkl.dump((train_x, train_y), f, -1)
        pkl.dump((validate_x, validate_y), f, -1)
        pkl.dump((test_x, test_y), f, -1)
    f.close()


def read_matrices_pickle(data='rotten', google=True, cv=True):
    path = 'D:/data/nlpdata/pickled_data/'
    filename = data + '_google.pkl' if google else data + '_glove.pkl'
    filename = Path(path + filename)
    print 'loading data from %s...' % filename
    f = open(filename, 'rb')
    if cv:
        x, y = pkl.load(f)
        return x, y
    else:
        train_x, train_y = pkl.load(f)
        validate_x, validate_y = pkl.load(f)
        test_x, test_y = pkl.load(f)
        return train_x, train_y, validate_x, validate_y, test_x, test_y


if __name__ == '__main__':
    save_matrices_pickle(google=False, data='imdb', cv=False)
