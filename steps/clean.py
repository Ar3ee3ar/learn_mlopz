# steps/clean.py
# 2. focus on data cleaning
import numpy as np
from sklearn.impute import SimpleImputer

class Cleaner:
    def __init__(self):
        # handling missing value (inthis case replace missing value using most frequent value)
        self.imputer = SimpleImputer(strategy='most_frequent', missing_values=np.nan)
        
        
    def clean_data(self, data):
        # drop un-informative feature
        data.drop(['id','SalesChannelID','VehicleAge','DaysSinceCreated'], axis=1, inplace=True)
        # drop missing value in target
        data = data.dropna(subset=['Result'], inplace=False)
        # cleaning data (remove euro sign and comma in cash value and cast to float)  
        data['AnnualPremium'] = data['AnnualPremium'].str.replace('£', '').str.replace(',', '').astype(float)
        # filling missing data
        for col in ['Gender', 'RegionID']:
             data[col] = self.imputer.fit_transform(data[[col]]).flatten()
        # fill missing value in age with 'med' strategy   
        data['Age'] = data['Age'].fillna(data['Age'].median()) 
        # fill missing value as 1 (bool type)
        data['HasDrivingLicense']= data['HasDrivingLicense'].fillna(1)
        # fill missing value
        data['Switch'] = data['Switch'].fillna(-1)
        # fill missing value and not modify original dataframe (inplace=false)
        data['PastAccident'] = data['PastAccident'].fillna("Unknown", inplace=False)
        # Note: Boxplot can show data distribution consists of Box (majority) and Whiskers (1.5x of box can specify outliers - outside of whisker range is outlier)
        # 1. minimum value
        # 2. Q1 (1st quartile): 25-75 ratio (have data least than its 25%) [left most of box]
        # 3. Median (2nd quartile): 50-50 ratio [center line of box]
        # 4. Q3 (3rd quartile): 75-25 ratio (have data least than its 75%) [right most of box]
        # 5. maximum
        Q1 = data['AnnualPremium'].quantile(0.25)
        Q3 = data['AnnualPremium'].quantile(0.75)
        # Interquartile Range (IQR) = Q3-Q1
        # lower whisker(lower bound) = max[min, Q1 - (1.5 * IQR)]
        # upper whisker(upper bound) = min[max, Q3 + (1.5 * IQR)]
        # Note: หาก “ภูเขา” อยู่ค่อนไปทางขวาของช่วงข้อมูลทั้งหมด เราก็ตอบได้ทันทีว่า ข้อมูลมีการกระจายตัวแบบเบ้ซ้าย (Left Skewed Distribution)
        IQR = Q3 - Q1
        upper_bound = Q3 + 1.5 * IQR
        data = data[data['AnnualPremium'] <= upper_bound] # filter only data that less than equal to upper_bound (not in outliers)
        
        return data