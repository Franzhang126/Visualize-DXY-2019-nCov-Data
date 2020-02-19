from functions import visualize_area_data_by_city, visualize_area_data_by_province

# 指定 'DXYArea.csv'文件的路径
fn_DXYArea = '../DXY-2019-nCoV-Data/csv/DXYArea.csv'

# 将希望绘制趋势图的城市名添加到下一行中
cityNames = ['孝感', '黄冈', '咸宁', '哈尔滨']
visualize_area_data_by_city(fn_DXYArea, cityNames)

# 将希望绘制趋势图的省份名添加到下一行中
provinceNames = ['湖北省', '黑龙江省']
visualize_area_data_by_province(fn_DXYArea, provinceNames)

# 绘制所有省份的趋势图
visualize_area_data_by_province(fn_DXYArea)
