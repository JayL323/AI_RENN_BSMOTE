"""Class to perform over-sampling using SMOTE and cleaning using ENN."""

# Authors: Guillaume Lemaitre <g.lemaitre58@gmail.com>
#          Christos Aridas
# License: MIT
from collections import Counter
from sklearn.datasets import make_classification

from sklearn.base import clone
from sklearn.utils import check_X_y

from imblearn.base import BaseSampler
from imblearn.over_sampling import BorderlineSMOTE
from imblearn.over_sampling.base import BaseOverSampler
#from imblearn.under_sampling import EditedNearestNeighbours
from imblearn.under_sampling import RepeatedEditedNearestNeighbours
from imblearn.utils import check_target_type
from imblearn.utils import Substitution
from imblearn.utils._docstring import _n_jobs_docstring
from imblearn.utils._docstring import _random_state_docstring
from sklearn import svm

import warnings
from sklearn.pipeline import make_pipeline
warnings.filterwarnings("ignore")
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np

@Substitution(
    sampling_strategy=BaseOverSampler._sampling_strategy_docstring,
    n_jobs=_n_jobs_docstring,
    random_state=_random_state_docstring,
)
class RENN_BSMOTE(BaseSampler):
    """Over-sampling using SMOTE and cleaning using ENN.

    Combine over- and under-sampling using SMOTE and Edited Nearest Neighbours.

    Read more in the :ref:`User Guide <combine>`.

    Parameters
    ----------
    {sampling_strategy}

    {random_state}

    smote : object, default=None
        The :class:`imblearn.over_sampling.SMOTE` object to use. If not given,
        a :class:`imblearn.over_sampling.SMOTE` object with default parameters
        will be given.

    enn : object, default=None
        The :class:`imblearn.under_sampling.EditedNearestNeighbours` object
        to use. If not given, a
        :class:`imblearn.under_sampling.EditedNearestNeighbours` object with
        sampling strategy='all' will be given.

    {n_jobs}

    See Also
    --------
    SMOTETomek : Over-sample using SMOTE followed by under-sampling removing
        the Tomek's links.

    Notes
    -----
    The method is presented in [1]_.

    Supports multi-class resampling. Refer to SMOTE and ENN regarding the
    scheme which used.

    References
    ----------
    .. [1] G. Batista, R. C. Prati, M. C. Monard. "A study of the behavior of
       several methods for balancing machine learning training data," ACM
       Sigkdd Explorations Newsletter 6 (1), 20-29, 2004.

    Examples
    --------

    >>> from collections import Counter
    >>> from sklearn.datasets import make_classification
    >>> from imblearn.combine import SMOTEENN # doctest: +NORMALIZE_WHITESPACE
    >>> X, y = make_classification(n_classes=2, class_sep=2,
    ... weights=[0.1, 0.9], n_informative=3, n_redundant=1, flip_y=0,
    ... n_features=20, n_clusters_per_class=1, n_samples=1000, random_state=10)
    >>> print('Original dataset shape %s' % Counter(y))
    Original dataset shape Counter({{1: 900, 0: 100}})
    >>> sme = SMOTEENN(random_state=42)
    >>> X_res, y_res = sme.fit_resample(X, y)
    >>> print('Resampled dataset shape %s' % Counter(y_res))
    Resampled dataset shape Counter({{0: 900, 1: 881}})
    """

    _sampling_type = "over-sampling"

    def __init__(
        self,
        sampling_strategy="auto",
        random_state=None,
        smote=None,
        enn=None,
        n_jobs=None,
    ):
        super().__init__()
        self.sampling_strategy = sampling_strategy
        self.random_state = random_state
        self.smote = smote
        self.enn = enn
        self.n_jobs = n_jobs

    def _validate_estimator(self):
        "Private function to validate SMOTE and ENN objects"
        if self.smote is not None:
            if isinstance(self.smote, BorderlineSMOTE):
                self.smote_ = clone(self.smote)
            else:
                raise ValueError(
                    "smote needs to be a SMOTE object."
                    "Got {} instead.".format(type(self.smote))
                )
        # Otherwise create a default SMOTE
        else:
            self.smote_ = BorderlineSMOTE(
                sampling_strategy=self.sampling_strategy,
                random_state=self.random_state,
                n_jobs=self.n_jobs,
            )

        if self.enn is not None:
            if isinstance(self.enn, RepeatedEditedNearestNeighbours):
                self.enn_ = clone(self.enn)
            else:
                raise ValueError(
                    "enn needs to be an EditedNearestNeighbours."
                    " Got {} instead.".format(type(self.enn))
                )
        # Otherwise create a default EditedNearestNeighbours
        else:
            self.enn_ = RepeatedEditedNearestNeighbours(
                sampling_strategy="all", n_jobs=self.n_jobs
            )

    def _fit_resample(self, X, y):
        self._validate_estimator()
        y = check_target_type(y)
        X, y = check_X_y(X, y, accept_sparse=["csr", "csc"])
        self.sampling_strategy_ = self.sampling_strategy

        X_res, y_res = self.smote_.fit_resample(X, y)
        return self.enn_.fit_resample(X_res, y_res)

def Load_hayes_roth_dataset(path):
    #将1,2类划分为一类（102）,3划分为一类（30），共132个样本
    #1: 97, -1: 94
    x=[]
    y=[]
    with open(path) as f:
        for eachline in f:
            datas=eachline.split(',')
            x.append([int(i) for i in datas[2:5]])
            y.append(1 if datas[5][0]!='3' else -1)
            #y.append(int(datas[5][0]))
    return x,y
X, y=Load_hayes_roth_dataset('./datasets/hayes-roth.data')
x_train, x_test, y_train, y_test = train_test_split(X, y)
# X, y = make_classification(n_classes=2, class_sep=2,
# weights=[0.2, 0.8], n_informative=3, n_redundant=1, flip_y=0,
# n_features=20, n_clusters_per_class=1, n_samples=1000, random_state=10)
print('Original dataset shape %s' % Counter(y))
sme = RENN_BSMOTE(random_state=42)
X_res, y_res = sme.fit_resample(x_train, y_train)
print('Resampled dataset shape %s' % Counter(y_res))
clf_rbf= svm.SVC(C=10,gamma=5,shrinking=True).fit(X_res, y_res)
#print(clf_rbf)
pre_ret=clf_rbf.predict(x_test)
print(pre_ret)
index=0
countRight=0
countAll=len(pre_ret)
for ret in pre_ret:
    if ret==y_test[index]:
        countRight=countRight+1
    index=index+1
print(float(countRight)/countAll)