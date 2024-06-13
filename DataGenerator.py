import csv
import requests
from math import isqrt


class PopulationAnalyzer:
    # Initializing the API URL
    def __init__(self, api_url):
        self.api_url=api_url
        self._data=None
        self.state_population_data={}
        self.population_change={}
        self.state_prime_factors={}
        self.years=[]

    @property
    # Property to fetch & store data from the API
    def data(self):
        if not self._data:
            self.fetch_data()
        return self._data

    def fetch_data(self):
        # Fetching data from the API and storing it
        response=requests.get(self.api_url)
        self._data=response.json()["data"]

    def process_data(self):
        # Processing the above fetched data and organizing it by state and year
        year_set=set()
        for entry in self.data:
            state=entry["State"]
            year=int(entry["Year"])
            population=int(entry["Population"])
            year_set.add(year)
            if state not in self.state_population_data:
                self.state_population_data[state]={}
            self.state_population_data[state][year]=population

        min_year=min(year_set)
        max_year=max(year_set)

        for year in range(min_year, max_year + 1):
            if year not in year_set:
                year_set.add(year)

        self.years=sorted(list(year_set))
        for state, population_data in self.state_population_data.items():
            for year in self.years:
                if year not in population_data:
                    self.state_population_data[state][year]=0

    def calculate_population_change(self):
        # Logic to calculate population change for individual state
        for state, population_data in self.state_population_data.items():
            for i in range(1, len(self.years)):
                prev_year=self.years[i - 1]
                current_year=self.years[i]
                change=population_data[current_year] - population_data[prev_year]
                percent_change=(change / population_data[prev_year]) * 100 if population_data[prev_year] != 0 else 0
                if state not in self.population_change:
                    self.population_change[state]={}
                self.population_change[state][current_year]=(change, percent_change)

    def calculate_prime_factors(self, n):
        # Calculating prime factor
        factors = []
        while n % 2==0:
            factors.append(2)
            n = n // 2
        for i in range(3, isqrt(n) + 1, 2):
            while n % i==0:
                factors.append(i)
                n = n // i
        if n > 2:
            factors.append(n)
        return factors

    def calculate_final_year_prime_factors(self):
        final_year=self.years[-1]
        for state, population_data in self.state_population_data.items():
            final_year_population=population_data[final_year]
            self.state_prime_factors[state]=self.calculate_prime_factors(final_year_population)

    def generate_csv(self):
        # Generating CSV
        with open('population_data.csv', 'w', newline='') as csvfile:
            writer=csv.writer(csvfile)
            header=["State Name"] + [str(year) for year in self.years] + ["Final Year Factors"]
            writer.writerow(header)
            for state, population_data in self.state_population_data.items():
                row=[state]
                for year in self.years:
                    population=population_data.get(year, "")
                    change, percent_change=self.population_change[state].get(year, ("", ""))
                    if percent_change != "":
                        population=f"{population} ({percent_change:.2f}%)"
                    row.append(population)
                factors=";".join(map(str, self.state_prime_factors[state]))
                row.append(factors)
                writer.writerow(row)

    def analyze_population(self):
        self.process_data()
        self.calculate_population_change()
        self.calculate_final_year_prime_factors()
        self.generate_csv()


if __name__ == "__main__":
    api_url="https://datausa.io/api/data?drilldowns=State&measures=Population"
    analyzer=PopulationAnalyzer(api_url)
    analyzer.analyze_population()
