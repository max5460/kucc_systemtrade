from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV


def GetOptimalClassifier(X_train, y_train):
    search_params = {
                     'n_estimators': [5, 10, 20, 30, 50, 100, 300],
                     'random_state': [2525],
                     'n_jobs': [1],
                     'min_samples_split': [3, 5, 10, 15, 20, 25, 30, 40, 50, 100],
                     'max_depth': [3, 5, 10, 15, 20, 25, 30, 40, 50, 100]
                    }
    gridSearchCV = GridSearchCV(RandomForestClassifier(), search_params, cv=3, verbose=True, n_jobs=-1)
    gridSearchCV.fit(X_train, y_train)

    return gridSearchCV.best_estimator_
