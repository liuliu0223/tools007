from urllib.request import urlopen
import json
import subprocess, shlex
import time
import os

gitlabToken = '自己gitlab的token'  # 自己gitlab上的tokne
gitlabAddr = '地址'  # gitlab地址名
#注意：去掉https: //
target = 'group name'  # 项目分组名 ， 为空则下载整个gitlab代码，慎用！


def getUrls(file_name):
    file = None
    try:
        path = os.path.join(os.getcwd(), file_name)
        print(path + '\n')
        file = open(path, encoding='utf-8')
        return file.readlines()
    finally:
        file.close()


def getToken(filename):
    fileobj = getUrls(filename)
    token = ""
    if fileobj is None:
        print("Please Check the Titlefile, there is error url!")
    else:
        tmp_token = fileobj[0].split("=")
        token = tmp_token[1]
    return token


def get_next(group_id):
    url = gen_next_url(group_id)
    allProjects = urlopen(url)
    allProjectsDict = json.loads(allProjects.read().decode())
    thisProjectURL = ""
    resultCode = None
    if len(allProjectsDict) == 0:
        return
    for thisProject in allProjectsDict:
        try:
            thisProjectURL = thisProject['ssh_url_to_repo']
            thisProjectPath = thisProject['path_with_namespace']
            if os.path.exists(thisProjectPath):
                command = shlex.split('git -C "%s" pull' % (thisProjectPath))
            else:
                command = shlex.split('git clone %s %s' % (thisProjectURL, thisProjectPath))
            resultCode = subprocess.Popen(command)
            time.sleep(1)
        except Exception as e:
            print("Error on %s" % (thisProjectURL))
            print("Unexception Error:{}".format(e))
    return resultCode


def have_next_projects(group_id):
    url = gen_next_url(group_id)
    allProjects = urlopen(url)
    allProjectsDict = json.loads(allProjects.read().decode())
    if len(allProjectsDict) == 0:
        return False
    return True


def get_sub_groups(parent_id):
    url = gen_subgroups_url(parent_id)
    allProjects = urlopen(url)
    allProjectsDict = json.loads(allProjects.read().decode())
    sub_ids = []
    id = ""
    if len(allProjectsDict) == 0:
        return sub_ids
    for thisProject in allProjectsDict:
        try:
            id = thisProject['id']
            sub_ids.append(id)
        except Exception as e:
            print("Error on %s" % (id))
            print("Unexception Error:{}".format(e))
    return sub_ids


def cal_next_sub_groupids(parent_id):
    parent = ''
    parent = parent_id
    is_start = 1
    parent_list = []
    sub_ids = get_sub_groups(parent_id)
    ok = have_next_projects(parent_id)
    if len(sub_ids) != 0 and ok == False:
        for i in range(len(sub_ids)):
            print(sub_ids[i])
            parent = sub_ids[i]
            a = cal_next_sub_groupids(sub_ids[i])
            return a
    if len(sub_ids) != 0 and ok == True:
        for i in range(len(sub_ids)):
            parent = sub_ids[i]
            parent_list.append(sub_ids[i])
            a = cal_next_sub_groupids(sub_ids[i])
            parent_list.extend(a)
    if len(sub_ids) == 0 and ok == True:
        parent_list.append(parent)
        return parent_list
    if len(sub_ids) == 0 and ok == False:
        return parent_list
    return parent_list


def download_code(parent_id):
    data = cal_next_sub_groupids(parent_id)
    for group_id in data:
        get_next(group_id)
    return


def gen_next_url(target_id):
    return "https://%s/api/v4/groups/%s/projects?private_token=%s" % (gitlabAddr, target_id, gitlabToken)


def gen_subgroups_url(target_id):
    return "https://%s/api/v4/groups/%s/subgroups?private_token=%s" % (gitlabAddr, target_id, gitlabToken)


def gen_global_url():
    return "http://%s/api/v4/projects?private_token=%s" % (gitlabAddr, gitlabToken)


def download_global_code():
    url = gen_global_url()
    allProjects = urlopen(url)
    allProjectsDict = json.loads(allProjects.read().decode())
    thisProjectURL = ""
    if len(allProjectsDict) == 0:
        return
    for thisProject in allProjectsDict:
        try:
            thisProjectURL = thisProject['ssh_url_to_repo']
            thisProjectPath = thisProject['path_with_namespace']
            print(thisProjectURL + ' ' + thisProjectPath)

            if os.path.exists(thisProjectPath):
                command = shlex.split('git -C "%s" pull' % (thisProjectPath))
            else:
                command = shlex.split('git clone %s %s' % (thisProjectURL, thisProjectPath))

            resultCode = subprocess.Popen(command)
            print(resultCode)
            time.sleep(1)
        except Exception as e:
            print("Error on %s" % (thisProjectURL))
            print("Unexception Error:{}".format(e))
    return


def main():
    filename = "Titles.txt"
    base_path = os.getcwd()

    fileobj = getUrls(filename)
    if fileobj is None:
        print("Please Check the Titlefile, there is error url!")
    else:
        tmp_token = fileobj[0].split("=")
        gitlabToken = getToken(tmp_token[1])
        tmp_groupname = fileobj[1].split("=")
        target = tmp_groupname[1]

        it = 2
        while it < len(fileobj):
            this_name = ""
            if target == '':
                download_global_code()
            else:
                gitlabAddr_list = fileobj[it].split("=")
                url = "https://%s/api/v4/groups?private_token=%s" % (gitlabAddr_list[1], gitlabToken)
                allProjects = urlopen(url)
                allProjectsDict = json.loads(allProjects.read().decode())
                if len(allProjectsDict) == 0:
                    return
                target_id = ''
                for thisProject in allProjectsDict:
                    try:
                        this_name = thisProject['name']
                        if target == this_name:
                            target_id = thisProject['id']
                            break
                    except Exception as e:
                        print("Error on %s:" % (this_name))
                        print("Unexception Error:{}".format(e))
                download_code(target_id)
                it = it + 1
        return


main()


