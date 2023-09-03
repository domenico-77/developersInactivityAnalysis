import os
import sys
import csv

#CONSTANT
ROW_AFTER_TF_DEVS = 'TF authors (Developer;Files;Percentage):'
FILE_TF_REPORT = 'output/TF_report.txt'
FOLDER_NAME = 'repoDiProva'
FOLDER_ANALYSIS = 'developersInactivityAnalysis'
FILE_UNMASKING_RESULTS = 'output/unmasking_results.csv'
TF_DEVS = 'output/TF_devs.csv'
TF_DEVS_NAMES = 'output/TF_devs_names.csv'

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

def get_path_TF_report(owner: str):
    """
    Returns the path to the TF_report file
    Args:
        owner(str): the name of the owner of the repository whose TF_report file we want to have
    Output:
        path(str): the path to the TF_report file
    """
    path_folder = get_path_to_folder()
    path = path_folder + '/' + FILE_TF_REPORT
    return path

def get_paht_unmasking_results(owner: str):
    """
    Returns the path to the unmasking_results file
    Args:
        owner(str): the name of the owner of the repository whose unmasking_results file we want to have
    Output:
        path(str): the path to the unmasking_results file
    """
    path_folder = get_path_to_folder()
    path = path_folder + '/' + FILE_UNMASKING_RESULTS
    return path

def get_path_TF_devs(owner: str):
    """
    Returns the path to the TF_devs file
    Args:
        owner(str): the name of the owner of the repository whose TF_devs file we want to have
    Output:
        path(str): the path to the TF_devs file
    """
    path_folder = get_path_to_folder()
    path = path_folder + '/' + TF_DEVS
    return path


def get_path_TF_devs_names(owner: str):
    """
    Returns the path to the TF_devs_names file
    Args:
        owner(str): the name of the owner of the repository whose TF_devs_names file we want to have
    Output:
        path(str): the path to the TF_devs_names file
    """
    path_folder = get_path_to_folder()
    path = path_folder + '/' + TF_DEVS_NAMES
    return path
    

def TF_report_reader(owner):
    """
    The function reads the TF_report file of the specified repository
    Args:
        owner(str): the name of the owner whose file we want to read
    Output:
        content(list): the list contains the contents of the TF_report file, each element of the list is a line of the file
    """
    file_path = get_path_TF_report(owner)
    try:
        with open(file_path, 'r') as file:
            content = file.readlines()
        return content
    except FileNotFoundError:
        print("Il file non è stato trovato.")
        return []

def extract_names_TF_developers(owner: str):
    """
    The function returns the list of names of TF developers
    Args:
        owner(str): the name of the owner of the repository of which we want the names of the TF developers
    Output:
        TF_devs_name(list): the list contains the names of TF developers
    """
    TF_report_content = TF_report_reader(owner)
    TF_devs_name = []
    row_exceeded = False
    for row in TF_report_content:
        row = row.strip()
        if not row_exceeded:
            if row == ROW_AFTER_TF_DEVS:
                row_exceeded = True
        else:
            TF_row = row.split(';')
            TF_devs_name.append(TF_row[0])
    
    TF_devs_name.pop(-1) # I delete the last element because it is an empty line
    return TF_devs_name

def extract_stats_TF_developers(owner: str):
    """
    The function returns the list of stats of TF developers
    Args:
        owner(str): the name of the owner of the repository of which we want the stats of the TF developers
    Output:
        TF_devs_name(list): the list contains the stats of TF developers
    """
    TF_report_content = TF_report_reader(owner)
    TF_devs_stats =[]
    row_exceeded = False
    i = 1
    for row in TF_report_content:
        row = row.strip()
        if not row_exceeded:
            if row == ROW_AFTER_TF_DEVS:
                row_exceeded = True
        else:
            print(str(i))
            TF_row = row.split(';')
            TF_stats = {
                'Developer': TF_row[0],
                'Files': TF_row[1],
                'Percentage': TF_row[2]
            }
            TF_devs_stats.append(TF_stats)
            i += 1
    
    TF_devs_stats.pop(-1)
    return TF_devs_stats

def create_TF_devs_names(owner: str):
    """
    The function generates the list of TF developers' stats and saves it to a file
    Args:
        owner(str): the name of the owner of the repository whose file we want to generate TF_devs_names
    """
    TF_devs_stats = extract_stats_TF_developers(owner)
    file_path = get_path_TF_devs_names(owner)
    try:
        with open(file_path, 'w', newline='') as file:
            column_names = ['Developer', 'Files', 'Percentage']
            writer = csv.DictWriter(file, fieldnames=column_names, delimiter=';')
            
            writer.writeheader() 
            
            for tf_dev in TF_devs_stats:
                writer.writerow(tf_dev)
        print("Data successfully written to", file_path)
    except Exception as e:
        print("An error has occurred:", e)





def read_unmasking_results(owner: str):
    """
    The function reads the unmasking_results file
    Args:
        owner(str): the name of the owner of the repository whose unmasking_results file we want to read
    Output:
        devs(list): the list contains the names and logins of every developer who has contributed to the repository
    """
    file_path = get_paht_unmasking_results(owner)
    devs = []
    try:
        with open(file_path, 'r', newline='') as file:
            reader = csv.reader(file, delimiter=';')
            for riga in reader:
                if len(riga) >= 2:  # Assicurati che ci siano almeno 2 valori (name e login) nella riga
                    name = riga[1]
                    login = riga[3]
                    devs.append((name, login))
        return devs
    except FileNotFoundError:
        print("Il file non è stato trovato.")
        return []



def create_list_tf_devs(owner: str):
    """
    The function creates a list formed by the names and logins of the TF developers
    Args:
        owner(str): the name of the owner whose list of TF developers we want
    Output:
        tf_devs(list): list formed by the names and logins of the TF developers
    """
    tf_devs = []
    TF_devs_name = extract_names_TF_developers(owner)
    devs = read_unmasking_results(owner)

    for name_TF in TF_devs_name:
        founded = False
        for name_dev, login in devs:
            if name_TF.lower() == name_dev:
                tf_dev = {
                    'name': name_TF,
                    'login': login
                }
                if not founded:
                    tf_devs.append(tf_dev)
                    founded = True
            else:
                if not founded:
                    words_tf = name_TF.lower().split(' ')
                    correct_name = True
                    for word in words_tf:
                        if not word in name_dev:
                            correct_name = False
                    
                        if not correct_name:
                            break
                    
                    if correct_name:
                        tf_dev = {
                        'name': name_TF,
                        'login': login
                        }
                        tf_devs.append(tf_dev)
                        founded = True
    return tf_devs


import csv

def create_TF_devs(owner: str):
    """
    The function generates the list of TF developers and saves it to a file
    Args:
        owner(str): the name of the owner of the repository whose file we want to generate TF_devs
    """
    file_path = get_path_TF_devs(owner)
    tf_devs = create_list_tf_devs(owner)
    try:
        with open(file_path, 'w', newline='') as file:
            column_names = ['name', 'login']
            writer = csv.DictWriter(file, fieldnames=column_names, delimiter=';')
            
            writer.writeheader() 
            
            for tf_dev in tf_devs:
                writer.writerow(tf_dev)
        print("Data successfully written to", file_path)
    except Exception as e:
        print("An error has occurred:", e)


# Sostituisci 'percorso_del_tuo_file.csv' con il percorso reale del tuo file CSV
if __name__ == "__main__":
    print('Arguments: {} --> {}'.format(len(sys.argv), str(sys.argv)))
    owner = sys.argv[1]
    create_TF_devs(owner)
    create_TF_devs_names(owner)


