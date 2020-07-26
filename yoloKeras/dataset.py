import os
import random

trainval_percent = 0.66  # 訓練加驗證集佔全部資料集比例
train_percent = 0.5  # 訓練集佔訓練加驗證集比例
xml_file_path = 'D:/桌面/Python/aidel/data/imageSet/annotations/pole'  # 標註檔路徑
txt_save_path = 'D:/桌面/Python/aidel/data/imageSet/main/pole'  # 訓練、驗證、測試清單路徑
total_xml = os.listdir(xml_file_path)

num = len(total_xml)
_list = range(num)
tv = int(num * trainval_percent)
tr = int(tv * train_percent)
trainval = random.sample(_list, tv)
train = random.sample(trainval, tr)

ftrainval = open(f'{txt_save_path}/trainval.txt', 'w')  # 指定訓練加驗證集清單檔
ftest = open(f'{txt_save_path}/test.txt', 'w')  # 指定測試資料集清單
ftrain = open(f'{txt_save_path}/train.txt', 'w')  # 指定訓練資料集清單
fval = open(f'{txt_save_path}/val.txt', 'w')  # 指定驗證資料集清單

for i in _list:
    name = total_xml[i][:-4]+'\n'
    if i in trainval:
        ftrainval.write(name)
        if i in train:
            ftrain.write(name)
        else:
            fval.write(name)
    else:
        ftest.write(name)

ftrainval.close()
ftrain.close()
fval.close()
ftest .close()