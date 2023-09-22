import requests
import os
import csv
import datetime
from datetime import datetime, timedelta
import time
import json
import math
import copy
import HunterDevGone

FOLDER_ANALYSIS = 'developersInactivityMetric'
FOLDER_NAME = 'repoDiProva'
COMMIT_LIST = 'output/{}/{}/commit_list.csv'
DEVS_LOGIN_LIST = 'output/devs_login_list.csv'
C_DEVS_LOGIN_LIST = 'output/c_devs_login_list.csv'
DEVS_STATS = 'output/devs_stats.csv'
REPLACEMENTS = 'output/replacements'
DEV_REPLECEMENTS = '{}_replacements.csv'


def get_path_to_folder():
    """
        Returns the path to the project folder
        Output:
            path(str): the path to the project folder
    """
    path_to_folder = os.getcwd()
    list_folder = path_to_folder.split('/')
    path = '/'
    for elem in list_folder:
        if elem != FOLDER_ANALYSIS:
            if path == '/':
                path = path + elem
            else:
                path = path + '/'+ elem
        else:
            path = path + '/' + FOLDER_NAME
            break
    return path

def get_path_to_replacements_folder():
    path_main_folder = get_path_to_folder()
    path_folder = path_main_folder + '/' + REPLACEMENTS
    exist = os.path.isdir(path_folder)
    if not exist:
        os.mkdir(path_folder)
    
    return path_folder

def get_path_to_dev_replacements(dev_gone):
    path_folder = get_path_to_replacements_folder()
    path = path_folder + '/' + DEV_REPLECEMENTS.format(dev_gone)
    return path

def get_path_commit_list(owner: str, repository: str):
    """
    Returns the path to the commit_list.csv file
    Args:
        repository(str): the name of the name of the repository whose commit_list file we want to have
    Output:
        path(str): the path to the commit_list file
    """
    path_folder = get_path_to_folder()
    path = path_folder + '/' + COMMIT_LIST.format(owner, repository)
    return path

def get_path_devs_login_list():
    """
    Returns the path to the devs_login_list.csv file
    Args:
        repository(str): the name of the name of the repository whose devs_login_list file we want to have
    Output:
        path(str): the path to the devs_login_list file
    """
    path_folder = get_path_to_folder()
    path = path_folder + '/' + DEVS_LOGIN_LIST
    return path

def get_path_c_devs_login_list():
    """
    Returns the path to the c_devs_login_list.csv file
    Args:
        repository(str): the name of the name of the repository whose c_devs_login_list file we want to have
    Output:
        path(str): the path to the c_devs_login_list file
    """
    path_folder = get_path_to_folder()
    path = path_folder + '/' + C_DEVS_LOGIN_LIST
    return path

def get_path_devs_stats():
    """
    Returns the path to the devs_stats.csv file
    Args:
        repository(str): the name of the name of the repository whose devs_stats file we want to have
    Output:
        path(str): the path to the devs_stats file
    """
    path_folder = get_path_to_folder()
    path = path_folder + '/' + DEVS_STATS
    return path

def convert_string_to_date(date_string, date_format = "%Y-%m-%d"):
    """
    Takes as input a date in string format and converts it to date type in the format specified in input
    Args:
        date_string(str): the string we want to convert to date
        date_format(str): the format in which we want to save the converted date
    Return:
        date(date): the converted date

    """
    date = datetime.strptime(date_string, date_format).date()
    return date

