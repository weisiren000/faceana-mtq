# 项目逻辑
1. "VISUAL INPUT" 区域需要增加后端支持
   1. 截图之后每张图像都发给facepp API进行情绪识别
   2. facepp API返回情绪识别结果
       - 识别的情绪类别：
         - 愤怒(Angry)
         - 厌恶(Disgusted)
         - 恐惧(Fearful)
         - 高兴(Happy)
         - 平静(Neutral)
         - 悲伤(Sad)
         - 惊讶(Surprised)
   3. 将情绪识别结果发送给Gemini API进行分析
   4. Gemini API返回分析结果
   5. 将分析结果发送给前端
   6. 前端将分析结果展示在"AI ANALYSIS"区域
