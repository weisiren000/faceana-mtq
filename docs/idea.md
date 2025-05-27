# 想法

# 模块
1. 需要添加图像压缩算法，达到快速上传图像的目的，同时也避免因为图像过大报错

1. 调用facepp API识别人像情绪识别(FACEPP_API_DOC_URL=https://console.faceplusplus.com.cn/documents/6329752)
    - 注意RGBA和RGB的区别，只支持RGB

2. 调用Gemini API、openrouter进行人像情绪识别，使用模型：
    - GEMINI_MODEL=gemma-3-27b-it
    - OPENROUTER_MODEL=google/gemma-3-27b-it:free
