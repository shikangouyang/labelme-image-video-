# -*- coding: utf-8 -*-
# @Time    : 2020/7/26 20:05
# @Author  : OYSK
# @File    : LoadSecondUi.py.py

from PyQt5.Qt import *
from labelme.second import Ui_widget
import cv2
import time
import os
import shutil


class Window(QWidget, Ui_widget):

    VIDEO_TYPE_OFFLINE = 0
    VIDEO_TYPE_REAL_TIME = 1

    STATUS_PLAYING = 1
    STATUS_PAUSE = 2

    def __init__(self, tempPath, fps=0, total_frames=0):
        super().__init__()
        self.tempPath = tempPath
        self.setupUi(self)
        self.total_frames = total_frames
        self.fps = fps
        self.img_url = ''
        self.n = 0
        self.status = self.STATUS_PLAYING
        self.PreDir = ""
        self.masterDir = ""
        self.videoName = ""
        self.ImgJsonPath = ""
        self.Flag = 0
        self.lumpIndex = None

        self.pushButton_2.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_3.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_4.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_6.setCursor(QCursor(Qt.PointingHandCursor))

        self.pushButton_4.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        self.pushButton_4.clicked.connect(self.switch_video)

        self.pushButton_3.clicked.connect(self.BtnRight)
        self.pushButton_2.clicked.connect(self.BtnLeft)
        self.pushButton_6.clicked.connect(self.BtnUpdata)
        self.lineEdit.returnPressed.connect(self.InputFrame)
        self.lineEdit_4.returnPressed.connect(self.setFps)

        self.comboBox.activated.connect(self.ComIndex)

        # timer 设置
        self.timer = VideoTimer(self.fps)
        self.timer.timeSignal.signal[str].connect(self.auto_play)

        self.open_image()

    def setFps(self):
        if self.lineEdit_4.text().strip() == '':
            self.timer.set_fps(self.fps)
        else:
            self.timer.set_fps(int(self.lineEdit_4.text()))

    def open_image(self):
        """
        select image file and open it
        :return:
        """
        self.lineEdit_3.setText(str(self.total_frames))
        self.lineEdit_4.setText(str(self.fps))
        self.lineEdit.setText(str(0))
        self.img_url = self.tempPath + "/" + self.lineEdit.text() + ".jpg"
        self.show_video_images()
        self.Flag = 1
        self.BtnUpdata()

    def BtnUpdata(self):
        self.comboBox.clear()
        ListJson = Window.getFiles(self.tempPath, ".json")
        ret = []
        for ele in ListJson:
            temp = os.path.split(ele)[1]
            TempVideoName = temp.partition('.')[0]
            ret.append(int(TempVideoName))
        for i in sorted(ret):
            self.comboBox.addItem(str(i))

    def ComIndex(self):
        index = self.comboBox.currentText()
        self.lineEdit.setText(str(index))
        self.lumpIndex = self.tempPath + "/" + self.lineEdit.text() + ".jpg"
        self.img_url = self.lumpIndex
        self.show_video_images()


    def BtnRight(self):
        if self.Flag == 0:
            self.messageDialog("请加载视频")
            return
        if self.lineEdit.text().strip() == '':
            self.messageDialog("当前帧不能为空")
            return
        if int(self.lineEdit.text()) >= (self.total_frames - 1):
            self.messageDialog("已经是最后一帧了".format(self.total_frames - 1))
            return
        if int(self.lineEdit.text()) < 0:
            self.messageDialog("您输入有误，应该输入0-{}的整数，请重新输入".format(self.total_frames - 1))
            return

        frameNum = int(self.lineEdit.text()) + 1
        self.img_url = self.tempPath + "/" + str(frameNum) + ".jpg"
        self.show_video_images()
        self.lineEdit.setText(str(frameNum))

    def BtnLeft(self):
        if self.Flag == 0:
            self.messageDialog("请加载视频")
            return
        if self.lineEdit.text().strip() == '':
            self.messageDialog("当前帧不能为空")
            return
        if int(self.lineEdit.text()) > (self.total_frames - 1):
            self.messageDialog("您输入有误，应该输入0-{}的整数，请重新输入".format(self.total_frames - 1))
            return
        if int(self.lineEdit.text()) <= 0:
            self.messageDialog("这已经是第0帧了")
            return

        frameNum = int(self.lineEdit.text()) - 1
        self.img_url = self.tempPath + "/" + str(frameNum) + ".jpg"
        self.show_video_images()
        self.lineEdit.setText(str(frameNum))

    # 直接定位到某一帧
    def InputFrame(self):
        if self.Flag == 0:
            self.messageDialog("请加载视频")
            return
        if self.lineEdit.text().strip() == '':
            self.messageDialog("当前帧不能为空")
            return
        if not str.isdigit(self.lineEdit.text()):
            self.messageDialog("您输入有误，应该输入0-{}的整数，请重新输入".format(self.total_frames - 1))
            return
        if int(self.lineEdit.text()) > (self.total_frames - 1):
            self.messageDialog("您输入有误，应该输入0-{}的整数，请重新输入".format(self.total_frames - 1))
            return
        if int(self.lineEdit.text()) < 0:
            self.messageDialog("您输入有误，应该输入0-{}的整数，请重新输入".format(self.total_frames - 1))
            return
        self.img_url = self.tempPath + "/" + self.lineEdit.text() + ".jpg"
        self.show_video_images()

    def switch_video(self):
        if self.Flag == 0:
            self.messageDialog("请加载视频")
            return
        if self.lineEdit.text().strip() == '':
            self.messageDialog("当前帧不能为空")
            return
        if int(self.lineEdit.text()) >= (self.total_frames - 1):
            self.pushButton_4.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.messageDialog("已经是最后一帧了".format(self.total_frames - 1))
            return
        if int(self.lineEdit.text()) < 0:
            self.pushButton_4.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.messageDialog("您输入有误，应该输入0-{}的整数，请重新输入".format(self.total_frames - 1))
            return
        elif self.status is Window.STATUS_PLAYING:
            self.timer.start()
            self.pushButton_4.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        elif self.status is Window.STATUS_PAUSE:
            self.timer.stop()
            self.pushButton_4.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        self.status = (Window.STATUS_PLAYING,
                       Window.STATUS_PAUSE,
                       Window.STATUS_PLAYING)[self.status]

    def auto_play(self):
        if self.Flag == 0:
            self.messageDialog("请加载视频")
            return
        self.n = int(self.lineEdit.text())
        if int(self.lineEdit.text()) >= (self.total_frames - 1):
            self.timer.stop()
            self.pushButton_4.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            return
        if int(self.lineEdit.text()) < 0:
            self.timer.stop()
            self.pushButton_4.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            return
        self.n = self.n + 1
        self.img_url = self.tempPath + "/" + str(self.n) + ".jpg"
        self.show_video_images()
        self.lineEdit.setText(str(self.n))

    def show_video_images(self):
        scale = 1.3
        frame = cv2.imread(self.img_url)
        height, width = frame.shape[:2]
        #frame = cv2.resize(frame, (int(height * 1.5), int(width * 1.5)))
        if frame.ndim == 3:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        elif frame.ndim == 2:
            rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        temp_image = QImage(rgb.flatten(), width, height, QImage.Format_RGB888)

        mgnWidth = int(width * scale)
        mgnHeight = int(height * scale)  # 缩放宽高尺寸
        size = QSize(mgnWidth, mgnHeight)
        # 修改图片实例大小并从QImage实例中生成QPixmap实例以备放入QLabel控件中
        temp_pixmap = QPixmap.fromImage(temp_image.scaled(size, Qt.IgnoreAspectRatio))
        self.label.resize(mgnWidth, mgnHeight)
        self.label.setPixmap(temp_pixmap)

        # temp_pixmap = QPixmap.fromImage(temp_image)
        # self.label.setPixmap(temp_pixmap)
        # self.pictureLabel.setScaledContents(True)

    @staticmethod
    def del_file(filepath):
        """
        删除某一目录下的所有文件或文件夹
        """
        del_list = os.listdir(filepath)
        for f in del_list:
            file_path = os.path.join(filepath, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    @staticmethod
    def VideoToImg(videos_path, tmp_path):

        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        else:
            Window.del_file(tmp_path)

        videoCap = cv2.VideoCapture(videos_path)
        # 帧频
        fps = videoCap.get(cv2.CAP_PROP_FPS)
        # 视频总帧数
        total_frames = int(videoCap.get(cv2.CAP_PROP_FRAME_COUNT))

        for i in range(total_frames):
            ret, frame = videoCap.read()
            if not ret:
                continue
            img_path = os.path.join(tmp_path, str(i) + '.jpg')
            cv2.imwrite(img_path, frame)
        videoCap.release()
        return fps, total_frames

    @staticmethod
    def FilesOperation(InPath, OutPath):
        ListJson = Window.getFiles(InPath, '.json')
        if len(ListJson) == 0:
            return
        else:
            for ele in ListJson:
                shutil.copy(ele, OutPath)

    @staticmethod
    def getFiles(dir, suffix):  # 查找根目录，文件后缀
        res = []
        for root, directory, files in os.walk(dir):  # =>当前根,根下目录,目录下的文件
            for filename in files:
                name, suf = os.path.splitext(filename)  # =>文件名,文件后缀
                if suf == suffix:
                    res.append(os.path.join(root, filename))  # =>吧一串字符串组合成路径
        return res

    def setup_ui(self):
        pass

    def messageDialog(self, warning):
        QMessageBox.information(self, "温馨提示", warning)

class Communicate(QObject):

    signal = pyqtSignal(str)


class VideoTimer(QThread):

    def __init__(self, frequent=20):
        QThread.__init__(self)
        self.stopped = False
        self.frequent = frequent
        self.timeSignal = Communicate()
        self.mutex = QMutex()

    def run(self):
        with QMutexLocker(self.mutex):
            self.stopped = False
        while True:
            if self.stopped:
                return
            self.timeSignal.signal.emit("1")
            time.sleep(1 / self.frequent)

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopped = True

    def is_stopped(self):
        with QMutexLocker(self.mutex):
            return self.stopped

    def set_fps(self, fps):
        self.frequent = fps


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())