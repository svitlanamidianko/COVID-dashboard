# By S Midianko, Aug 2021
# importing necessary libraries

import pandas as pd
import numpy as np
import sys # to allow for more advanced functionality
from tabulate import tabulate # to allow for better displayed dashboard

class DashboardAPI():
    # class which will allow for the dashboard functionality
    def __init__(self, date='2021-06-16'):
        # default date is as stated in the instr. However, my implementation also allows for choosing a date in advanced mode.
        self.df = self.preprocess_df(pd.read_csv('PA_singlestate_timeseries.csv'))
        self.date = date
        self.day_df = self.df[self.df['date'] == self.date]

    def preprocess_df(self, df):
        preprocessed_df = df.copy()
        # data is an object, but should be datetime for easy identification and filtration
        preprocessed_df['date'] = pd.to_datetime(df['date'])
        # We also have object - columns  whereas they should be either float or int.
        # This is because  there is a string 'Not available' in them, making those objects by default.
        # Not available can be replaced with np.nan which holds the same meaning and then column is converted to float.
        preprocessed_df['actuals.contactTracers'] = df['actuals.contactTracers'].\
                                                                        replace('Not available', np.nan).astype(float)
        preprocessed_df['actuals.icuBeds.currentUsageCovid'] = df['actuals.icuBeds.currentUsageCovid'].\
                                                                        replace('Not Available', np.nan).astype(float)
        preprocessed_df['actuals.icuBeds.currentUsageCovid'] = df['actuals.icuBeds.currentUsageCovid'].\
                                                                        replace('Not Available', np.nan).astype(float)

        return preprocessed_df

    def display_intro_info(self, mode):
        self.df['is_duplicated'] = self.df.duplicated() # method to create a new col with bool meaning if it is duplicate
        num_duplicates = self.df['is_duplicated'].sum()
        intro_info = f'''-----------------
                        The information below is taken from COVID act now at https://covidactnow.org/?s=21821108. 
                        This program has two modes: 
                            (1) basic, which displays primary COVID metrics such as cases/deaths and vaccination rates, 
                            (2) advanced, which adjusts the dashboards according to your needs and allows to also add metrics about tests and hospital capacities.
                        You are now in {mode} mode.
                        
                        Total number of duplicates for the whole time range is {num_duplicates}.
                        Below dashboard is for Pennsylvania, {self.date}.
                      '''
        return intro_info

    def display_basic_dashboard(self):

        # because it is very common in a given df to have a null, we need to account for this
        new_cases = self.finddata_and_checkforavailability('actuals.newCases')
        new_deaths = self.finddata_and_checkforavailability('actuals.newDeaths')
        cumulative_cases = self.finddata_and_checkforavailability('actuals.cases')
        cumulative_deaths = self.finddata_and_checkforavailability('actuals.deaths')
        cases_per100k = self.finddata_and_checkforavailability('metrics.caseDensity')

        vaccRatio_completed = self.finddata_and_checkforavailability('metrics.vaccinationsCompletedRatio', True)
        vacc_completed = self.finddata_and_checkforavailability('actuals.vaccinationsCompleted')
        vaccRatio_initiated = self.finddata_and_checkforavailability('metrics.vaccinationsInitiatedRatio', True)
        vacc_initiated = self.finddata_and_checkforavailability('actuals.vaccinationsInitiated')
        return [["=BASIC DATA=", "===", "===", "==="],
                ["", "INFECTION", "", ""],
                ["", "", "new cases", new_cases],
                ["", "", "new deaths", new_deaths],
                ["", "", "cumulative cases", cumulative_cases],
                ["", "", "cumulative deaths", cumulative_deaths],
                ["", "", "cases per 100k (using 7-day rolling average)", cases_per100k],
                ["", "VACCINATION", "", ""],
                ["", "", "completed ratio (total)", f"{vaccRatio_completed} ({vacc_completed})"],
                ["", "", "initiated ratio (total)", f"{vaccRatio_initiated} ({vacc_initiated})"]]

    def display_advanced_dashboard(self, display_test, display_hospital):
        result = [["=ADVANCED=", "", "", ""]]
        if display_test:
            tests_pos = int(self.day_df['actuals.positiveTests'])
            tests_neg = int(self.day_df['actuals.negativeTests'])

            result += [['', 'TEST', '', ''],
                       ['', '', 'number of positive tests (to date)', tests_pos],
                       ['', '', 'number of negative tests (to date)', tests_neg]]
        if display_hospital:
            hos_capacity = self.finddata_and_checkforavailability('actuals.hospitalBeds.capacity')
            hos_currUsage = self.finddata_and_checkforavailability('actuals.hospitalBeds.currentUsageTotal')
            hos_currUsageCOVID = self.finddata_and_checkforavailability('actuals.hospitalBeds.currentUsageCovid')
            hos_typicalUsage = self.finddata_and_checkforavailability('actuals.hospitalBeds.typicalUsageRate', True)

            hosicu_capacity = self.finddata_and_checkforavailability('actuals.icuBeds.capacity')
            hosicu_currUsage = self.finddata_and_checkforavailability('actuals.icuBeds.currentUsageTotal')
            hosicu_currUsageCOVID = self.finddata_and_checkforavailability('actuals.icuBeds.currentUsageCovid')
            hosicu_typicalUsage = self.finddata_and_checkforavailability('actuals.icuBeds.typicalUsageRate', True)

            result += [['', 'HOSPITAL', '', ''],
                       ['', '', 'total beds in use (out of them, by COVID patients)', f"{hos_currUsage} ({hos_currUsageCOVID})" ],
                       ['', '', 'total beds available', hos_capacity],
                       ['', '', 'typical use of beds', hos_typicalUsage],
                       ['', '', '', ''],
                       ['', '', 'total ICU beds in use (out of them, by COVID patients)', f"{hosicu_currUsage} ({hosicu_currUsageCOVID})" ],
                       ['', '', 'total ICU beds available', hosicu_capacity],
                       ['', '', 'typical ICU use of beds', hosicu_typicalUsage],
                       ['', '', '', '']]
        return result

    def display_legend(self, test, hospital):
        legend = """
                    BASIC: INFECTION
                        * New cases**: New confirmed or suspected cases. 
                        * New deaths**: New confirmed or suspected COVID-19 deaths.
                        * Cumulative cases: Cumulative confirmed or suspected cases.
                        * Cumulative deaths: Cumulative deaths that are suspected or confirmed to have been caused by COVID-19.
                        * Cases per 100k (using 7-day rolling average)**: also known as case density
                    
                    BASIC: VACCINATION
                        * Completed ratio (total): Ratio of population that has completed vaccination.
                        * Initiated ratio (total): Ratio of population that has initiated vaccination.
                     """
        if test:
            legend += """
                    ADVANCED: TEST
                        * number of positive tests: Cumulative positive test results to date
                        * number of negative tests: Cumulative negative test results to date
                         """
        if hospital:
            legend += """
                    ADVANCED: HOSPITAL
                        * total beds in use: Total number of beds currently in use
                        * total beds available: Current staffed acute bed capacity.
                        * typical use of beds: Typical acute bed utilization rate.
                        * total ICU beds in use: Total number of ICU beds currently in use
                        * total ICU beds available: Current staffed ICU bed capacity.
                        * typical ICU use of beds: Typical ICU utilization rate.
                        """
        legend += "\n ** For more info on pre-processing & calculation, check https://apidocs.covidactnow.org/api/"
        return legend

    def finddata_and_checkforavailability(self, column, is_float=False):
        # helper function
        print(self.day_df.shape, 'SHAPE')
        if np.isnan(self.day_df[column].item()):
            return "data is not available"
        elif is_float:
            return float(self.day_df[column])
        else:
            return int(self.day_df[column])

