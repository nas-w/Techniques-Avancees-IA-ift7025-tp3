import math
import random 

import numpy as np

def euclidian_distance(x1, x2):
    distance = 0.0
    for i in range(len(x1)-1):
        distance += (x1[i] - x2[i])**2
    return math.sqrt(distance)

def binary_confusion_matrix(y_pred, y_true, label):
    y_pred = np.where(y_pred == label, 1, 0)
    y_true = np.where(y_true == label, 1, 0)

    result = [[0, 0], [0, 0]]
    for i in range(len(y_true)):
        result[y_true[i]][y_pred[i]] += 1

    return result

def multilabel_confusion_matrix(y_pred, y_true, labels):
    con_matrix = list()
    for label in labels:
        con_matrix.append(list(binary_confusion_matrix(y_pred, y_true, label)))
    return np.array(con_matrix)

def accuracy_metrics(con_matrix):
    return (con_matrix[0][0]+con_matrix[1][1])/(con_matrix[0][0]+con_matrix[0][1]+con_matrix[1][0]+con_matrix[1][1])

def precision_metrics(con_matrix):
    return con_matrix[1][1]/(con_matrix[1][1]+con_matrix[0][1])

def recall_metrics(con_matrix):
    return con_matrix[1][1]/(con_matrix[1][1]+con_matrix[1][0])

def f1_score_metrics(con_matrix):
    return con_matrix[1][1]/(con_matrix[1][1]+0.5*(con_matrix[0][1]+con_matrix[1][0]))

def KFold(X, n_splits=10, shuffle=False, random_state=None):
    X_split = list()
    X_copy = list(X)
    
    fold_size = int(len(X) / n_splits)
    
    for _ in range(n_splits):
        fold = list()
        while len(fold) < fold_size:
            index = random.randrange(len(X_copy))
            X_copy.pop(index)
            fold.append(index)
        X_split.append(fold)

    result = list()
    for n in range(n_splits):
        X_copy = list(X_split)
        test_index = X_copy.pop(n)
        train_index = X_copy
        result.append((train_index, test_index))
    
    return result

def cross_validation_scores(estimator, X, y, n_folds):
    scores = list()
    for train_index, test_index in KFold(X, n_folds):
        X_train = list()
        y_train = list()
        for index in train_index:
            X_train = X_train + list(X[index])
            y_train = y_train + list(y[index])

        X_test = X[test_index]
        y_test = y[test_index]

        estimator.train(X_train, y_train)
        
        evals = estimator.evaluate(X_test, y_test)
        del(evals["con_matrix"])
        scores.append(evals)

    return scores

def all_metrics(y_pred, y_true, labels):
    weight = []
    for classe in np.unique(y_true):
        weight.append(len(y_true[y_true==classe])/len(y_true))
    #Une seule matrice de confusion si on a un problème de classification binaire
    if len(labels) == 2:
        con_matrix = binary_confusion_matrix(y_pred, y_true, labels[1])
        accuracy = accuracy_metrics(con_matrix)
        precision = precision_metrics(con_matrix)
        recall = recall_metrics(con_matrix)
        f1_score = f1_score_metrics(con_matrix)

        return {"Confusion Matrix":con_matrix, "Accuracy":accuracy, "Precision":precision, "Recall":recall, "F1-score":f1_score}
    #Approche un-contre-tous si on n'a pas un problème de classification binaire
    elif len(labels) > 2:
        con_matrix = multilabel_confusion_matrix(y_pred, y_true, labels)
        accuracy = np.zeros(len(labels), dtype=np.float64)
        precision = np.zeros(len(labels), dtype=np.float64)
        recall = np.zeros(len(labels), dtype=np.float64)
        f1_score = np.zeros(len(labels), dtype=np.float64)

        for idx_classe, classe in enumerate(labels):
            accuracy[idx_classe] = accuracy_metrics(con_matrix[idx_classe])
            precision[idx_classe] = precision_metrics(con_matrix[idx_classe])
            recall[idx_classe] = recall_metrics(con_matrix[idx_classe])
            f1_score[idx_classe] = f1_score_metrics(con_matrix[idx_classe])
        accuracy_mean = np.average(accuracy, weights=weight)
        precision_mean = np.average(precision, weights=weight)
        recall_mean = np.average(recall, weights=weight)
        f1_score_mean = np.average(f1_score, weights=weight)
        return {"Confusion Matrix":con_matrix, "Accuracy":accuracy_mean, "Precision":precision_mean, "Recall":recall_mean, "F1-score":f1_score_mean}
