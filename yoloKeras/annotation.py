import xml.etree.ElementTree as ET
from os import getcwd

sets = ['train', 'val', 'test']  # 定義資料集名稱
classes = ['pole']  # 定義自訂義類別名稱

xml_file_path = 'D:/桌面/Python/aidel/data/imageSet/annotations/pole'  # 標註檔路徑
txt_save_path = 'D:/桌面/Python/aidel/data/imageSet/main/pole'  # 訓練、驗證、測試清單路徑
img_file_path = 'D:/桌面/Python/aidel/data/imageSet/images/pole' # 原始照片路徑

def convert_annotation(img_id, list_file):
    in_file = open(
        f'{xml_file_path}/{img_id}.xml', encoding='utf-8')  # 指定標註檔路徑
    tree = ET.parse(in_file)
    root = tree.getroot()

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        _cls = obj.find('name').text
        if _cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(_cls)
        xmlbox = obj.find('bndbox')
        b = (int(xmlbox.find('xmin').text), int(xmlbox.find('ymin').text),
             int(xmlbox.find('xmax').text), int(xmlbox.find('ymax').text))
        list_file.write(" " + ",".join([str(a)
                                        for a in b]) + ',' + str(cls_id))


for image_set in sets:
    img_names = open(f'{txt_save_path}/{image_set}.txt').read().strip().split()  # 指定待轉換清單檔案名稱
    list_file = open(f'{txt_save_path}/transform_{image_set}.txt', 'w')  # 指定轉換完成清單名稱
    for img_name in img_names:
        list_file.write(f'{img_file_path}/{img_name}.jpg')
        img_id = img_name.split('.')
        convert_annotation(img_id[0], list_file)
        list_file.write('\n')
    list_file.close()