if __name__ == "__main__":
    display_test = False
    display_hospital = False
    if len(sys.argv) == 1: # if one, then only filename is passed (ie dashboard.py)

        dashboardAPI = DashboardAPI()
        intro = dashboardAPI.display_intro_info("BASIC")
        result = dashboardAPI.display_basic_dashboard()

    else:
        if len(sys.argv) == 2:
            if sys.argv[1] == 'advanced':
                print("We will ask you a few questions to display most suitable dashboard. Answer the questions below.")

                display_test_q = input('\nWould you like you see data about the tests? Type Y for yes and N for no.:   ')
                if display_test_q.lower() in ['y', 'yes']:
                    display_test = True

                display_hospital_q = input('\nWould you like you see data about the hospital beds availability.\
                                          \nType Y for yes and N for no.?:   ')
                if display_hospital_q.lower() in ['y', 'yes']:
                    display_hospital = True

                display_date = input('\nDefault date for the dashboard displayed in June 16, 2021.\
                                     \nPress Enter to proceed with default date or otherwise follow instructions below\
                                     \nIf you want to see dashboard for another date, type YYYY-MM-DD of the preferred day.')
                if display_date == "" or len(np.unique(list(set(display_date)))) == 1:
                    # second or is to allow for human factor & accidental typing of the space/some other char
                    display_date = '2021-06-16'

                dashboardAPI = DashboardAPI(display_date)
                intro = dashboardAPI.display_intro_info("ADVANCED")
                result = dashboardAPI.display_basic_dashboard()
                result += dashboardAPI.display_advanced_dashboard(display_test, display_hospital)

            else:
                print(f"Did you mean to write advanced? You typed {sys.argv[0]} instead. \nPlease rerun the program.")
        else:
            print(f"It seems like you mistyped arguments. You typed in {sys.argv},\
                    whereas program expects nothing or advanced.")

    print(intro, tabulate(result))
    display_leg = input("Would you like to see the legend? \nType Y for yes and N for no.   :")
    if display_leg.lower() in ['y', 'yes']:
        legend = dashboardAPI.display_legend(display_test, display_hospital)
        print(legend, "\nThanks for using our program!")
    else:
        print('Thanks for using our program!')

# thanks for reading!
