import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import timedelta, date
#import seaborn as sns
import os

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

def extract_by_city(df_in, cityName, calc_increment = True, debug = False):
    df_1 = df_in[df_in['cityName'] == cityName]

    if debug:
        print(df_1.columns)
    subset_labels = ['provinceName', 'cityName',
       'city_confirmedCount', 'city_suspectedCount', 'city_curedCount',
       'city_deadCount', 'updateTime']
    indices = [df_1.columns.get_loc(egg) for egg in subset_labels]
    if debug:
        print(indices)

    df_2 = df_1.iloc[::-1, indices]
    if debug:
        print(df_2.columns)
        #print(df_2)

    df_3 = select_record_until_certain_time_on_each_day(df_2)
    if debug:
        #print(df_3.columns)
        print(df_3)

    datetimes = pd.to_datetime(df_3.loc[:, 'updateTime'])

    dates = [row[1].date() for row in datetimes.items()]

    df_4 = df_3.rename(columns={'updateTime': 'updateDate'})
    df_4.loc[:, 'updateDate'] = dates
    
    if calc_increment:
        df_4['city_confirmedCountIncrement'] = df_4['city_confirmedCount']
        idx_tmp1 = df_4.columns.get_loc('city_confirmedCountIncrement')
        idx_tmp2 = df_4.columns.get_loc('city_confirmedCount')
        df_4.iloc[0, idx_tmp1] = 0
        if df_4.shape[0] > 1:
            for i_row in range(1, df_4.shape[0]):
                df_4.iloc[i_row, idx_tmp1] = df_4.iloc[i_row, idx_tmp2] - df_4.iloc[i_row - 1, idx_tmp2]

        df_4['city_curedCountIncrement'] = df_4['city_curedCount']
        idx_tmp1 = df_4.columns.get_loc('city_curedCountIncrement')
        idx_tmp2 = df_4.columns.get_loc('city_curedCount')
        df_4.iloc[0, idx_tmp1] = 0
        if df_4.shape[0] > 1:
            for i_row in range(1, df_4.shape[0]):
                df_4.iloc[i_row, idx_tmp1] = df_4.iloc[i_row, idx_tmp2] - df_4.iloc[i_row - 1, idx_tmp2]

        df_4['city_deadCountIncrement'] = df_4['city_deadCount']
        idx_tmp1 = df_4.columns.get_loc('city_deadCountIncrement')
        idx_tmp2 = df_4.columns.get_loc('city_deadCount')
        df_4.iloc[0, idx_tmp1] = 0
        if df_4.shape[0] > 1:
            for i_row in range(1, df_4.shape[0]):
                df_4.iloc[i_row, idx_tmp1] = df_4.iloc[i_row, idx_tmp2] - df_4.iloc[i_row - 1, idx_tmp2]
                
    if debug:
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
    
    path_figure_cities = os.path.join(os.getcwd(), 'figures')
    if (not os.path.exists(path_figure_cities)):
        os.mkdir(path_figure_cities)

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
        fn_tmp = os.path.join(path_figure_cities, \
            '累计确诊数-{:s}-{:s}.png'.format(provinceName, cityName))
        plt.savefig(fn_tmp, dpi = 100)
    if show:
        plt.show()
    plt.close()

    fig, ax = plt.subplots()
    ax.plot(df_tmp['updateDate'], df_tmp['city_confirmedCountIncrement'], '.-', label = cityName)

    ax.xaxis.set_major_formatter(hfmt)
    plt.legend()
    plt.ylabel('单日新增确诊数')
    ylims = ax.get_ylim()
    ax.set_ylim([0, ylims[1]])
    if savefig:
        fn_tmp = os.path.join(path_figure_cities,\
            '单日新增确诊数-{:s}-{:s}.png'.format(provinceName, cityName))
        plt.savefig(fn_tmp, dpi = 100)
    if show:
        plt.show()
    plt.close()

    return

