from path import Path
from io_utils.preprocess import SIMPLE_FILTERS, preprocess_review
import cPickle as pkl

import platform
if platform.system() == 'Windows':
    cr_pickle = Path('C:/Users/Song/Course/571/project/pickled_data/cr.pkl')
    pos = Path('D:/data/nlpdata/cr/custrev.pos')
    neg = Path('D:/data/nlpdata/cr/custrev.neg')
else:
    cr_pickle = Path('/home/scz8928999/data/pickled/cr.pkl')
    pos = Path('/home/scz8928999/data/cr/custrev.pos')
    neg = Path('/home/scz8928999/data/cr/custrev.neg')


def read_data(p):
    label = 1 if p[-3:] == 'pos' else 0
    f = open(p)
    x = []
    for line in f:
        line = unicode(line, errors='ignore')
        x.append(preprocess_review(line, filters=SIMPLE_FILTERS))
    y = [label] * len(x)
    return x, y


def save_cr_pickle():
    pos_x, pos_y = read_data(pos)
    neg_x, neg_y = read_data(neg)
    x = pos_x + neg_x
    y = pos_y + neg_y
    f = open('cr.pkl', 'wb')
    pkl.dump((x, y), f, -1)
    f.close()


def read_cr_pickle():
    f = open(cr_pickle, 'rb')
    x, y = pkl.load(f)
    return x, y