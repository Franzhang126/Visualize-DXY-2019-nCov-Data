import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import timedelta, date
import seaborn as sns

mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['SimHei'] # 'Arial'

mpl.rcParams['xtick.labelsize'] = 12
mpl.rcParams['ytick.labelsize'] = 12
mpl.rcParams['legend.fontsize'] = 12
mpl.rcParams['axes.labelsize'] = 12

mpl.rcParams['xtick.direction'] = 'in'
mpl.rcParams['ytick.direction'] = 'in'

#sns.set()

def select_record_until_certain_time_in_one_day(times_in, hour_target, minute_target):
    deltas = [[egg[0], timedelta(hours = hour_target - egg[1], minutes = minute_target - egg[2]).seconds] for egg in times_in]
    deltas = np.array(deltas)

    i2_min_tmp = -1
    delta_min = 99999999
    for i2 in range(deltas.shape[0]):
        delta_tmp = deltas[i2, :]
        if delta_tmp[1] > 0 and delta_tmp[1] < delta_min:
            i2_min_tmp = i2
            delta_min = delta_tmp[1]
    
    return deltas[i2_min_tmp, 0]

def select_record_until_certain_time_on_each_day(dat_in, hour_target = 12, minute_target = 0, key = 'updateTime'):
    indices_tmp = []
    
    datetime_old = pd.to_datetime(dat_in.iat[0, 6])
    day_old = datetime_old.day
    
    hour_old = datetime_old.hour
    minute_old = datetime_old.minute
    times_in_day = [[0, hour_old, minute_old]]
    
    #print([day_old, hour_old, minute_old])    
    
    for i in range(1, dat_in.shape[0]):
        datetime_tmp = pd.to_datetime(dat_in.iat[i, 6])
        #print(datetime_tmp)
        
        day_tmp, hour_tmp, minute_tmp = datetime_tmp.day, datetime_tmp.hour, datetime_tmp.minute
        
        if day_tmp == day_old:
            #print('Append')
            times_in_day.append([i, hour_tmp, minute_tmp])        
        else:
            #print('Select')
            index_tmp = select_record_until_certain_time_in_one_day(times_in_day, hour_target, minute_target)            
            indices_tmp.append(index_tmp)
            
            day_old = day_tmp
            times_in_day = [[i, hour_tmp, minute_tmp]]
            
    #print('Finalize')
    index_tmp = select_record_until_certain_time_in_one_day(times_in_day, hour_target, minute_target)            
    indices_tmp.append(index_tmp)
    
    return dat_in.iloc[indices_tmp, :]

def extract_by_city(df_in, cityName, calc_increment = True, print = False):
    df_1 = df_in[df_in['cityName'] == cityName]

    df_2 = df_1.iloc[::-1, [0,1,6,7,8,9,10]]
    #print(df_2.columns)
    #print(df_2)

    df_3 = select_record_until_certain_time_on_each_day(df_2)
    #print(df_3.columns)
    #print(df_3)

    datetimes = pd.to_datetime(df_3.loc[:, 'updateTime'])

    dates = [row[1].date() for row in datetimes.items()]

    df_4 = df_3.rename(columns={'updateTime': 'updateDate'})
    df_4.loc[:, 'updateDate'] = dates
    
    if calc_increment:
        df_4['confirmedIncrement'] = df_4['city_confirmedCount']
        df_4.iloc[0, 7] = 0
        if df_4.shape[0] > 1:
            for i_row in range(1, df_4.shape[0]):
                df_4.iloc[i_row, 7] = df_4.iloc[i_row, 2] - df_4.iloc[i_row - 1, 2]
                
    if print:
        print(df_4)
    
    return df_4

def extract_by_province(df_in, provinceName, calc_increment = True):
    df_1 = df_in[df_in['provinceName'] == provinceName]
    #print(df_1)

    #print(df_1['cityName'])
    #print(df_1['cityName'].unique())
    cityNames = df_1['cityName'].unique()
    nCity = len(cityNames)
    datasetsInProvince = []
    for i in range(nCity):
        datasetsInProvince.append(extract_by_city(df_in, cityNames[i]))
    dfInProvince = pd.concat(datasetsInProvince)
    #print(dfInProvince)

    return dfInProvince

