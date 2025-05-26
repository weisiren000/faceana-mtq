# an idea file

1. capture.py ：打开识别的电脑摄像头，如果识别到人脸则开始瞬时截图4秒5张图存放到data\capture
2. tagger.py ：对data\capture中的图片进行人脸关键点检测，将检测结果存放到data\tagger
3. splicer.py ：将data\tagger中的图片进行拼接，将拼接结果存放到data\splicer
    - 拼接方式：
    - 1. 将data\capture中的图片按照时间顺序进行横向拼接
    - 2. 将data\tagger中的图片按照时间顺序进行横向拼接
    - 3. 将1、2步骤拼接的图像进行纵向拼接存放到data\splicer
4. caller.py ：调用AI模型对data\capture中的图片进行分析
    - 1. 调用facepp对data\capture中的人脸图像进行情绪识别，将facepp返回的data数据发送给DSA_Agent,DSA_Agent进行数据提取（下判定）
    - 2. 将data\capture中的图片发送给VSA_Agent,VSA_Agent进行图像分析（下情绪判定）
    - 3. 将上述两个智能体下的判定都发给JSA_Agent，JSA_Agent进行综合判定，最后将判定结果返回给前端


. cleaner.py ：程序运行结束之后清理data\capture和data\tagger中的图片