def plot_province_dataframe_by_matplot(df_in, provinceName, show = False, savefig = True):
    
    path_figure_cities = os.path.join(os.getcwd(), 'figures')
    if (not os.path.exists(path_figure_cities)):
        os.mkdir(path_figure_cities)

    # matplotlib date format object
    hfmt = mpl.dates.DateFormatter('%m/%d')

    columnNames = ['province_confirmedCount', 'province_confirmedCountIncrement', \
        'province_curedCount', 'province_curedCountIncrement', \
        'province_deadCount', 'province_deadCountIncrement']
    columnChineseNames = ['累计确诊数', '单日新增确诊数', '累计治愈数', \
        '单日新增治愈数', '累计死亡数', '单日新增死亡数']

    nColumnName = len(columnNames)
    for iCol in range(nColumnName):
        fig, ax = plt.subplots()
        ax.plot(df_in['updateDate'], df_in[columnNames[iCol]], '.-', label = provinceName)

        ax.xaxis.set_major_formatter(hfmt)
        plt.legend()
        #plt.xlabel('日期')
        plt.ylabel(columnChineseNames[iCol])
        ylims = ax.get_ylim()
        ax.set_ylim([0, ylims[1]])

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()

        if savefig:
            fn_tmp = '{:s}-{:s}.png'.format(columnChineseNames[iCol], provinceName)
            plt.savefig(fn_tmp, dpi = 300)
        if show:
            plt.show()
        plt.close()

    return

def plot_datasets_by_matplot(dat_in, cityNames, show = False, savefig = True):
    nDat = len(dat_in)
    
    # matplotlib date format object
    hfmt = mpl.dates.DateFormatter('%m/%d')

    columnNames = ['city_confirmedCount', 'city_confirmedCountIncrement', \
        'city_curedCount', 'city_curedCountIncrement', \
        'city_deadCount', 'city_deadCountIncrement']
    columnChineseNames = ['累计确诊数', '单日新增确诊数', '累计治愈数', \
        '单日新增治愈数', '累计死亡数', '单日新增死亡数']

    nColumnName = len(columnNames)
    for iCol in range(nColumnName):
        fig, ax = plt.subplots()
        for i in range(nDat):
            df_tmp = dat_in[i]
            ax.plot(df_tmp['updateDate'], df_tmp[columnNames[iCol]], '.-', label = cityNames[i])

        ax.xaxis.set_major_formatter(hfmt)
        plt.legend()
        #plt.xlabel('日期')
        plt.ylabel(columnChineseNames[iCol])
        ylims = ax.get_ylim()
        ax.set_ylim([0, ylims[1]])

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()
        
        if savefig:
            plt.savefig(columnChineseNames[iCol]+'.png', dpi = 300)
        if show:
            plt.show()
        plt.close()
    
    if savefig:
        print('已保存趋势图至本目录：')
        for iCol in range(nColumnName):
            print('{:d}. {:s}.png'.format(iCol+1, columnChineseNames[iCol]))

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

        dates = df_tmp['updateDate'].unique()
        nDate = len(dates)

        dfProvince_tmp = pd.DataFrame({'provinceName': provinceNames[i], \
            'updateDate': dates})

        columnNamesForSum = ['confirmedCount', 'confirmedCountIncrement', \
            'curedCount', 'curedCountIncrement', 'deadCount', 'deadCountIncrement']

        for iCol in range(len(columnNamesForSum)):
            columnName = columnNamesForSum[iCol]
            cityColumnName = 'city_'+columnName
            provinceColumnName = 'province_'+columnName

            sumInProvince = np.zeros([nDate], dtype = 'int')

            for iDate in range(nDate):
                dfInDay_tmp = df_tmp[df_tmp['updateDate'] == dates[iDate]]                
                sumInProvince[iDate] = dfInDay_tmp[cityColumnName].sum()


            dfProvince_tmp[provinceColumnName] = sumInProvince

        dfProvince_tmp = dfProvince_tmp.sort_values(by='updateDate')
        #print(dfProvince_tmp)
        plot_province_dataframe_by_matplot(dfProvince_tmp, provinceNames[i])
    return

