## 评测使用说明

需要在main.py同级目录里放置课程组的投喂包，命名为"input.exe"

checker：analyze_input从输入获取乘客信息，analyze_output分析输入（默认接受重置的信号正确输出），check进行正确性检验。

data_generator：生成随机数据，用于测试。

data_loader：读取数据，用于测试。

如果需要使用自定义的数据生成器，可以在main.py修改process_function中的pass为自定义的函数。这个函数需要将数据写入f'workspace/{case_id}/stdin.txt'

计时功能需要下载func_timeout包，可以使用pip安装。

```shell
pip install func_timeout
```

具体运行设置参考config,json
**注意：jar_path需要填写绝对地址**

## 检测指定的输入输出

确保 `congfig.json, checker.py, stdin.txt, ouput.txt, test.py` 在同一目录下

将输入、输出分别填写到 `stdin.txt` 和 `output.txt` 中，运行 `test.py` 即可

## 相关信息

采用多线程评测

由gpf和zx共同完成