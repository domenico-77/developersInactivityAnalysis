import sys, os
import pandas
from github import Github

sys.path.insert(1, 'developersInactivityAnalysis')
import Utilities as util

### MAIN FUNCTION
def main(repoName, token):
    organization, repository = repoName.split('/')
    # TODO '../A80_Results/' should be a parameter
    sourceFolder = '../A80_Results/' + repository
    devsFilePath = os.path.join(sourceFolder, 'Cstats.csv')

    devs = pandas.read_csv(devsFilePath, sep=';')

    devs_map = pandas.DataFrame(columns=['name', 'email', 'login', 'commits'])

    g = Github(token)
    try:
        g.get_rate_limit()
    except Exception as e:
        print('Exception {}'.format(e))
        return
    g.per_page = 100

    repo = g.get_repo(repoName)
    contributors = repo.get_contributors()

    for contributor in contributors:
        login = contributor.login.lower()
        dev_name = contributor.name
        dev_email = contributor.email
        if dev_name is not None:
            dev_name = dev_name.lower()
            for name in devs['name'].tolist():
                if dev_name == name:
                    aliases = devs[devs['name']==name]
                    for i, a in aliases.iterrows():
                        if a['name'] not in devs_map['name'].tolist():
                            rec = [a['name'], a['email'], login, a['commits']]
                            util.add(devs_map, rec)
                            print('Dev Login Found from NAME: ', rec)
        for name in devs['name'].tolist():
            if login == name:
                aliases = devs[devs['name']==login]
                for i, a in aliases.iterrows():
                    if a['name'] not in devs_map['name'].tolist():
                        rec = [a['name'], a['email'], login, a['commits']]
                        util.add(devs_map, rec)
                        print('Dev Login Found from LOGIN: ', rec)
        if dev_email is not None:
            dev_email = dev_email.lower()
            for email in devs['email'].tolist():
                if dev_email == email:
                    aliases = devs[devs['email']==email]
                    for i, a in aliases.iterrows():
                        if a['email'] not in devs_map['email'].tolist():
                            rec = [a['name'], a['email'], login, a['commits']]
                            util.add(devs_map, rec)
                            print('Dev Login Found from EMAIL: ', rec)

    for i, dev in devs.iterrows():
        if dev['name'] not in devs_map['name'].tolist() or dev['email'] not in devs_map['email'].tolist():
            rec = [dev['name'], dev['email'], None, dev['commits']]
            util.add(devs_map, rec)
            print('Dev Login Not Found: ', rec)

    devs_map.to_csv(os.path.join(sourceFolder, 'login_map.csv'),
                             sep=';', na_rep='N/A', index=True, index_label='id', quoting=None, line_terminator='\n')

if __name__ == "__main__":
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    os.chdir(THIS_FOLDER)

    ### ARGUMENTS MANAGEMENT
    # python script.py repoName(format: organization/project) tokenNumber
    print('Arguments: {} --> {}'.format(len(sys.argv), str(sys.argv)))
    repoName = sys.argv[1]
    try:
        token = util.getToken(int(sys.argv[2]))
    except:
        token = sys.argv[2]
        pass
    main(repoName, token)
