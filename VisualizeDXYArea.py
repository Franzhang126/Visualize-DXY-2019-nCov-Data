import functions

# Set the language for text in figures
language = 'ZH' # 'EN' for English, 'ZH' for 中文(Chinese Simplified)。
functions.set_language(language) 

# 指定 'DXYArea.csv'文件的路径
# Set the path pointing to 'DXYArea.csv'
fn_DXYArea = '../DXY-2019-nCoV-Data/csv/DXYArea.csv'

# 将希望绘制趋势图的城市名添加到下一行中
# Set the names of cities whose trend you would like to visualize.
cityNames = ['孝感', '黄冈', '咸宁', '哈尔滨'] # Chinese version
#cityNames = ['Xiaogan', 'Huanggang', 'Xianning', 'Harbin'] # English version
functions.visualize_area_data_by_city(fn_DXYArea, cityNames)

# 将希望绘制趋势图的省份名添加到下一行中
provinceNames = ['湖北省', '黑龙江省'] # Chinese version
#provinceNames = ['Hubei', 'Heilongjiang'] # English version
functions.visualize_area_data_by_province(fn_DXYArea, provinceNames)

# 若不提供具体省名，则绘制所有省份的趋势图
# If you don't fill in a definite name of province, then the trends of all provinces will be plotted.
functions.visualize_area_data_by_province(fn_DXYArea)