class Dev_recomender:
    def __init__(self, owner, repository, token):
        """
        it is the constructor of the Dev_recomender class, when it is called, in addition to validating the class attributes, 
        it checks if the devs_stats.csv data set exists, 
        if it does not exist, the creation of the data set begins
        """
        self.__owner = owner
        self.__repository = repository
        self.__token = token
        exist = os.path.isfile(get_path_devs_stats())
        if not exist:
            print("the devs_stats data set does not exist")
            self.calculate_devs_stats_list()
        else:
            c_devs_login_list = self.__read_copy_devs_login_list()
            if len(c_devs_login_list) > 1:
                print("devs_stats exists but statistics for all devs have not been calculated. I continue with the calculation")
                self.calculate_devs_stats_list()
        
        self.__iff_calculation = self.calculate_iff_for_each_file()
        self.__devs_stats_cf_iff = self.edit_devs_stats_with_cf_iff()
        


    def __read_commit_list(self):
        """
        The function reads the commit_list.csv file
        Output:
            commit_list(list): each item in the list is a commit, represented as a dictionary with the following keys:
            'sha',unique commit code; 
            'author', login of the dev who committed;  
            'date', the date the commit was made in the format yyyy-mm-dd
        """
        path = get_path_commit_list(self.__owner, self.__repository)
        commit_list = []
        with open(path, 'r', newline= '') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                sha = row['sha']
                date = convert_string_to_date(row['date'][:10])
                commit_list.append({
                    'sha': sha,
                    'author': row['author_id'],
                    'date': date
                })
        
        return commit_list
    
    def __get_dev_commit_list(self, dev_login: str):
        """
        The function returns all commits made by a specific developer
        Args:
            dev_login(str): the login of the dev whose commits we want
        Output: 
            dev_commit_list(list): each item in the list is a dev_login's commit , represented as a dictionary with the following keys:
            'sha',unique commit code; 
            'author', login of the dev who committed;  
            'date', the date the commit was made in the format yyyy-mm-dd
        """
        commit_list = self.__read_commit_list()
        dev_commit_list = []
        for commit in commit_list:
            if commit['author'] == dev_login:
                dev_commit_list.append(commit)
        
        return dev_commit_list


    def __handle_rate_limit(self, response_headers):
        """
        The function checks the remaining rate limit of the token and in case the number of remaining requests is equal to 0, 
        the function suspends the program, until the rate limit is restored
        Args:
            response_headers: the header of the response of the gi hub api, which contains the information regarding the rate limit
        """
        if "X-RateLimit-Remaining" in response_headers:
            remaining_requests = int(response_headers["X-RateLimit-Remaining"])
            reset_timestamp = int(response_headers["X-RateLimit-Reset"])

            if remaining_requests == 0:
                # Attenzione: è necessario attendere fino al reset_timestamp prima di effettuare ulteriori richieste
                current_timestamp = int(time.time())
                sleep_duration = max(0, reset_timestamp - current_timestamp) + 5  # Aggiungi 5 secondi di margine
                print(f"Rate limit exceeded. Sleeping for {sleep_duration} seconds...")
                time.sleep(sleep_duration)

    def __get_modified_files_in_commit(self, commit_sha):
        """
        The function through the git hub api gets the names of the files modified by a commit
        Args:
            commit_sha(str): the unique code of the code used by the API to obtain the names of the modified files
        Outuput:
            files_modified(list): the list containing the names of the files modified by the commit
        """
        url = f"https://api.github.com/repos/{self.__owner}/{self.__repository}/commits/{commit_sha}"
        headers = {
        "Authorization": f"token {self.__token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self.__handle_rate_limit(response.headers)
            commit_data = response.json()
            if 'files' in commit_data:
                files_modified = [file_modified['filename'].split('/')[-1] for file_modified in commit_data['files']]
                return files_modified
        
        else:
            print(f"Errore {response.status_code}: {response.text}")
        
        return []
    
    def __get_devs_stats(self, dev_login: str):
        """
        the function calculates developer statistics by calculating 
        for each file the number of commits made by the developer on that file
        Args:
            dev_login(str): the login of the dev whose statistics we want to calculate
        Output:
            dev_stats(dict): A dictionary containing the developer's statistics, with the following keys:
            'dev': dev login
            for each file we have a 'file_name' key: number of commits made by the developer on the file
        """
        dev_commit_list = self.__get_dev_commit_list(dev_login)
        number_commits = len(dev_commit_list)
        i = 0
        T_status = 5
        dev_stats = {'dev': dev_login}
        for commit in dev_commit_list:
            files_modified = self.__get_modified_files_in_commit(commit['sha'])
            for file_modified in files_modified:
                if file_modified in dev_stats:
                    dev_stats[file_modified] += 1
                else:
                    dev_stats[file_modified] = 1
            
            i += 1
            perc = int(i/number_commits * 100)
            if perc == T_status:
                print('Commits calculated of devoloper {}%'.format(perc))
                T_status += 5
        
        print("End calculation of developer statistics " + str(dev_login))
        
        return dev_stats
    
    def __get_devs_login_list(self):
        """
        The function calls the git hub api to get the list of logins of developers working on the repository
        Output:
            devs_login_list(list): the list contains the logins of the repository developers
        """
        print("Start calculation to get all developer logins of the repository " + str(self.__owner) + '/' + str(self.__repository))
        base_url = f"https://api.github.com/repos/{self.__owner}/{self.__repository}/contributors"
        devs_login_list = []

        page = 1
        per_page = 100

        while True:
            params = {
                'page': page,
                'per_page': per_page
            }

            headers = {
                'Authorization': f"token {self.__token}"
            }

            response = requests.get(base_url, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if len(data) == 0:
                    break
                for contributor in data:
                    devs_login_list.append(contributor['login'])
                page += 1
            else:
                print(f"Errore nella richiesta: {response.status_code}")
                break
        print("End of calculation for developers")
        return devs_login_list
    
    def __save_devs_login_list(self):
        """
        The function checks if the devs_login_list file exists, 
        if it does not exist it generates the login_list 
        and saves the devs_login_list.csv file
        """
        path_list = get_path_devs_login_list()
        exist = os.path.isfile(path_list)
        if not exist:
            print("The devs_login_list.csv file is missing")
            devs_login_list = self.__get_devs_login_list()
            print("Saving developer logins in devs_login_list.csv")
            with open(path_list, mode = 'w') as file:
                for dev_login in devs_login_list:
                    file.write(f"{dev_login}\n")

    
    def read_devs_login_list(self):
        """
        The function reads the devs_login_list.csv file
        Output:
            devs_login_list(list): the list contains the logins of all the developers of the repository
        """
        path_list = get_path_devs_login_list()
        self.__save_devs_login_list()
        with open(path_list, mode='r') as file:
            content = file.readlines()
            devs_login_list = [line.strip() for line in content]
        
        return devs_login_list
    
    def __create_copy_devs_login_list(self):
        """
        The function creates a copy of the devs_login_list file and saves the copy to the c_devs_login_list file
        """
        path_c_devs_login_list = get_path_c_devs_login_list()
        exist = os.path.isfile(path_c_devs_login_list)
        if not exist:
            devs_login_list = self.read_devs_login_list()
            print("Writing copy of developer login list")
            with open(path_c_devs_login_list, mode='w') as file:
                for dev_login in devs_login_list:
                    file.write(f"{dev_login}\n")
    
    def __read_copy_devs_login_list(self):
        """
        The function reads the c_devs_login_list.csv file
        Output:
            devs_login_list(list): the list contains the logins of all the developers of the repository
        """
        path_file = get_path_c_devs_login_list()
        self.__create_copy_devs_login_list()
        with open(path_file, mode='r') as file:
            content = file.readlines()
            c_devs_login_devs = [line.strip() for line in content]
        
        return c_devs_login_devs
    
    def __update_copy_devs_login_list(self, c_devs_login_devs):
        """
        The function is used to update the c_devs_login_list file, 
        and is used to keep the system updated 
        on developers that are missing from the statistics calculation
        Args:
            c_devs_login_devs(list): The list of developer logins that are missing from the statistics calculation
        """
        path_file = get_path_c_devs_login_list()
        with open(path_file, mode= 'w') as file:
            for dev_login in c_devs_login_devs:
                file.write(f"{dev_login}\n")

    def __update_devs_stats(self, dev_stats):
        """
        The function is used to update the devs_stats file 
        every time the calculation of a developer's statistics is finished
        Args:
            devs_stats(list): the list containing the statistics of the developers whose statistics we have finished calculating
        """
        path_file = get_path_devs_stats()
        exist = os.path.isfile(path_file)
        if not exist:
            with open(path_file, 'w') as new_file:
                pass
        
        with open(path_file, mode='a') as file:
            line_json = json.dumps(dev_stats)
            file.write(f"{line_json}\n")

    def read_devs_stats(self):
        """
        The function reads the devs_stats.csv file
        Output:
            devs_stats(list): A list containing dictionaries that represent developer statistics and are of the type:
            'dev': dev login
            for each file we have a 'file_name' key: number of commits made by the developer on the file
        """
        path_file = get_path_devs_stats()
        with open(path_file, mode='r') as file:
            lines = file.readlines()
        
        devs_stats_list = []
        for line in lines:
            devs_stats_list.append(json.loads(line))
        
        return devs_stats_list
    
    def calculate_devs_stats_list(self):
        """
        The function generates devs_stats.csv. 
        It scans the list of developer logins and 
        for each developer calculates the statistics taking into account the commits they have made in the commit_list.
        Every time the statistics calculation finishes, update the devs_stats file and the c_devs_login_list file
        """
        print("Start calculation for the creation of devs_stats.csv")
        login_devs = self.__read_copy_devs_login_list()
        login_devs2 = copy.deepcopy(login_devs)
        number_devs = len(self.read_devs_login_list())
        T_status = 5
        i = 0
        for login_dev in login_devs:
            print("Start calculating statistics for the developer " + str(login_dev))
            dev_stats = self.__get_devs_stats(login_dev)
            print("End of calculation, saving statistics")
            self.__update_devs_stats(dev_stats)
            login_devs2.remove(login_dev)
            self.__update_copy_devs_login_list(login_devs2)
            i += 1
            perc = int(i/number_devs * 100)
            if perc == T_status:
                print('Calculated statistics for developers {}%'.format(perc))
                T_status += 5
        
        print("End of statistics calculation for all developers")


    def get_developer_stats(self, login_dev: str):
        """
        The function returns the statistics of a specific developer
        Args:
            login_dev(str): the login of the developer whose statistics we want
        Output:
            dev_stat(dict): developer statistics in the following format:
            'dev': dev login
            for each file we have a 'file_name' key: number of commits made by the developer on the file
        """
        for dev_stat in self.__devs_stats_cf_iff:
            if dev_stat['dev'] == login_dev:
                return dev_stat
        
        print("the developer " + login_dev + " could not be found")

    def cosine_similarity(self, first_dev, second_dev,decimal_places):
        """
        the function calculates the cosine similarity of two developers' statistics
        Args:
            first_dev(dict): the statistics of the developer whose replacement we want to find
            second_dev(dict): the statistics of the possible replacement
            decimal_places(int): the number of decimal places to round the cosine similarity value
        Output:
            cosine_similarity(float): the cosine similarity between the two developers rounded
        """
        scalar_product = self.scalar_product(first_dev, second_dev)
        length_normalization_f = self.length_normalization(first_dev)
        length_normalization_s = self.length_normalization(second_dev)
        cosine_similarity = scalar_product/(length_normalization_f * length_normalization_s)
        print("decimal places" +str(decimal_places)+"tipo"+ str(type(decimal_places)))
        print("cosine similarity" +str(cosine_similarity)+"tipo"+ str(type(cosine_similarity)))
        return round(cosine_similarity, decimal_places)
    
    def recomender(self, login_dev, k, decimal_places):
        """
        the function calculates the list of developers who can be possible substitutes for the requested developer, 
        calculating the cosine similarity between the requested developer and all other substitutes. 
        The function considers the top k developers with the highest cosine similarity
        Args:
            login_dev(str): the login of the developer for whom we want to find a replacement
            k(int): the number of substitutes I want the recommender to recommend to us
            decimal_places(int): the number of decimal places to round the cosine similarity value
        Output:
            classification(list):the list of developers who can be substitutes.
            Each item in the list is a developer in the form of a dictionary with the following keys:
            'dev', developer name;
            'cosine_similarity', cosine similarity value
        """
        devs_stats = copy.deepcopy(self.__devs_stats_cf_iff)
        dev_stats = self.get_developer_stats(login_dev)
        if dev_stats:
            devs_stats.remove(dev_stats)
            classification = []
            for dev in devs_stats:
                keys_s = set(dev.keys())
                keys_s.discard('dev')
                if keys_s:
                    cosine_similarity = self.cosine_similarity(dev_stats, dev, decimal_places)
                    classification.append({
                        'dev': dev['dev'],
                        'cosine_similarity': cosine_similarity
                    })
            
            classification = sorted(classification, key=lambda x: x['cosine_similarity'], reverse=True)
            return classification[0:k]

    def scalar_product(self, first_dev, second_dev):
        """
        The function performs the dot product between the statistics of two developers
        Args:
            first_dev(dict): the statistics of the developer whose replacement we want to find
            second_dev(dict): the statistics of the possible replacement
        Output:
            scalar_product(float): the result of the dot product between the statistics of the two developers
        """
        keys_second_dev = set(second_dev.keys())
        keys_first_dev = set(first_dev.keys())
        shared_keys = keys_first_dev & keys_second_dev
        shared_keys.discard('dev')
        scalar_product = 1
        if len(shared_keys) > 0:
            for key in shared_keys:
                cf_iff_f = first_dev[key]
                cf_iff_s = second_dev[key]
                scalar_product += (cf_iff_f * cf_iff_s)
            return scalar_product
        else:
            return 1
    
    def edit_devs_stats_with_cf_iff(self):
        """
        the function normalizes the values of the developer statistics according to the cf_iff
        """
        devs_stats = self.read_devs_stats()
        for i in range(0, len(devs_stats)):
            keys = set(devs_stats[i])
            keys.discard('dev')
            for key in keys:
                devs_stats[i][key] = (1 + math.log10(devs_stats[i][key]))*self.__iff_calculation[key]
        
        return devs_stats

    def length_normalization(self, dev_stats):
        """
        the function calculates the normalization of the length of a developer's statistics
        Args:
            dev_stats(dict): the developer statistics whose length normalization we want to calculate
        """
        keys = set(dev_stats.keys())
        keys.discard('dev')
        sum_squares = 0
        for key in keys:
            sum_squares += pow(dev_stats[key], 2)
        
        length_normalization = math.sqrt(sum_squares)
        return length_normalization


    def get_file_names(self):
        """
        the function returns the set of file names in the repository
        Output:
            files_name_set(set): the set containing the names of the repository files
        """
        devs_stats = self.read_devs_stats()
        files_name_set = set()
        for dev in devs_stats:
            files_name_dev = set(dev.keys())
            files_name_dev.discard('dev')
            if not files_name_set:
                files_name_set = files_name_dev
            else:
                files_name_set = files_name_set | files_name_dev
        
        return files_name_set
    
    def calculate_iff_for_each_file(self):
        """
        the function calculates the iff value for each file
        Output:
            basis_ff_calculation(dict): the dictionary contains the iff values for each file, 
            in the following format:
            'file_name', iff value
        """
        devs_stats = self.read_devs_stats()
        basis_ff_calculation = self.creates_basis_for_iff_calculation()
        files_number = len(basis_ff_calculation)
        for iff_file in basis_ff_calculation:
            ff = 1
            for dev_stats in devs_stats:
                if iff_file in dev_stats:
                    ff += 1
            
            iff = math.log10(files_number/math.log10(ff))
            basis_ff_calculation[iff_file] = iff
        
        return basis_ff_calculation
    
    def creates_basis_for_iff_calculation(self):
        """
        the function creates the basis for the iff calculation by creating
        Output:
            basis_iff_calculation(dict): dictionary in the following format, for each file:
            'file_name', iff value initialized to 0
        """
        files_name_set = self.get_file_names()
        basis_iff_calculation = {name_file: 0 for name_file in files_name_set}
        return basis_iff_calculation
    
    def read_developers_gone(self):
        path_devs_gone = HunterDevGone.get_path_devs_gone()
        devs_gone = []
        with open(path_devs_gone, mode='r', newline='') as file:
            content = file.readlines()
            devs_gone = [line.strip() for line in content]
        
        return devs_gone
    
    def save_dev_s_replacements(self, dev_gone, classification):
        path_replacement = get_path_to_dev_replacements(dev_gone)
        fieldname = ['dev', 'cosine_similarity']
        with open(path_replacement, mode= 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldname)
            writer.writeheader()
            writer.writerows(classification)
    
    def recomender_substitutes(self, k, decimal_places):
        devs_gone = self.read_developers_gone()

        for dev_gone in devs_gone:
           classification = self.recomender(dev_gone, k, decimal_places)
           self.save_dev_s_replacements(dev_gone, classification)




