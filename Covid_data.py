import pandas as pd
import numpy as np
import scipy as sc
import datetime
from sklearn import linear_model

class CovidMobility:
    COUNTY_DICT = {'Albany': 0, 'Allegany' : 1, 'Broome': 2, 'Cattaraugus' : 3, 'Cayuga' : 4, 'Chautauqua' : 5,
 'Chemung' : 6, 'Chenango' : 7, 'Clinton' : 8, 'Columbia' : 9, 'Cortland': 10, 'Delaware': 11,
 'Dutchess': 12, 'Erie' : 13, 'Essex': 14, 'Franklin': 15, 'Fulton': 16, 'Genesee': 17, 'Greene': 18,
 'Herkimer': 19, 'Jefferson' : 20, 'Lewis' : 21,'Livingston': 22, 'Madison': 23, 'Monroe': 24,
 'Montgomery': 25, 'Nassau': 26, 'New York': 27, 'Niagara': 28, 'Oneida': 29, 'Onondaga': 30, 'Ontario': 31,
 'Orange': 32, 'Orleans': 33, 'Oswego': 34, 'Otsego': 35, 'Putnam': 36, 'Rensselaer': 37, 'Rockland': 38,
 'Saratoga': 39, 'Schenectady': 40, 'Schoharie': 41, 'Schuyler': 42, 'Seneca': 43, 'St. Lawrence': 44,
 'Steuben': 45, 'Suffolk': 46, 'Sullivan': 47, 'Tioga': 48, 'Tompkins': 49, 'Ulster': 50,
 'Warren': 51, 'Washington': 52, 'Wayne': 53, 'Westchester': 54, 'Wyoming': 55, 'Yates': 56}

    def get_mobility_data(self,data_path):
        mobility_data = pd.read_csv(data_path)
        mobility_data.drop(mobility_data[mobility_data['country_region_code'] != "US"].index, inplace=True)
        mobility_data.drop(mobility_data[mobility_data['sub_region_1'] != "New York"].index, inplace=True)
        fixer  = lambda x: datetime.datetime.strptime(x,'%y-%m-%d')
        mobility_data['date'] = mobility_data['date'].apply(fixer)
        grouped = mobility_data.groupby(['sub_region_2'])
        self.counties_indvidual = mobility_data['sub_region_2'].drop_duplicates().dropna()
        self.counties_indvidual = self.counties_indvidual.apply(CovidMobility.county_fixer)
        self.counties__mob_array = self.counties_indvidual.to_numpy()
        self.counties_mob = []
        print (self.counties_indvidual.shape)
        for name, group in grouped:
            county = grouped.get_group(name).drop(['country_region_code','country_region'
                                                      ,'sub_region_1','iso_3166_2_code'],axis = 1)
            self.counties_mob.append(county)

    @staticmethod
    def date_fixer(date):
        x = date.split('/')
        month,day,year = [int(i) for i in x]
        return datetime.datetime(year = year, month = month, day = day)
    @staticmethod
    def county_fixer(county):
        kosher = ['County',"City"]
        if len(county.split())<2:
            return county
        elif county.split()[-1] not in kosher:
            return county
        x = county.split(' ')[:-1]
        x = " ".join(x)
        return x

    def get_case_data(self,data_path):
        case_data = pd.read_csv(data_path)
        case_data.drop(case_data[case_data['state'] != "New York"].index, inplace=True)
        case_data['date'] = case_data['date'].apply(CovidMobility.date_fixer)
        self.count_indvidual = case_data['county'].sort_values().drop_duplicates().dropna()
        self.count_indvidual = self.count_indvidual.apply(CovidMobility.county_fixer)
        self.counties__case_array = self.count_indvidual.to_numpy()
        self.case_toxic_index = []
        for c in self.counties__case_array:
            if not self.counties__mob_array.__contains__(c):
                self.case_toxic_index.append(np.argwhere(self.counties__case_array == c))
        self.mob_toxic_index = []
        for i in self.counties__mob_array:
            if not self.counties__case_array.__contains__(i):
                self.mob_toxic_index.append(np.argwhere(self.counties__mob_array == i))

        grouped = case_data.groupby(['county'])
        self.counties_cases = []
        self.counties_as_array = []
        for name, group in grouped:
            county = grouped.get_group(name)
            county = county.drop(['state','deaths','fips'],axis = 1)
            self.counties_cases.append(county)
        i = 0
        for toxic in self.case_toxic_index:
            del self.counties_cases[toxic[0][0] - i]
            i+=1
        j = 0
        for toxic in self.mob_toxic_index:
            del self.counties_mob[toxic[0][0] - j ]
            j+=1

    def regression_approach(self,start_date, lag, county):
        X = self.counties_mob[self.COUNTY_DICT[county]]
        y = self.counties_cases[self.COUNTY_DICT[county]]
        mob_start = startdate
        case_start = startdate + datetime.timedelta(days = lag)
        bool_mob = X['date'] > mob_start
        bool_case = y['date'] > case_start
        final_date_X = X.tail(1)['date'].to_numpy()
        bool_end_y = y["date"] < final_date_X[0] + datetime.timedelta(days = lag)
        X = X[bool_mob]
        y = y[bool_case & bool_end_y]
        lm = linear_model.LinearRegression()
        model_cases = lm.fit(X,cases)
        test = lm.predict(X)
        print(lm.score(X,cases))
        return model_cases











mob_data = 'Global_Mobility_Report.csv'
case_data = "Raw_Covid_Case_Data.csv"
print(CovidMobility.county_fixer('New York County'))
cov = CovidMobility()
cov.get_mobility_data("Global_Mobility_Report.csv")
cov.get_case_data("Raw_Covid_Case_Data.csv")
startdate = datetime.datetime(2020,3,10)
cov.regression_approach(start_date = startdate, lag = 4 ,county = 'Albany')