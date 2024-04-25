# 注意事项  
本评测机需要安装networkx，cyaron库，可以通过以下命令安装：  
```bash
pip install networkx
pip install cyaron
```
若要使用计时功能，需要安装func_timeout库，可通过以下命令安装：  
```bash
pip install func_timeout
```

## 绘图功能使用说明  
### 前置条件  
需要plotly库，可以通过以下命令安装：  
```bash
pip install plotly
```
当图很大时，可能需要下载额外的包，可以通过以下命令安装：  
```bash
pip install scipy
```
确保input.txt和output.txt在同一目录下，运行draw.py即可。

## 检验正确性功能使用说明
在check.py中，修改264行的参数为你的input,output文件路径，运行check.py即可。