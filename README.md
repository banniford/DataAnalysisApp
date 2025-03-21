# DataAnalysisApp

## 概要

本项目主要根据数据源主指标变量分析识别突变时间点t，结合不同的数据分析算法（平均值，最小，最大）实现对数据源的主/次变量计算，分析完成后需要绘制对应图表确认后生成数据报告。

## 环境构建说明

&emsp;&emsp;要导出你的 Python 应用程序 app.py 使用的库名称，你可以使用 pip 和 pipreqs 工具。以下是步骤：

&emsp;&emsp;安装 pipreqs 工具，如果尚未安装：

```shell
pip install pipreqs -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

&emsp;&emsp;切换到包含 app.py 文件的目录。

&emsp;&emsp;运行以下命令，生成 requirements.txt 文件：

```shell
pipreqs . --force
```

&emsp;&emsp;这将分析当前目录中的代码文件，查找导入的库，并将这些库的名称添加到 requirements.txt 文件中。

## 打包说明

&emsp;&emsp;使用 pyinstaller 工具打包成 win 可执行文件，以下是打包命令：

```shell
pip install pyinstaller==6.10.0 -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
pyinstaller -F -w -i ./assets/image/faviceon.ico ./src/app.py
```