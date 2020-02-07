from functions import visualize_area_data_by_city, visualize_area_data_by_province

# 指定 'DXYArea.csv'文件的路径
fn_DXYArea = '../DXY-2019-nCoV-Data/csv/DXYArea.csv'

# 将希望绘制趋势图的城市名添加到下一行中
cityNames = ['武汉', '黄冈', '孝感']
visualize_area_data_by_city(fn_DXYArea, cityNames)

provinceNames = ['湖北省']
#visualize_area_data_by_province(fn_DXYArea, provinceNames = None)
#visualize_area_data_by_province(fn_DXYArea, provinceNames)
