#!/usr/bin/env python
# coding: utf-8

# Import stuff

# In[1]:


import os, sys
import pandas

sys.path.insert(1, 'developersInactivityAnalysis/BreaksManager')
import BreaksManager.BreaksLabeling as BL

from datetime import datetime
import datetime as dt

sys.path.insert(1, 'developersInactivityAnalysis')
import Utilities as util
import Settings as cfg

# Gets the list of breaks from the chosen repo

# In[2]:


def listBreaks(workingFolder, repo, mode):
    organization, project = repo.split('/')
    breaksFolder = os.path.join(workingFolder, organization, cfg.breaks_folder_name, mode.upper())

    repo_Blist = pandas.DataFrame(columns=['dev', 'repo', 'dates', 'len', 'Tfov'])
    for fileName in os.listdir(breaksFolder):
        filePath = os.path.join(breaksFolder, fileName)
        if os.path.isfile(filePath):
            dev = fileName.split('_')[0]
            dev_breaks = pandas.read_csv(filePath, sep=cfg.CSV_separator)
            for i, b in dev_breaks.iterrows():
                util.add(repo_Blist, [dev, repo, b.dates, b.len, b.th])

    return repo_Blist


# Gets the list of NON_CODING breaks from the chosen repo

# In[3]:


def listNonCoding(workingFolder, repo, mode):
    organization, project = repo.split('/')
    breaksFolder = os.path.join(workingFolder, organization, cfg.labeled_breaks_folder_name, mode.upper())

    repo_NClist = pandas.DataFrame(columns=['dev', 'repo', 'dates', 'len', 'Tfov', 'before', 'label', 'after'])
    for fileName in os.listdir(breaksFolder):
        filePath = os.path.join(breaksFolder, fileName)
        if os.path.isfile(filePath):
            dev = fileName.split('_')[0]
            dev_breaks = pandas.read_csv(filePath, sep=cfg.CSV_separator)
            for i, b in dev_breaks[dev_breaks.label == cfg.NC].iterrows():
                end_date = b.dates.split('/')[1]
                for i, ab in dev_breaks[dev_breaks.previously == cfg.NC].iterrows():
                    begin_date = ab.dates.split('/')[0]
                    if begin_date == end_date:
                        after = ab.label
                        util.add(repo_NClist, [dev, repo, b.dates, b.len, b.th, b.previously, b.label, after])
                        break
    return repo_NClist


# Gets the list of INACTIVE breaks from the chosen repo

# In[4]:


def listInactive(workingFolder, repo, mode):
    organization, project = repo.split('/')
    breaksFolder = os.path.join(workingFolder, organization, cfg.labeled_breaks_folder_name, mode.upper())

    repo_Ilist = pandas.DataFrame(columns=['dev', 'repo', 'dates', 'len', 'Tfov', 'previously', 'label', 'after'])
    for fileName in os.listdir(breaksFolder):
        filePath = os.path.join(breaksFolder, fileName)
        if os.path.isfile(filePath):
            dev = fileName.split('_')[0]
            dev_breaks = pandas.read_csv(filePath, sep=cfg.CSV_separator)
            for i, b in dev_breaks[dev_breaks.label == cfg.I].iterrows():
                end_date = b.dates.split('/')[1]
                for i, ab in dev_breaks[dev_breaks.previously == cfg.I].iterrows():
                    begin_date = ab.dates.split('/')[0]
                    if begin_date == end_date:
                        after = ab.label
                        util.add(repo_Ilist, [dev, repo, b.dates, b.len, b.th, b.previously, b.label, after])
                        break
    return repo_Ilist


# Gets the list of GONE from the chosen repo

# In[5]:


def listGone(workingFolder, repo, mode):
    organization, project = repo.split('/')
    breaksFolder = os.path.join(workingFolder, organization, cfg.labeled_breaks_folder_name, mode.upper())
    print(breaksFolder)
    repo_Glist = pandas.DataFrame(columns=['dev', 'repo', 'dates', 'len', 'Tfov', 'previously', 'label', 'after'])
    #print(os.listdir(breaksFolder))
    for fileName in os.listdir(breaksFolder):
        filePath = os.path.join(breaksFolder, fileName)
        if os.path.isfile(filePath):
            dev = fileName.split('_')[0]
            dev_breaks = pandas.read_csv(filePath, sep=cfg.CSV_separator)
            for i, b in dev_breaks[dev_breaks.label == cfg.G].iterrows():
                end_date = b.dates.split('/')[1]
                for i, ab in dev_breaks[dev_breaks.previously == cfg.G].iterrows():
                    begin_date = ab.dates.split('/')[0]
                    if begin_date == end_date:
                        after = ab.label
                        util.add(repo_Glist, [dev, repo, b.dates, b.len, b.th, b.previously, b.label, after])
                        break
    
    return repo_Glist


