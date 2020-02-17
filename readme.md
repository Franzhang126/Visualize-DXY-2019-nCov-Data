# VisualizeDXYArea
## 用途 | Purpose
将 *BlankerL* 提供的[2019新型冠状病毒疫情时间序列数据仓库](https://github.com/BlankerL/DXY-COVID-19-Data)进行可视化。目前为自用，可提供市级的确诊数、治愈数、死亡数时程线，（各大网站只提供全国确诊数的时程线）。

Visualize the time-history of important daily counts in COVID-19.
However, the features are quite limited by now as it is for my personal use. (I live in the epicenter of the pandemic, Wuhan City, Hubei Province. I care about the trend.)

The daily increment will be calculated and plotted so that we are aware of the trend.

The data is provided by *BlankerL* at his repository [DXY-COVID-19-Data](https://github.com/BlankerL/DXY-COVID-19-Data).

<img src="单日新增确诊数.png" width=400 />
<img src="单日新增确诊数-湖北省.png" width=400 />
<img src="单日新增死亡数-湖北省.png" width=400 />
<img src="multi-province.png" width=600 />

## 用法 | Usage
打开`VisualizeDXYArea.py`，填入感兴趣的省名、市名、数据文件的路径，保存后，运行

Open `VisualizeDXYArea.py`, fill the names of interested cities or provinces, save and run:

```
python VisualizeDXYArea.py
```
将生成`png`格式的时程线图片。

Time-histories will be saved as figures in format of `png`.

## 依赖库 | Dependencies
除标准`python`库外，需额外安装的库有：

Besides the standard `python 3` library, you need these libs installed: 

`matplotlib pandas`