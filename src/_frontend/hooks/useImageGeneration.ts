"use client"

import { useState, useEffect } from "react"
import { generateFromEmotion, checkComfyUIConnection } from "../lib/comfyui-api"

interface EmotionData {
  emotion: string
  percentage: number
  color: string
}

interface UseImageGenerationOptions {
  backendUrl?: string
  comfyuiUrl?: string
  autoCheck?: boolean
}

interface UseImageGenerationResult {
  isConnected: boolean
  isGenerating: boolean
  generatedImage: string | null
  error: string | null
  progress: number
  generateImage: (dominantEmotion: EmotionData, customPrompt?: string) => Promise<void>
  checkConnection: () => Promise<boolean>
}

/**
 * 图像生成钩子
 * @param options 配置选项
 * @returns 图像生成状态和方法
 */
export function useImageGeneration(options: UseImageGenerationOptions = {}): UseImageGenerationResult {
  const [isConnected, setIsConnected] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedImage, setGeneratedImage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  
  const backendUrl = options.backendUrl || "http://localhost:8000"
  const comfyuiUrl = options.comfyuiUrl || "http://localhost:8000"
  const autoCheck = options.autoCheck !== false
  
  // 自动检查连接
  useEffect(() => {
    if (autoCheck) {
      checkConnection()
    }
  }, [comfyuiUrl, autoCheck])
  
  // 检查连接
  const checkConnection = async (): Promise<boolean> => {
    try {
      const connected = await checkComfyUIConnection(comfyuiUrl)
      setIsConnected(connected)
      if (!connected) {
        setError("无法连接到ComfyUI服务器")
      } else {
        setError(null)
      }
      return connected
    } catch (err) {
      setIsConnected(false)
      setError(`连接错误: ${err instanceof Error ? err.message : String(err)}`)
      return false
    }
  }
  
  // 生成图像
  const generateImage = async (dominantEmotion: EmotionData, customPrompt?: string): Promise<void> => {
    if (!dominantEmotion) {
      setError("请先进行情绪分析")
      return
    }
    
    setIsGenerating(true)
    setProgress(0)
    setError(null)
    setGeneratedImage(null)
    
    try {
      // 模拟进度更新
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval)
            return 95
          }
          return prev + Math.random() * 5
        })
      }, 500)
      
      // 发送生成请求
      const result = await generateFromEmotion(
        {
          emotion: dominantEmotion.emotion.toLowerCase(),
          intensity: dominantEmotion.percentage / 100,
          custom_prompt: customPrompt,
          comfyui_url: comfyuiUrl
        },
        backendUrl
      )
      
      clearInterval(progressInterval)
      
      if (result.success) {
        // 生成成功，模拟一个图像URL
        // 在实际应用中，应该从ComfyUI获取真实的图像URL
        setProgress(100)
        
        // 模拟延迟，然后显示图像
        setTimeout(() => {
          // 这里应该是从ComfyUI获取的真实图像URL
          // 目前使用占位图像
          setGeneratedImage(`${comfyuiUrl}/view?filename=emoscan_${dominantEmotion.emotion.toLowerCase()}.png`)
          setIsGenerating(false)
        }, 1000)
      } else {
        setError(result.error || "生成失败")
        setIsGenerating(false)
        setProgress(0)
      }
    } catch (err) {
      setError(`生成错误: ${err instanceof Error ? err.message : String(err)}`)
      setIsGenerating(false)
      setProgress(0)
    }
  }
  
  return {
    isConnected,
    isGenerating,
    generatedImage,
    error,
    progress,
    generateImage,
    checkConnection
  }
} 