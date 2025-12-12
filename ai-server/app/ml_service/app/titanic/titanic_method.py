from pathlib import Path
from typing import Tuple
import pandas as pd
import numpy as np
from pandas import DataFrame
from app.titanic.titanic_dataset import TitanicDataSet
import logging

logger = logging.getLogger(__name__)

class TitanicMethod(object): 

    def __init__(self):
        self.dataset = TitanicDataSet()

    def read_csv(self, fname: str) -> pd.DataFrame:
        return pd.read_csv(fname)

    def create_df(self, df: DataFrame, label: str) -> pd.DataFrame:
        """특정 컬럼을 제거한 DataFrame 반환 (컬럼이 없으면 원본 반환)"""
        if label in df.columns:
            return df.drop(columns=[label])
        else:
            # 컬럼이 없으면 원본 반환 (test.csv의 경우 Survived 컬럼이 없음)
            return df.copy()

    def create_label(self, df: DataFrame, label: str) -> pd.DataFrame:
        return df[[label]]

    def drop_feature(self, this, *feature: str) -> object:
        [i.drop(j, axis=1, inplace=True) for j in feature for i in [this.train,this.test ] ]

        # for i in [this.train, this.test]:
        #     for j in feature:
        #         i.drop(j, axis=1, inplace=True)
 
        return this

    def check_null(self, this) -> int:
        """결측치 개수 확인 (DataFrame 또는 TitanicDataSet 객체 받기)"""
        # DataFrame인 경우
        if isinstance(this, pd.DataFrame):
            return int(this.isnull().sum().sum())
        
        # TitanicDataSet 객체인 경우
        total_null = 0
        for i in [this.train, this.test]:
            if i is not None:
                null_count = int(i.isnull().sum().sum())
                logger.info(f"결측치 개수: {null_count}")
                total_null += null_count
        return total_null

    def extract_title_from_name(self, this):
        """Name 컬럼에서 Title 추출"""
        [i.__setitem__('Title', i['Name'].str.extract('([A-Za-z]+)\.', expand=False)) 
         for i in [this.train, this.test] if i is not None and 'Name' in i.columns]
        return this
    

    def remove_duplicate_title(self, train_df: DataFrame, test_df: DataFrame):
        a = []
        for i in [train_df, test_df]:
            # a.append(i['Title'].unique())
            a += list(set(i['Title'])) # train, test 두번을 누적해야 해서서
        a = list(set(a)) # train, test 각각은 중복이 아니지만, 합치면서 중복발생
        print("🐞🐞🐞")
        print(a)
        # ['Mr', 'Miss', 'Dr', 'Major', 'Sir', 'Ms', 'Master', 'Capt', 'Mme', 'Mrs', 
        #  'Lady', 'Col', 'Rev', 'Countess', 'Don', 'Mlle', 'Dona', 'Jonkheer']
        '''
        ['Mr', 'Sir', 'Major', 'Don', 'Rev', 'Countess', 'Lady', 'Jonkheer', 'Dr',
        'Miss', 'Col', 'Ms', 'Dona', 'Mlle', 'Mme', 'Mrs', 'Master', 'Capt']
        Royal : ['Countess', 'Lady', 'Sir']
        Rare : ['Capt','Col','Don','Dr','Major','Rev','Jonkheer','Dona','Mme' ]
        Mr : ['Mlle']
        Ms : ['Miss']
        Master
        Mrs
        '''
        title_mapping = {'Mr': 1, 'Ms': 2, 'Mrs': 3, 'Master': 4, 'Royal': 5, 'Rare': 6}
        
        return (train_df, test_df)
    

    def title_nominal(self, this):
        """Title을 숫자로 매핑"""
        title_mapping = {'Mr': 1, 'Ms': 2, 'Mrs': 3, 'Master': 4, 'Royal': 5, 'Rare': 6}
        
        for i in [this.train, this.test]:
            if i is not None and 'Title' in i.columns:
                i['Title'] = i['Title'].replace(['Countess', 'Lady', 'Sir'], 'Royal')
                i['Title'] = i['Title'].replace(['Capt','Col','Don','Dr','Major','Rev','Jonkheer','Dona','Mme'], 'Rare')
                i['Title'] = i['Title'].replace(['Mlle'], 'Mr')
                i['Title'] = i['Title'].replace(['Miss'], 'Ms')
                # Master, Mrs는 변화없음
                i['Title'] = i['Title'].fillna('Mr')  # 결측치는 Mr로
                i['Title'] = i['Title'].map(title_mapping).fillna(1).astype(int)
        
        return this          
        


    def pclass_ordinal(self, this):
        """Pclass를 ordinal로 처리 (이미 정수형이므로 그대로 유지)"""
        return this

    def gender_nominal(self, this):
        """성별을 숫자로 매핑"""
        gender_mapping = {'male': 0, 'female': 1}
        [i.__setitem__('Gender', i['Sex'].map(gender_mapping)) 
         for i in [this.train, this.test] if i is not None and 'Sex' in i.columns]
        return this

    def age_ratio(self, this):
        """나이를 구간으로 나누어 처리"""
        for i in [this.train, this.test]:
            if i is not None and 'Age' in i.columns:
                # 결측치를 -0.5로 채우기
                i['Age'] = i['Age'].fillna(-0.5)
                
                # 나이 구간화
                bins = [-1, 0, 5, 12, 18, 24, 35, 60, np.inf]
                labels = ['Unknown','Baby','Child','Teenager','Student','Young Adult','Adult', 'Senior']
                age_mapping = {'Unknown':0 , 'Baby': 1, 'Child': 2, 'Teenager' : 3, 'Student': 4,
                               'Young Adult': 5, 'Adult':6,  'Senior': 7}
                i['AgeGroup'] = pd.cut(i['Age'], bins, labels=labels).map(age_mapping)
        
        return this

    def fare_ordinal(self, this):
        """요금을 구간으로 나누어 처리"""
        for i in [this.train, this.test]:
            if i is not None and 'Fare' in i.columns:
                # 결측치를 중앙값으로 채우기
                if i['Fare'].isnull().any():
                    median_fare = i['Fare'].median()
                    i['Fare'] = i['Fare'].fillna(median_fare)
                
                # 사분위수로 구간화
                try:
                    i['FareBand'] = pd.qcut(i['Fare'], 4, labels=[1, 2, 3, 4], duplicates='drop')
                except ValueError:
                    # 중복값이 많으면 cut 사용
                    i['FareBand'] = pd.cut(i['Fare'], bins=4, labels=[1, 2, 3, 4])
                
                i['FareBand'] = i['FareBand'].fillna(1).astype(int)
        
        return this

    def embarked_ordinal(self, this):
        """탑승 항구를 숫자로 매핑"""
        for i in [this.train, this.test]:
            if i is not None and 'Embarked' in i.columns:
                i['Embarked'] = i['Embarked'].fillna('S')  # 사우스햄튼이 가장 많으니까
                embarked_mapping = {'S': 1, 'C': 2, 'Q': 3}
                i['Embarked'] = i['Embarked'].map(embarked_mapping)
        
        return this

    def kwargs_sample(**kwargs) -> None:
        # for key, value in kwargs.items():
        #     print(f'키워드: {key} 값: {value}')
        {print(''.join(f'키워드: {key} 값: {value}')) for key, value in kwargs.items()}