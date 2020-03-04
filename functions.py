import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import timedelta, date
#import seaborn as sns
import os

mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei'] # 'Arial', 'SimHei'

mpl.rcParams['xtick.labelsize'] = 12
mpl.rcParams['ytick.labelsize'] = 12
mpl.rcParams['legend.fontsize'] = 12
mpl.rcParams['axes.labelsize'] = 12

mpl.rcParams['xtick.direction'] = 'in'
mpl.rcParams['ytick.direction'] = 'in'

# 'ZH' for Chinese Simplified (简体中文), 'EN' for English.
_language = 'ZH'
key_cityName = 'cityName'
key_provinceName = 'provinceName'

#sns.set()

def test_language(num = 0):
    print(str(num) + ' ' + _language)

def set_language(language_target):
    global _language, key_cityName, key_provinceName
    global label_latestValue, label_confirmedCount, label_confirmedCountIncrement
    global label_curedCount, label_curedCountIncrement, label_deadCount, label_deadCountIncrement
    global label_mostSeriousCity

    _language = language_target

    if _language == 'ZH':
        key_cityName = 'cityName'
        key_provinceName = 'provinceName'
        label_latestValue = '最新值'
        label_confirmedCount = '累计确诊数'
        label_confirmedCountIncrement = '单日新增确诊数'
        label_curedCount = '累计治愈数'
        label_curedCountIncrement = '单日新增治愈数'
        label_deadCount = '累计死亡数'
        label_deadCountIncrement = '单日新增死亡数'
        label_mostSeriousCity = '最严重城市'
    elif _language == 'EN':
        key_cityName = 'cityEnglishName'
        key_provinceName = 'provinceEnglishName'
        label_latestValue = 'today:'
        label_confirmedCount = 'count of confirmed case'
        label_confirmedCountIncrement = 'daily increment of confirmed count'
        label_curedCount = 'count of cured case'
        label_curedCountIncrement = 'daily increment of cured case'
        label_deadCount = 'count of dead case'
        label_deadCountIncrement = 'daily increment of dead case'
        label_mostSeriousCity = 'most serious city'
    else:
        raise ValueError('Language type not implemented yet: ' + language_target)

    return


def autolabel(rects, ax):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

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

def select_record_until_certain_time_on_each_day(dat_in, hour_target = 23, minute_target = 0, key = 'updateTime'):
    '''
    There may be multiple record for the city in one day.
    We select the latest record until our target moment (at hour_target:minute_target) on that day.
    '''
    indices_tmp = []
    
    colIndexUpdateTime = dat_in.columns.get_loc('updateTime')
    datetime_old = pd.to_datetime(dat_in.iat[0, colIndexUpdateTime])
    day_old = datetime_old.day
    
    hour_old = datetime_old.hour
    minute_old = datetime_old.minute
    times_in_day = [[0, hour_old, minute_old]]
    
    #print([day_old, hour_old, minute_old])    
    
    for i in range(1, dat_in.shape[0]):
        datetime_tmp = pd.to_datetime(dat_in.iat[i, colIndexUpdateTime])
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
    df_1 = df_in[df_in[key_cityName] == cityName]
    if debug:
        print(cityName)
        print(df_1.columns)
        #print(df_1.to_string())

    if len(df_1.index) > 0:
        subset_labels = [key_provinceName, key_cityName,
           'city_confirmedCount', 'city_suspectedCount', 'city_curedCount',
           'city_deadCount', 'updateTime']
        indices = [df_1.columns.get_loc(egg) for egg in subset_labels]
        if debug:
            print(indices)

        df_2 = df_1.iloc[::-1, indices]
        if debug:
            print(df_2.columns)
            print(df_2.to_string())

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
    else:
        # return a zero-row DataFrame.
        return df_1

