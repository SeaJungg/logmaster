from django.shortcuts import render
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import re
import os
from django.core.files.storage import FileSystemStorage
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def index(request):
    return render(request, 'index.html')

def result(request):
    keyword = request.POST.get('keyword', None)
    unit_time = request.POST.get('unitTime', None)
    log_file = request.FILES['uploadFile']
    fs = FileSystemStorage(location='media', base_url='media')
    filename = fs.save(log_file.name, log_file)
    log_file_path = fs.url(filename)
    pltname = getImage(log_file_path, keyword, unit_time)

    return render(request, 'result.html', {'pltname':pltname})

def getImage(log_file_path, keyword, unit_time):
    imageName = datetime.datetime.now().strftime('%H%M%S')
    timeline_and_count = pd.DataFrame(makeSpecificData(BASE_DIR + '/' + log_file_path, keyword, unit_time)).value_counts().rename_axis('timeline').reset_index(name='count')

    if unit_time == 'millisecond':
        #millisecond
        start = datetime.datetime.strptime(timeline_and_count['timeline'].iloc[0], '%Y-%m-%d %H:%M:%S.%f')
        end = datetime.datetime.strptime(timeline_and_count['timeline'].iloc[-1], '%Y-%m-%d %H:%M:%S.%f')
        temp = start
        timeline = []
        while temp < end:
            if len(str(temp))<20:
                timeline.append(str(temp)+ ".0")
            else:
                timeline.append(str(temp)[0:21])
            temp = temp + datetime.timedelta(milliseconds=100)
        print(timeline[0], '\n', timeline[-1])
    elif unit_time == 'second':
        #second
        start = datetime.datetime.strptime(timeline_and_count['timeline'].iloc[0], '%Y-%m-%d %H:%M:%S')
        end = datetime.datetime.strptime(timeline_and_count['timeline'].iloc[-1], '%Y-%m-%d %H:%M:%S')
        temp = start
        timeline = []
        while temp < end:
            if len(str(temp))<20:
                timeline.append(str(temp))
            else:
                timeline.append(str(temp)[0:21])
            temp = temp + datetime.timedelta(seconds=1)
        print(timeline[0],'\n', timeline[-1])
    else:
        print('define unittime_option s or ms')



    count_with_zero_worker1 = []
    for i in timeline:
        if (timeline_and_count['timeline'] == i).any():
            target_count = timeline_and_count.loc[timeline_and_count['timeline'] == i].iloc[0][1]
            count_with_zero_worker1.append(target_count)
        else:
            count_with_zero_worker1.append(0)
    y_worker1_count = count_with_zero_worker1

    fig_worker = plt.gcf()
    fig_worker.set_size_inches(400, 20)

    plt.grid(True, axis='x')
    plt.xticks(fontsize=16, rotation='vertical')
    plt.yticks(fontsize=35)
    plt.bar(timeline, y_worker1_count, color="skyblue")

    plt.savefig( BASE_DIR + '\\static\\' + imageName + '.png', dpi=100)

    return imageName


def makeSpecificData(log_file_path, keyword, unittime_option):
    match_list = []
    if unittime_option == 'millisecond':
        with open(log_file_path, "r") as file:
            confirm_line_print = False
            for line in file:
                for match in re.finditer(keyword, line, re.S):
                    match_text = match.group()
                    splited_line = line.split(':')
                    milisec = splited_line[2][0:4] #100ms단위로 자르기 - 14.487를 14.4로 만들거임
                    match_list.append(splited_line[0]+':'+splited_line[1]+':'+milisec)
                    if(confirm_line_print == False):
                        print('Raw Data with "%s" | ' %keyword, line)
                        confirm_line_print = True
        file.close()
    elif unittime_option == 'second' :
        with open(log_file_path, "r") as file:
            confirm_line_print = False
            for line in file:
                for match in re.finditer(keyword, line, re.S):
                    match_text = match.group()
                    splited_line = line.split(':')
                    sec = splited_line[2][0:2] #1s단위로 자르기 - 14.487를 14로 만들거임
                    match_list.append(splited_line[0]+':'+splited_line[1]+':'+sec)
                    if(confirm_line_print == False):
                        print('Raw Data with "%s" | ' %keyword, line)
                        confirm_line_print = True
        file.close()

    else :
        print('no data with your keyword')
    return match_list