def plot_city_dataset_by_matplot(df_in, provinceName, cityName, show = False, savefig = True):
    df_tmp = df_in[df_in['cityName'] == cityName]

    # matplotlib date format object
    hfmt = mpl.dates.DateFormatter('%m/%d')

    fig, ax = plt.subplots()
    ax.plot(df_tmp['updateDate'], df_tmp['city_confirmedCount'], '.-', label = cityName)

    ax.xaxis.set_major_formatter(hfmt)
    plt.legend()
    #plt.xlabel('日期')
    plt.ylabel('累计确诊数')
    ylims = ax.get_ylim()
    ax.set_ylim([0, ylims[1]])
    if savefig:
        plt.savefig('累计确诊数-{:s}-{:s}.png'.format(provinceName, cityName), dpi = 100)
    if show:
        plt.show()
    plt.close()

    fig, ax = plt.subplots()
    ax.plot(df_tmp['updateDate'], df_tmp['confirmedIncrement'], '.-', label = cityName)

    ax.xaxis.set_major_formatter(hfmt)
    plt.legend()
    plt.ylabel('单日新增确诊数')
    ylims = ax.get_ylim()
    ax.set_ylim([0, ylims[1]])
    if savefig:
        plt.savefig('单日新增确诊数-{:s}-{:s}.png'.format(provinceName, cityName), dpi = 300)
    if show:
        plt.show()
    plt.close()

    return

def plot_datasets_by_matplot(dat_in, cityNames, show = False, savefig = True):
    nDat = len(dat_in)
    
    # matplotlib date format object
    hfmt = mpl.dates.DateFormatter('%m/%d')

    fig, ax = plt.subplots()
    for i in range(nDat):
        df_tmp = dat_in[i]
        ax.plot(df_tmp['updateDate'], df_tmp['city_confirmedCount'], '.-', label = cityNames[i])

    ax.xaxis.set_major_formatter(hfmt)
    plt.legend()
    #plt.xlabel('日期')
    plt.ylabel('累计确诊数')
    ylims = ax.get_ylim()
    ax.set_ylim([0, ylims[1]])
    if savefig:
        plt.savefig('累计确诊数.png', dpi = 300)
    if show:
        plt.show()
    plt.close()

    fig, ax = plt.subplots()
    for i in range(nDat):
        df_tmp = dat_in[i]
        ax.plot(df_tmp['updateDate'], df_tmp['confirmedIncrement'], '.-', label = cityNames[i])

    ax.xaxis.set_major_formatter(hfmt)
    plt.legend()
    plt.ylabel('单日新增确诊数')
    ylims = ax.get_ylim()
    ax.set_ylim([0, ylims[1]])
    if savefig:
        plt.savefig('单日新增确诊数.png', dpi = 300)
    if show:
        plt.show()
    plt.close()
    
    if savefig:
        print('已保存趋势图至本目录：\n1.累计确诊数.png\n2.单日新增确诊数.png')

    return

def visualize_area_data_by_city(fn_csv, cityNames):
    df_orig = pd.read_csv(fn_csv)

    nCity = len(cityNames)

    datasets = []
    for i in range(nCity):
        df_tmp = extract_by_city(df_orig, cityNames[i])
        datasets.append(df_tmp)

    plot_datasets_by_matplot(datasets, cityNames)
    return

def visualize_area_data_by_province(fn_csv, provinceNames = None):
    df_orig = pd.read_csv(fn_csv)
    #print(df_orig.columns)

    if provinceNames is None:
        provinceNames = df_orig['provinceName'].unique()
    nProvince = len(provinceNames)

    datasets = []
    for i in range(nProvince):
        df_tmp = extract_by_province(df_orig, provinceNames[i])
        datasets.append(df_tmp)

        cityNames = df_tmp['cityName'].unique()
        nCity = len(cityNames)

        for iCity in range(nCity):
            print('Plotting {:s} {:s}'.format(provinceNames[i], cityNames[iCity]))
            plot_city_dataset_by_matplot(df_tmp, provinceNames[i], cityNames[iCity])
    return