def extract_by_province(df_in, provinceName, calc_increment = True):
    df_1 = df_in[df_in[key_provinceName] == provinceName]
    #print(df_1)

    #print(df_1['cityName'])
    #print(df_1['cityName'].unique())
    cityNames = df_1[key_cityName].unique()
    nCity = len(cityNames)
    datasetsInProvince = []
    for i in range(nCity):
        df_tmp = extract_by_city(df_in, cityNames[i])
        if len(df_tmp.index) > 0:
            datasetsInProvince.append(df_tmp)
    dfInProvince = pd.concat(datasetsInProvince)
    #print(dfInProvince)

    return dfInProvince

def plot_city_dataset_by_matplot(df_in, provinceName, cityName, show = False, savefig = True):
    
    path_figure_cities = os.path.join(os.getcwd(), 'figures')
    if (not os.path.exists(path_figure_cities)):
        os.mkdir(path_figure_cities)

    df_tmp = df_in[df_in[key_cityName] == cityName]

    # matplotlib date format object
    hfmt = mpl.dates.DateFormatter('%m/%d')

    fig, ax = plt.subplots()
    x_tmp, y_tmp = df_tmp['updateDate'], df_tmp['city_confirmedCount']    
    ax.plot(x_tmp, y_tmp, '.-', label = cityName + '({:s} {:d})'.format(\
        label_latestValue, y_tmp.iloc[-1]))

    ax.xaxis.set_major_formatter(hfmt)
    plt.legend()
    #plt.xlabel('日期')
    plt.ylabel(label_confirmedCount)
    ylims = ax.get_ylim()
    ax.set_ylim([0, ylims[1]])

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()

    if savefig:
        fn_tmp = os.path.join(path_figure_cities, \
            '{:s}-{:s}-{:s}.png'.format(label_confirmedCount, provinceName, cityName))
        plt.savefig(fn_tmp, dpi = 100)
    if show:
        plt.show()
    plt.close()

    fig, ax = plt.subplots()
    x_tmp, y_tmp = df_tmp['updateDate'], df_tmp['city_confirmedCountIncrement']
    ax.plot(x_tmp, y_tmp, '.-', label = cityName + '({:s} {:d})'.format(\
        label_latestValue, y_tmp.iloc[-1]))

    ax.xaxis.set_major_formatter(hfmt)
    plt.legend()
    plt.ylabel(label_confirmedCountIncrement)
    ylims = ax.get_ylim()
    ax.set_ylim([0, ylims[1]])

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()
    
    if savefig:
        fn_tmp = os.path.join(path_figure_cities,\
            '{:s}-{:s}-{:s}.png'.format(label_confirmedCountIncrement, provinceName, cityName))
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
    columnDisplayNames = [label_confirmedCount, label_confirmedCountIncrement, \
        label_curedCount, label_curedCountIncrement, \
        label_deadCount, label_deadCountIncrement]

    nColumnName = len(columnNames)
    for iCol in range(nColumnName):
        fig, ax = plt.subplots()
        ax.plot(df_in['updateDate'], df_in[columnNames[iCol]], '.-', label = provinceName)

        ax.xaxis.set_major_formatter(hfmt)
        plt.legend()
        #plt.xlabel('日期')
        plt.ylabel(columnDisplayNames[iCol])
        ylims = ax.get_ylim()
        ax.set_ylim([0, ylims[1]])

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()

        if savefig:
            fn_tmp = '{:s}-{:s}.png'.format(columnDisplayNames[iCol], provinceName)
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
    columnDisplayNames = [label_confirmedCount, label_confirmedCountIncrement, \
        label_curedCount, label_curedCountIncrement, \
        label_deadCount, label_deadCountIncrement]

    nColumnName = len(columnNames)
    for iCol in range(nColumnName):
        fig, ax = plt.subplots()
        for i in range(nDat):
            df_tmp = dat_in[i]
            ax.plot(df_tmp['updateDate'], df_tmp[columnNames[iCol]], '.-', \
                label = cityNames[i]+'({:s} {:d})'.format(\
                label_latestValue, df_tmp[columnNames[iCol]].iloc[-1]))

        ax.xaxis.set_major_formatter(hfmt)
        plt.legend()
        #plt.xlabel('日期')
        plt.ylabel(columnDisplayNames[iCol])
        ylims = ax.get_ylim()
        ax.set_ylim([0, ylims[1]])

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()
        
        if savefig:
            plt.savefig(columnDisplayNames[iCol]+'.png', dpi = 300)
        if show:
            plt.show()
        plt.close()
    
    if savefig:
        if _language == 'ZH':
            print('已保存趋势图至本目录：')
        elif _language == 'EN':
            print('Figures saved to current directory:')

        for iCol in range(nColumnName):
            print('{:d}. {:s}.png'.format(iCol+1, columnDisplayNames[iCol]))

    return