# Prints the list of Sub-breaks from the given Break

# In[6]:


def analyzeLongBreak(repo, dev, targetBreakDates, targetBreakTfov):
    organization, project = repo.split('/')
    workingFolder = os.path.join(cfg.main_folder, organization)
    actionsFolder = os.path.join(workingFolder, cfg.actions_folder_name)

    devActionsFile = '{}_actions_table.csv'.format(dev)
    if devActionsFile in actionsFolder:
        user_actions = pandas.read_csv(actionsFolder + '/' + devActionsFile, sep=cfg.CSV_separator)
    else:
        user_actions = BL.get_activities(workingFolder, dev)

    # CHECK ACTIVITIES
    threshold = targetBreakTfov
    break_range = targetBreakDates.split('/')
    inner_start = (datetime.strptime(break_range[0], "%Y-%m-%d") + dt.timedelta(days=1)).strftime("%Y-%m-%d")
    inner_end = (datetime.strptime(break_range[1], "%Y-%m-%d") - dt.timedelta(days=1)).strftime("%Y-%m-%d")

    break_actions = user_actions.loc[:, inner_start:inner_end]  # Gets only the chosen period

    break_actions = break_actions.loc[~(break_actions == 0).all(axis=1)]  # Removes the actions not performed

    is_activity_day = (break_actions != 0).any()  # List Of Columns With at least a Non-Zero Value
    action_days = is_activity_day.index[is_activity_day].tolist()  # List Of Columns NAMES Having Column Names at least a Non-Zero Value

    if len(break_actions) > 0:  # There are other activities: the Break is Non-coding
        break_detail = BL.splitBreak(targetBreakDates, action_days, threshold)
        print('Break Detail: \n', break_detail)
        #actions_detail = break_actions[action_days[1:-1]]  # splitBreak() has added the commit days, thus I exclude them here
        #print('Break Actions: \n', actions_detail)
    else:
        print('NONE')


# MAIN FUNCTION

# In[7]:


### ARGUMENTS MANAGEMENT
if __name__ == "__main__":
    mode = 'A80API'
    repos_list = util.getReposList()

    workingDir = os.path.join(cfg.main_folder)
    BreaksList = pandas.DataFrame(columns=['dev', 'repo', 'dates', 'len', 'Tfov'])
    NClist = pandas.DataFrame(columns=['dev', 'repo', 'dates', 'len', 'Tfov', 'previously', 'label', 'after'])
    Ilist = pandas.DataFrame(columns=['dev', 'repo', 'dates', 'len', 'Tfov', 'previously', 'label', 'after'])
    Glist = pandas.DataFrame(columns=['dev', 'repo', 'dates', 'len', 'Tfov', 'previously', 'label', 'after'])

    for repo in repos_list:
        repo_Blist = listBreaks(workingDir, repo, mode)
        BreaksList = pandas.concat([BreaksList, repo_Blist], ignore_index=True)


        repo_NClist = listNonCoding(workingDir, repo, mode)
        NClist = pandas.concat([NClist, repo_NClist], ignore_index=True)

        repo_Ilist = listInactive(workingDir, repo, mode)
        Ilist = pandas.concat([Ilist, repo_Ilist], ignore_index=True)

        repo_Glist = listGone(workingDir, repo, mode)
        #print(repo_Glist)
        Glist = pandas.concat([Glist, repo_Glist], ignore_index=True)
        #print(Glist)

        print(repo, 'DONE!')

    outputFileName = os.path.join(workingDir, mode.upper(), 'Breaks_full_list.csv')
    #print(BreaksList)
    BreaksList.to_csv(outputFileName,
                sep=cfg.CSV_separator, na_rep=cfg.CSV_missing, index=False, quoting=None, line_terminator='\n')
    
    outputFileName = os.path.join(workingDir, mode.upper(), 'NC_full_list.csv')
    NClist.to_csv(outputFileName,
                    sep=cfg.CSV_separator, na_rep=cfg.CSV_missing, index=False, quoting=None, line_terminator='\n')
    
    outputFileName = os.path.join(workingDir, mode.upper(), 'I_full_list.csv')
    Ilist.to_csv(outputFileName,
                    sep=cfg.CSV_separator, na_rep=cfg.CSV_missing, index=False, quoting=None, line_terminator='\n')
    
    outputFileName = os.path.join(workingDir, mode.upper(), 'G_full_list.csv')
    Glist.to_csv(outputFileName,
                    sep=cfg.CSV_separator, na_rep=cfg.CSV_missing, index=False, quoting=None, line_terminator='\n')


    # In[26]:


    #analyzeLongBreak('atom/atom', 'jasonrudolph', '2015-02-20/2017-04-04', 46)
