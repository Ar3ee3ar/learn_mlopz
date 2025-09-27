# Sample data extraction file which generate a classification dataset using sklearn.datasets
from sklearn.datasets import make_classification
import pandas as pd
import os

def extract_data():
    # create directory/file if not exist
    if not os.path.exists("data"):
        os.mkdir("data")
    # check if file exist (if path point to directory or not exist return false)
    append_mode = os.path.isfile("data/train.csv")
    # if append_mode is false set num_datasets = 10 else num_datasets = 1 
    num_datasets = 10 if not append_mode else 1

    for _ in range(num_datasets):
        # generate feature and target
        # 10000 row, 10 feature, 8 informative feature (helpful for classify), 
        # 2 redundant (generate as random linear combination of informative feature)
        # 2 target class (y), random seed
        X, y = make_classification(n_samples=10000, n_features=10, n_informative=8, n_redundant=2, n_classes=2, random_state=42)
        # create dataframe for feature
        df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])
        # add target column
        df['target'] = y
        # split train 8000 and test 2000
        train_data = df.iloc[:8000]
        test_data = df.iloc[8000:]
        # append to csv (not add header if not append_mode)
        train_data.to_csv("data/train.csv", mode="a", header=not append_mode, index=False)
        test_data.to_csv("data/test.csv", mode="a", header=not append_mode, index=False)

    print("Extracted data from source successfully")

if __name__ == "__main__":
    extract_data()