def plot_most_serious_cities(df_in, by, fn_pre, ylabel, date_in, num_max = 10):
    df_tmp = df_in.sort_values(by = by, ascending = False)
    cityNames = df_tmp[key_cityName][0:num_max]
    values = df_tmp[by][0:num_max]
    #print(cityNames)
    #print(values)

    fig, ax = plt.subplots()
    rects1 = ax.bar(cityNames, values)
    autolabel(rects1, ax)
    plt.ylabel(ylabel)
    title_tmp = '{:s}({:04d}-{:02d}-{:02d})'.format(fn_pre, \
        date_in.year, date_in.month, date_in.day)
    fn_tmp = '{:s}_{:04d}_{:02d}_{:02d}.png'.format(\
        fn_pre, date_in.year, date_in.month, date_in.day)
    plt.title(title_tmp)
    plt.savefig(fn_tmp, dpi = 300)
    plt.close()
    return

def visualize_area_data_by_city(fn_csv, cityNames):
    df_orig = pd.read_csv(fn_csv)

    nCity = len(cityNames)

    datasets = []
    for i in range(nCity):
        df_tmp = extract_by_city(df_orig, cityNames[i])
        datasets.append(df_tmp)

    plot_datasets_by_matplot(datasets, cityNames)

    df_cities = pd.concat(datasets)
    # write to csv
    df_cities.to_csv('subset_cities.csv')
    return df_cities

def visualize_area_data_by_province(fn_csv, provinceNames = None, debug = False):
    df_orig = pd.read_csv(fn_csv)
    #print(df_orig.columns)

    if provinceNames is None:
        provinceNames = df_orig[key_provinceName].unique()
    nProvince = len(provinceNames)

    dfLatestDay = []
    latestDays = []

    #datasets = []
    for i in range(nProvince):
        if debug:
            print(provinceNames[i])
        df_tmp = extract_by_province(df_orig, provinceNames[i])
        #datasets.append(df_tmp)

        cityNames = df_tmp[key_cityName].unique()
        nCity = len(cityNames)

        for iCity in range(nCity):
            print('Plotting {:s} {:s}'.format(provinceNames[i], cityNames[iCity]))
            plot_city_dataset_by_matplot(df_tmp, provinceNames[i], cityNames[iCity])

        dates = df_tmp['updateDate'].unique()
        nDate = len(dates)

        # Extract the city data on the latest day
        latestDay = dates.max()
        latestDays.append(latestDay)
        dfLatestDayInProvince = df_tmp[df_tmp['updateDate'] == latestDay]
        #print(dfLatestDayInProvince.to_string())
        dfLatestDay.append(dfLatestDayInProvince)

        # Assemble the time history of the provinces from the cities'.

        dfProvince_tmp = pd.DataFrame({key_provinceName: provinceNames[i], \
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

    dfLatestDay = pd.concat(dfLatestDay)
    #print(dfLatestDay.to_string())

    latestDays = pd.Series(latestDays)
    latestDay = latestDays.max()
    plot_most_serious_cities(dfLatestDay, 'city_confirmedCountIncrement', \
        label_confirmedCountIncrement+label_mostSeriousCity, \
        label_confirmedCountIncrement, latestDay)
    return

