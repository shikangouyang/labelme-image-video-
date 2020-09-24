本项目是在原labelme(https://github.com/wkentaro/labelme)上所做的修改可以完成对视频、图片进行标注。

```
# Setup conda
conda create --name labelme python==3.6.0
conda activate labelme
pip install opencv-python

# Build the standalone executable
pip install .
pip install pyinstaller
pyinstaller labelme.spec
dist/labelme --version
```

标注视频的时候默认保存的是json文件，路径中不要出现中文。

<font color=red>**videos目录下会生成ImgJson文件，文件中会保存标记的图片及对应的json文件**</font>

