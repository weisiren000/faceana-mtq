"use client"

import { useState } from "react"
import { useImageGeneration } from "../../hooks/useImageGeneration"

interface EmotionData {
  emotion: string
  percentage: number
  color: string
}

interface GenerationPanelProps {
  emotionData: EmotionData[]
}

export default function GenerationPanel({ emotionData }: GenerationPanelProps) {
  const [customPrompt, setCustomPrompt] = useState("")
  const [comfyuiUrl, setComfyuiUrl] = useState("http://localhost:8000")
  const [showSettings, setShowSettings] = useState(false)
  
  const {
    isConnected,
    isGenerating,
    generatedImage,
    error,
    progress,
    generateImage,
    checkConnection
  } = useImageGeneration({
    comfyuiUrl
  })
  
  // 获取主导情绪
  const getDominantEmotion = (): EmotionData | null => {
    if (!emotionData || emotionData.length === 0) return null
    
    return emotionData.reduce(
      (prev, current) => (current.percentage > prev.percentage ? current : prev),
      emotionData[0]
    )
  }
  
  // 处理生成按钮点击
  const handleGenerate = async () => {
    const dominantEmotion = getDominantEmotion()
    if (!dominantEmotion) return
    
    await generateImage(dominantEmotion, customPrompt || undefined)
  }
  
  // 处理连接检查
  const handleCheckConnection = async () => {
    const connected = await checkConnection()
    if (connected) {
      alert("成功连接到ComfyUI服务器!")
    }
  }
  
  return (
    <div className="mt-6 border border-gray-700 rounded-lg p-4 bg-black/30">
      <h3 className="text-xl font-bold mb-2">情绪图像生成</h3>
      
      {/* 连接状态 */}
      <div className="flex items-center mb-3">
        <div className={`w-3 h-3 rounded-full mr-2 ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
        <span className="text-sm">{isConnected ? 'ComfyUI已连接' : 'ComfyUI未连接'}</span>
        <button 
          onClick={handleCheckConnection}
          className="ml-2 text-xs bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded"
        >
          检查连接
        </button>
      </div>
      
      {/* ComfyUI地址 */}
      <div className="mb-3">
        <label className="block text-sm mb-1">ComfyUI地址</label>
        <input
          type="text"
          value={comfyuiUrl}
          onChange={(e) => setComfyuiUrl(e.target.value)}
          className="w-full bg-black/50 border border-gray-600 rounded px-3 py-2"
          placeholder="http://localhost:8000"
        />
      </div>
      
      {/* 提示词编辑器 */}
      <div className="mb-3">
        <label className="block text-sm mb-1">自定义提示词 (可选)</label>
        <textarea
          value={customPrompt}
          onChange={(e) => setCustomPrompt(e.target.value)}
          className="w-full bg-black/50 border border-gray-600 rounded px-3 py-2 h-20"
          placeholder="输入自定义提示词，将与情绪提示词结合"
        />
      </div>
      
      {/* 生成按钮 */}
      <button
        onClick={handleGenerate}
        disabled={isGenerating || !emotionData.length || !isConnected}
        className={`w-full py-2 rounded-md ${
          isGenerating || !emotionData.length || !isConnected
            ? "bg-gray-600 cursor-not-allowed"
            : "bg-purple-600 hover:bg-purple-700"
        }`}
      >
        {isGenerating ? "生成中..." : "生成情绪图像"}
      </button>
      
      {/* 错误信息 */}
      {error && (
        <div className="mt-2 text-red-400 text-sm">
          错误: {error}
        </div>
      )}
      
      {/* 生成进度 */}
      {isGenerating && (
        <div className="mt-3">
          <p className="text-sm">生成进度: {Math.round(progress)}%</p>
          <div className="w-full bg-gray-700 rounded-full h-2.5 mt-2">
            <div 
              className="bg-purple-600 h-2.5 rounded-full transition-all duration-300" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      )}
      
      {/* 图像预览 */}
      {generatedImage && (
        <div className="mt-4">
          <p className="text-sm mb-2">生成结果:</p>
          <img 
            src={generatedImage} 
            alt="情绪图像" 
            className="w-full h-auto rounded-lg border border-gray-600"
          />
          <div className="flex justify-end mt-2">
            <button 
              onClick={() => window.open(generatedImage, '_blank')}
              className="text-xs bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded"
            >
              查看原图
            </button>
          </div>
        </div>
      )}
      
      {/* 主导情绪信息 */}
      {getDominantEmotion() && (
        <div className="mt-3 text-sm text-gray-400">
          主导情绪: {getDominantEmotion()?.emotion} ({getDominantEmotion()?.percentage.toFixed(1)}%)
        </div>
      )}
    </div>
  )
} 