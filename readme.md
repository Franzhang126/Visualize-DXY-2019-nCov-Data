# VisualizeDXYArea
## 用途
将 *BlankerL* 提供的[2019新型冠状病毒疫情时间序列数据仓库](https://github.com/BlankerL/DXY-2019-nCoV-Data)进行可视化。目前为自用，可提供市级的确诊数、治愈数、死亡数时程线，（各大网站只提供全国确诊数的时程线）。

<img src="单日新增确诊数.png" width=400 />
<img src="单日新增确诊数-湖北省.png" width=400 />
<img src="单日新增死亡数-湖北省.png" width=400 />
<img src="multi-province.png" width=600 />

## 用法
打开`VisualizeDXYArea.py`，填入感兴趣的省名、市名、数据文件的路径，保存后，运行
```
python VisualizeDXYArea.py
```
将生成`png`格式的时程线图片。

## 依赖库
除标准python库外，需额外安装的库有：
`matplotlib pandas`