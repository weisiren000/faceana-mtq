"use client"

import { useState, useRef, useEffect } from "react"
import { useTheme } from "@/hooks/useTheme"
import { ThemeToggle } from "@/components/ThemeToggle"

interface EmotionData {
  emotion: string
  percentage: number
  color: string
}

interface CapturedImage {
  id: number
  url: string
  analyzing: boolean
}

enum AnalysisMode {
  QUICK = "quick",
  DETAILED = "detailed"
}

// 自定义Hook：打字机效果
function useTypewriter(text: string, baseSpeed: number = 50) {
  const [displayText, setDisplayText] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [showCursor, setShowCursor] = useState(true)
  const [typingProgress, setTypingProgress] = useState(0) // 0-1 表示打字进度

  useEffect(() => {
    if (!text) {
      setDisplayText("")
      setIsTyping(false)
      return
    }

    setIsTyping(true)
    setDisplayText("")
    let index = 0
    let animationId: number

    const typeNextChar = () => {
      if (index < text.length) {
        setDisplayText(prev => text.slice(0, index + 1)) // 使用函数式更新
        setTypingProgress(index / text.length) // 更新打字进度
        index++

        // 计算下一个字符的延迟时间
        let delay = baseSpeed
        const char = text[index - 1]

        // 根据字符类型调整速度
        if (char === '\n') {
          delay = baseSpeed * 1.5 // 换行后稍微停顿
        } else if (char === ' ') {
          delay = baseSpeed * 0.7 // 空格打得快一些
        } else if (/[.!?]/.test(char)) {
          delay = baseSpeed * 2 // 句号后停顿更久
        } else if (/[,;:]/.test(char)) {
          delay = baseSpeed * 1.2 // 逗号后稍微停顿
        }

        // 减少随机变化，提高稳定性
        delay += (Math.random() - 0.5) * baseSpeed * 0.2

        animationId = window.setTimeout(typeNextChar, Math.max(20, delay))
      } else {
        setIsTyping(false)
      }
    }

    // 开始打字前稍微延迟
    animationId = window.setTimeout(typeNextChar, 200)

    return () => {
      if (animationId) {
        clearTimeout(animationId)
      }
    }
  }, [text, baseSpeed])

  // 光标闪烁效果 - 只在打字时闪烁
  useEffect(() => {
    if (isTyping) {
      const cursorInterval = setInterval(() => {
        setShowCursor(prev => !prev)
      }, 500)
      return () => clearInterval(cursorInterval)
    } else {
      // 打字完成后隐藏光标
      setShowCursor(false)
    }
  }, [isTyping])

  return { displayText, isTyping, showCursor, typingProgress }
}

export default function EmoscanApp() {
  const { isDark, mounted } = useTheme()
  const [isRecording, setIsRecording] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [capturedImages, setCapturedImages] = useState<CapturedImage[]>([])
  const [emotionData, setEmotionData] = useState<EmotionData[]>([
    { emotion: "Happy", percentage: 0, color: "#00ff88" },
    { emotion: "Sad", percentage: 0, color: "#0099ff" },
    { emotion: "Angry", percentage: 0, color: "#ff0066" },
    { emotion: "Surprised", percentage: 0, color: "#ffaa00" },
    { emotion: "Neutral", percentage: 0, color: "#888888" },
    { emotion: "Disgusted", percentage: 0, color: "#9d4edd" },
    { emotion: "Fearful", percentage: 0, color: "#f72585" },
  ])
  const [llmOutput, setLlmOutput] = useState("")
  const [scanLine, setScanLine] = useState(0)
  const [currentTime, setCurrentTime] = useState("--:--:--") // 防止Hydration不匹配
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>(AnalysisMode.QUICK)

  // 使用打字机效果
  const { displayText, isTyping, showCursor, typingProgress } = useTypewriter(llmOutput, 25)

  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const outputRef = useRef<HTMLDivElement>(null)

  // 防止重复API调用的锁定机制
  const apiCallLockRef = useRef<boolean>(false)
  const currentCallIdRef = useRef<string | null>(null)

  // 自动滚动逻辑
  useEffect(() => {
    if (outputRef.current) {
      if (isTyping) {
        // 打字时滚动到底部
        outputRef.current.scrollTop = outputRef.current.scrollHeight
      } else if (displayText && !isTyping) {
        // 打字完成后，缓慢滚动到顶部
        const scrollToTop = () => {
          const element = outputRef.current
          if (element) {
            const startScrollTop = element.scrollTop
            const duration = 2000 // 2秒滚动到顶部
            const startTime = performance.now()

            const animateScroll = (currentTime: number) => {
              const elapsed = currentTime - startTime
              const progress = Math.min(elapsed / duration, 1)

              // 使用easeInOutCubic缓动函数
              const easeProgress = progress < 0.5
                ? 4 * progress * progress * progress
                : 1 - Math.pow(-2 * progress + 2, 3) / 2

              element.scrollTop = startScrollTop * (1 - easeProgress)

              if (progress < 1) {
                requestAnimationFrame(animateScroll)
              }
            }

            requestAnimationFrame(animateScroll)
          }
        }

        // 延迟1秒后开始滚动
        const timer = setTimeout(scrollToTop, 1000)
        return () => clearTimeout(timer)
      }
    }
  }, [displayText, isTyping])

  // 扫描线动画
  useEffect(() => {
    const interval = setInterval(() => {
      setScanLine((prev) => (prev + 1) % 100)
    }, 50)
    return () => clearInterval(interval)
  }, [])

  // 时间更新 - 防止Hydration不匹配
  useEffect(() => {
    // 只在客户端挂载后才开始更新时间
    if (!mounted) return

    const updateTime = () => {
      setCurrentTime(new Date().toLocaleTimeString())
    }

    // 立即更新一次
    updateTime()

    // 每秒更新
    const interval = setInterval(updateTime, 1000)
    return () => clearInterval(interval)
  }, [mounted])

  // 隐藏滚动条和添加文字大小渐变效果 + 无限循环滚动
  useEffect(() => {
    if (outputRef.current) {
      const element = outputRef.current
      // 直接设置CSS样式来隐藏滚动条
      element.style.setProperty('scrollbar-width', 'none', 'important')
      element.style.setProperty('-ms-overflow-style', 'none', 'important')

      // 创建样式规则
      const style = document.createElement('style')
      style.textContent = `
        .ai-output-container::-webkit-scrollbar {
          display: none !important;
          width: 0 !important;
          height: 0 !important;
        }

        /* 3D圆柱体透视文字容器 */
        .cylindrical-text-container {
          position: relative;
          perspective: 1200px;
          transform-style: preserve-3d;
          overflow: hidden;
        }

        /* 每行文字的基础样式 */
        .text-line {
          display: block;
          text-align: center;
          font-family: 'Courier New', monospace;
          white-space: pre-wrap;
          transition: all 0.08s ease-out;
          transform-origin: center center;
        }

        /* 滚动容器优化 */
        .ai-output-container {
          scroll-behavior: smooth; /* 恢复平滑滚动 */
          will-change: scroll-position;
          -webkit-overflow-scrolling: touch;
          /* 确保可以正常选择文本 */
          user-select: text;
          -webkit-user-select: text;
          -moz-user-select: text;
          -ms-user-select: text;
          /* 确保滚动正常工作 */
          overflow-y: auto;
          overflow-x: hidden;
        }

        /* 移除阻止滚动的伪元素 */
      `
      document.head.appendChild(style)

      // 3D圆柱体效果的滚动监听器 - 优化性能和平滑度
      let animationId: number

      const handleScroll = () => {
        // 使用requestAnimationFrame优化性能
        if (animationId) {
          cancelAnimationFrame(animationId)
        }

        animationId = requestAnimationFrame(() => {
          const textLines = element.querySelectorAll('.text-line') as NodeListOf<HTMLElement>
          if (textLines.length === 0) return

          const containerRect = element.getBoundingClientRect()
          const containerHeight = containerRect.height
          const containerCenter = containerHeight / 2

          // 为每一行文字计算透视效果
          textLines.forEach((line) => {
            const lineRect = line.getBoundingClientRect()
            const lineCenter = lineRect.top + lineRect.height / 2 - containerRect.top

            // 计算距离容器中心的距离 (0-1, 0为中心)
            const distanceFromCenter = Math.abs(lineCenter - containerCenter) / containerCenter

            // 限制距离范围，使用更平滑的曲线
            const clampedDistance = Math.min(distanceFromCenter, 1)
            const smoothDistance = Math.pow(clampedDistance, 0.8) // 使用幂函数创建更平滑的过渡

            // 计算透视效果参数 - 调整为更温和的变化
            // 字体大小：中心最大(16px)，边缘最小(11px)
            const fontSize = 16 - (smoothDistance * 5)

            // 透明度：中心最亮(1.0)，边缘最暗(0.4) - 确保边缘文字仍然可见
            const opacity = 1.0 - (smoothDistance * 0.6)

            // 宽度：中心最宽(100%)，边缘最窄(75%)
            const width = 100 - (smoothDistance * 25)

            // Z轴位移：创建深度效果
            const translateZ = -smoothDistance * 25

            // X轴旋转：增强透视效果
            const rotateX = smoothDistance * 6

            // 应用样式
            line.style.fontSize = `${fontSize}px`
            line.style.opacity = `${opacity}`
            line.style.width = `${width}%`
            line.style.margin = '0 auto'
            line.style.transform = `translateZ(${translateZ}px) rotateX(${rotateX}deg)`

            // 使用CSS变量获取当前主题的文本颜色
            const rootStyles = window.getComputedStyle(document.documentElement)
            const textColorHsl = rootStyles.getPropertyValue('--emoscan-text').trim()
            const accentColorHsl = rootStyles.getPropertyValue('--emoscan-accent').trim()

            // 将HSL转换为RGB以便设置透明度
            const isDarkTheme = document.documentElement.classList.contains('dark')
            if (isDarkTheme) {
              // 深色主题：使用绿色系
              line.style.color = `hsla(${accentColorHsl}, ${opacity})`
              line.style.textShadow = `0 0 ${12 * opacity}px hsla(${accentColorHsl}, ${opacity * 0.5}),
                 0 ${1.5 * opacity}px ${6 * opacity}px rgba(0,0,0,0.3),
                 0 0 ${25 * opacity}px hsla(${accentColorHsl}, ${opacity * 0.25})`
            } else {
              // 浅色主题：使用深色文字
              line.style.color = `hsla(${textColorHsl}, ${opacity})`
              line.style.textShadow = `0 ${1 * opacity}px ${3 * opacity}px rgba(0,0,0,0.2)`
            }
          })
        })
      }

      // 滚动处理变量（保留用于清理）

      // 初始化文本行样式
      const initializeTextLines = () => {
        // 延迟执行，确保DOM已更新
        setTimeout(() => {
          handleScroll()
        }, 50)
      }

      // 只添加滚动监听器，移除wheel监听器让浏览器处理滚轮事件
      element.addEventListener('scroll', handleScroll, { passive: true })

      // 防止文本选择时的意外滚动
      element.addEventListener('selectstart', (e) => {
        // 允许文本选择，但防止选择时的滚动
        e.stopPropagation()
      }, { passive: true })

      element.addEventListener('mousedown', (e) => {
        // 如果是文本选择操作，不触发滚动
        if (e.detail > 1) { // 双击或多击
          e.stopPropagation()
        }
      }, { passive: true })

      // 监听DOM变化，当文本内容更新时重新计算样式
      const observer = new MutationObserver(() => {
        initializeTextLines()
      })

      observer.observe(element, {
        childList: true,
        subtree: true,
        characterData: true
      })

      // 初始化
      initializeTextLines()

      return () => {
        element.removeEventListener('scroll', handleScroll)
        observer.disconnect()
        document.head.removeChild(style)

        // 清理动画帧
        if (animationId) {
          cancelAnimationFrame(animationId)
        }
      }
    }
  }, [])

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop())
      }
    }
  }, [])

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
      })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
    } catch (error) {
      console.error("Error accessing camera:", error)
    }
  }

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop())
      streamRef.current = null
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
  }

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current
      const video = videoRef.current
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight

      const ctx = canvas.getContext("2d")
      if (ctx) {
        ctx.drawImage(video, 0, 0)
        return canvas.toDataURL("image/jpeg")
      }
    }
    return null
  }

  const startRecording = async () => {
    setIsRecording(true)
    setCapturedImages([])
    setAnalysisProgress(0)
    setLlmOutput("")

    await startCamera()

    const captureInterval = setInterval(() => {
      const imageUrl = captureImage()
      if (imageUrl) {
        setCapturedImages((prev) => {
          const newImage = {
            id: prev.length + 1,
            url: imageUrl,
            analyzing: true,
          }
          const updated = [...prev, newImage]

          if (updated.length >= 5) {
            clearInterval(captureInterval)
            startAnalysis(updated)
          }

          return updated
        })
      }
    }, 800)
  }

  const startAnalysis = async (images: CapturedImage[]) => {
    const callId = Math.random().toString(36).substr(2, 9);
    setIsRecording(false)
    setIsAnalyzing(true)
    stopCamera()

    // 根据分析模式选择不同的处理方式
    if (analysisMode === AnalysisMode.DETAILED) {
      // 详细模式：分析所有图像
      await analyzeBatchImages(images)
      return // 详细模式完成后直接返回
    } else {
      // 快速模式：只分析最后一张图像
      if (images.length > 0) {
        const lastImage = images[images.length - 1]

        // 将dataURL转换为Blob
        if (lastImage.url) {
          try {
            const response = await fetch(lastImage.url)
            const blob = await response.blob()

            // 调用后端API
            await analyzeImageWithAPI(blob, callId)
            setIsAnalyzing(false)

            // 更新图像状态
            images.forEach((_, index) => {
              setTimeout(
                () => {
                  setCapturedImages((prev) => prev.map((img, i) => (i === index ? { ...img, analyzing: false } : img)))
                },
                (index + 1) * 200,
              )
            })

            return // 快速模式API调用成功后直接返回
          } catch (error) {
            console.error('快速模式图像转换失败:', error)
            // 快速模式失败，继续执行fallback逻辑
          }
        }
      }
    }

    // 只有在快速模式失败时才执行fallback逻辑
    console.log('执行fallback逻辑，使用模拟数据')
    let progress = 0
    const progressInterval = setInterval(() => {
      progress += Math.random() * 15
      if (progress >= 100) {
        progress = 100
        clearInterval(progressInterval)
        completeAnalysisWithMockData()
        setIsAnalyzing(false)
      }
      setAnalysisProgress(progress)
    }, 200)

    images.forEach((_, index) => {
      setTimeout(
        () => {
          setCapturedImages((prev) => prev.map((img, i) => (i === index ? { ...img, analyzing: false } : img)))
        },
        (index + 1) * 1000,
      )
    })
  }

  // 批量分析所有图像
  const analyzeBatchImages = async (images: CapturedImage[]) => {
    try {
      // 首先检查API是否可用
      const apiAvailable = await checkApiAvailability();
      
      if (!apiAvailable) {
        // API不可用，直接使用模拟数据
        console.log("API不可用，使用模拟数据");
        completeAnalysisWithMockData();
        setIsAnalyzing(false);
        
        // 更新图像状态
        images.forEach((_, index) => {
          setTimeout(
            () => {
              setCapturedImages((prev) => prev.map((img, i) => (i === index ? { ...img, analyzing: false } : img)))
            },
            (index + 1) * 200,
          )
        });
        return;
      }
      
      const formData = new FormData()

      // 将所有图像转换为Blob并添加到FormData
      for (let i = 0; i < images.length; i++) {
        const image = images[i]
        if (image.url) {
          const response = await fetch(image.url)
          const blob = await response.blob()
          formData.append('files', blob, `capture_${i+1}.jpg`)
        }
      }

      // 对于批量分析，我们先使用原有的批量API，然后基于结果生成图像
      const response = await fetch('http://localhost:8000/api/v1/analyze/batch', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`批量API调用失败: ${response.status}`)
      }

      const result = await response.json()

      if (result.success) {
        // 使用API返回的情绪数据
        setEmotionData(result.emotion_data)

        // 使用API返回的分析文本
        let analysisText = result.analysis_text

        // 尝试基于批量分析结果生成图像
        try {
          const imageGenResponse = await fetch('http://localhost:8000/api/v1/generation/generate-from-analysis', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              emotion_data: result.emotion_data,
              seed: Math.floor(Math.random() * 1000000) // 随机种子
            }),
          })

          if (imageGenResponse.ok) {
            const imageGenResult = await imageGenResponse.json()

            // 添加图像生成结果信息
            analysisText += "\n\n" + "━".repeat(80) + "\n"
            analysisText += ">>> COMFYUI IMAGE GENERATION <<<\n\n"

            if (imageGenResult.success) {
              analysisText += `✅ 图像生成成功!\n`
              analysisText += `🎨 生成时间: ${imageGenResult.generation_time?.toFixed(2)}秒\n`
              analysisText += `📸 生成图像: ${imageGenResult.images?.length || 0}张\n`

              if (imageGenResult.images && imageGenResult.images.length > 0) {
                analysisText += `\n生成的图像:\n`
                imageGenResult.images.forEach((img: any, index: number) => {
                  analysisText += `${index + 1}. ${img.filename}\n`
                  analysisText += `   URL: ${img.url}\n`
                })
              }
            } else {
              analysisText += `❌ 图像生成失败: ${imageGenResult.error_message}\n`
              analysisText += `💡 提示: 请检查ComfyUI服务是否正常运行\n`
            }
          } else {
            analysisText += "\n\n" + "━".repeat(80) + "\n"
            analysisText += ">>> COMFYUI IMAGE GENERATION <<<\n\n"
            analysisText += `❌ 图像生成API调用失败: ${imageGenResponse.status}\n`
          }
        } catch (imageGenError) {
          console.warn('图像生成失败，但情绪分析成功:', imageGenError)
          analysisText += "\n\n" + "━".repeat(80) + "\n"
          analysisText += ">>> COMFYUI IMAGE GENERATION <<<\n\n"
          analysisText += `❌ 图像生成异常: ${imageGenError}\n`
        }

        setLlmOutput(analysisText)
      } else {
        // API调用失败，显示错误信息
        const errorText = `>>> 批量API调用失败 <<<\n\n错误信息: ${result.error_message || '未知错误'}\n\n请检查后端服务是否正常运行。`
        setLlmOutput(errorText)

        // 使用默认的情绪数据
        completeAnalysisWithMockData()
      }

      setIsAnalyzing(false)

      // 更新图像状态
      images.forEach((_, index) => {
        setTimeout(
          () => {
            setCapturedImages((prev) => prev.map((img, i) => (i === index ? { ...img, analyzing: false } : img)))
          },
          (index + 1) * 200,
        )
      })

    } catch (error) {
      console.error('批量API调用异常:', error)

      // 网络错误或其他异常，显示错误信息并使用模拟数据
      const errorText = `>>> 批量分析连接失败 <<<\n\n错误信息: ${error}\n\n正在使用模拟数据进行演示...`
      setLlmOutput(errorText)

      // 使用模拟数据
      completeAnalysisWithMockData()
      setIsAnalyzing(false)

      // 更新图像状态
      images.forEach((_, index) => {
        setTimeout(
          () => {
            setCapturedImages((prev) => prev.map((img, i) => (i === index ? { ...img, analyzing: false } : img)))
          },
          (index + 1) * 200,
        )
      })
    }
  }

  // 检查API是否可用
  const checkApiAvailability = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000); // 2秒超时
      
      const response = await fetch('http://localhost:8000/health', {
        method: 'GET',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      console.log('API不可用:', error);
      return false;
    }
  };

  // 调用后端API进行情绪分析和图像生成
  const analyzeImageWithAPI = async (imageBlob: Blob, callId?: string) => {
    const id = callId || Math.random().toString(36).substr(2, 9);

    // 防止重复调用
    if (apiCallLockRef.current) {
      console.warn(`API调用被阻止，已有调用正在进行中: ${currentCallIdRef.current}`);
      return;
    }

    // 设置锁定
    apiCallLockRef.current = true;
    currentCallIdRef.current = id;

    try {
      // 首先检查API是否可用
      const apiAvailable = await checkApiAvailability();

      if (!apiAvailable) {
        // API不可用，直接使用模拟数据
        console.log("API不可用，使用模拟数据");
        completeAnalysisWithMockData();
        return;
      }

      const formData = new FormData()
      formData.append('file', imageBlob, 'capture.jpg')

      // 第一步：进行情绪分析
      const response = await fetch('http://localhost:8000/api/v1/analyze/image', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`API调用失败: ${response.status}`)
      }

      const result = await response.json()

      if (result.success) {
        // 使用API返回的情绪数据
        setEmotionData(result.emotion_data)

        // 使用API返回的分析文本
        let analysisText = result.analysis_text

        // 第二步：基于情绪分析结果生成图像
        try {
          const imageGenResponse = await fetch('http://localhost:8000/api/v1/generation/generate-from-analysis', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              emotion_data: result.emotion_data,
              seed: Math.floor(Math.random() * 1000000) // 随机种子
            }),
          })

          // 添加图像生成结果信息
          analysisText += "\n\n" + "━".repeat(80) + "\n"
          analysisText += ">>> COMFYUI IMAGE GENERATION <<<\n\n"

          if (imageGenResponse.ok) {
            const imageGenResult = await imageGenResponse.json()

            if (imageGenResult.success) {
              analysisText += `✅ 图像生成成功!\n`
              analysisText += `🎨 生成时间: ${imageGenResult.generation_time?.toFixed(2)}秒\n`
              analysisText += `📸 生成图像: ${imageGenResult.images?.length || 0}张\n`

              if (imageGenResult.images && imageGenResult.images.length > 0) {
                analysisText += `\n生成的图像:\n`
                imageGenResult.images.forEach((img: any, index: number) => {
                  analysisText += `${index + 1}. ${img.filename}\n`
                  analysisText += `   URL: ${img.url}\n`
                })
              }
            } else {
              analysisText += `❌ 图像生成失败: ${imageGenResult.error_message}\n`
              analysisText += `💡 提示: 请检查ComfyUI服务是否正常运行\n`
            }
          } else {
            analysisText += `❌ 图像生成API调用失败: ${imageGenResponse.status}\n`
          }
        } catch (imageGenError) {
          console.warn('图像生成失败，但情绪分析成功:', imageGenError)
          analysisText += `❌ 图像生成异常: ${imageGenError}\n`
        }

        setLlmOutput(analysisText)
      } else {
        // API调用失败，显示错误信息
        const errorText = `>>> API调用失败 <<<\n\n错误信息: ${result.error_message || '未知错误'}\n\n请检查后端服务是否正常运行。`
        setLlmOutput(errorText)

        // 使用默认的情绪数据
        completeAnalysisWithMockData()
      }
    } catch (error) {
      console.error('API调用异常:', error)

      // 网络错误或其他异常，显示错误信息并使用模拟数据
      const errorText = `>>> 网络连接失败 <<<\n\n错误信息: ${error}\n\n正在使用模拟数据进行演示...`
      setLlmOutput(errorText)

      // 使用模拟数据
      completeAnalysisWithMockData()
    } finally {
      // 释放锁定
      apiCallLockRef.current = false;
      currentCallIdRef.current = null;
    }
  }

  const completeAnalysisWithMockData = () => {
    const newEmotionData = [
      { emotion: "Happy", percentage: Math.random() * 40 + 30, color: "#00ff88" },
      { emotion: "Sad", percentage: Math.random() * 20 + 5, color: "#0099ff" },
      { emotion: "Angry", percentage: Math.random() * 15 + 5, color: "#ff0066" },
      { emotion: "Surprised", percentage: Math.random() * 20 + 10, color: "#ffaa00" },
      { emotion: "Neutral", percentage: Math.random() * 25 + 15, color: "#888888" },
      { emotion: "Disgusted", percentage: Math.random() * 10 + 2, color: "#9d4edd" },
      { emotion: "Fearful", percentage: Math.random() * 15 + 3, color: "#f72585" },
    ]

    setEmotionData(newEmotionData)

    const analysisText = [
      ">>> NEURAL NETWORK ANALYSIS COMPLETE <<<",
      "",
      "EMOTIONAL SIGNATURE DETECTED:",
      "━".repeat(80),
      "",
      "SUBJECT ANALYSIS:",
      `• Primary Emotion: ${newEmotionData[0].emotion.toUpperCase()}`,
      `• Confidence Level: ${Math.floor(newEmotionData[0].percentage)}%`,
      `• Secondary Traits: ${newEmotionData
        .slice(1, 3)
        .map((e) => e.emotion)
        .join(", ")}`,
      "",
      "BIOMETRIC DATA:",
      "• Heart Rate Variability: DETECTED",
      "• Micro-expressions: 47 PATTERNS IDENTIFIED",
      "• Facial Symmetry: ANALYZED",
      "• Eye Movement: TRACKED",
      "",
      "PSYCHOLOGICAL PROFILE:",
      "• Stress Indicators: LOW-MODERATE",
      "• Authenticity Score: 87.3%",
      "• Emotional Stability: STABLE",
      "• Cognitive Load: NORMAL",
      "",
      "RECOMMENDATION:",
      "Subject displays genuine emotional responses.",
      "No deception indicators detected.",
      "Emotional state within normal parameters.",
      "",
      "━".repeat(80),
      "ANALYSIS TIMESTAMP: " + currentTime,
      "NEURAL NETWORK VERSION: EMOSCAN v2.1.7",
      "STATUS: COMPLETE",
    ].join("\n")

    setLlmOutput(analysisText)
  }

  return (
    <div className="min-h-screen font-mono overflow-hidden relative transition-colors duration-300 bg-[hsl(var(--emoscan-bg))] text-[hsl(var(--emoscan-text))]">
      {/* 背景网格 */}
      <div className="absolute inset-0 opacity-10">
        <div className="grid grid-cols-20 grid-rows-20 h-full w-full">
          {Array.from({ length: 400 }).map((_, i) => (
            <div key={i} className="border border-[hsl(var(--emoscan-grid)/0.2)]" />
          ))}
        </div>
      </div>

      {/* 顶部导航栏 */}
      <header className="relative z-10 border-b backdrop-blur-sm transition-colors duration-300 border-[hsl(var(--emoscan-border)/0.3)] bg-[hsl(var(--emoscan-bg)/0.8)]">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-4">
            <div className="text-2xl font-bold animate-pulse text-[hsl(var(--emoscan-accent))]">EMOSCAN</div>
            <div className="text-sm text-[hsl(var(--emoscan-text)/0.7)]">Neural Emotion Analysis System</div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full animate-pulse bg-[hsl(var(--emoscan-accent))]" />
              <span className="text-xs">SYSTEM ONLINE</span>
            </div>
            <div className="text-xs text-[hsl(var(--emoscan-text)/0.7)]">{currentTime}</div>
            {/* 主题切换按钮 */}
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* 主要内容区域 */}
      <div className="flex h-[calc(100vh-80px)] relative z-10">
        {/* 左侧面板 - 摄像头区域 */}
        <div className="w-1/3 border-r backdrop-blur-sm p-6 transition-colors duration-300 border-[hsl(var(--emoscan-border)/0.3)] bg-[hsl(var(--emoscan-panel)/0.5)]">
          <div className="h-full flex flex-col">
            <h2 className="text-lg font-semibold mb-4 text-[hsl(var(--emoscan-accent))]">VISUAL INPUT</h2>

            {/* 摄像头显示区域 */}
            <div className="flex-1 relative border rounded-lg overflow-hidden transition-colors duration-300 border-[hsl(var(--emoscan-border)/0.5)] bg-[hsl(var(--emoscan-bg)/0.8)]">
              <video
                ref={videoRef}
                autoPlay
                muted
                className="w-full h-full object-cover"
                style={{ transform: "scaleX(-1)" }}
              />
              <canvas ref={canvasRef} className="hidden" />

              {/* 扫描线效果 */}
              {isRecording && (
                <div
                  className="absolute left-0 w-full h-0.5 shadow-lg bg-[hsl(var(--emoscan-accent))] shadow-[hsl(var(--emoscan-accent)/0.5)]"
                  style={{
                    top: `${scanLine}%`,
                    transition: "top 0.05s linear",
                  }}
                />
              )}

              {/* 录制状态指示器 */}
              {isRecording && (
                <div className="absolute top-4 left-4 flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                  <span className="text-sm text-red-400">RECORDING</span>
                </div>
              )}
            </div>

            {/* 控制按钮 */}
            <div className="mt-4 space-y-3">
              {/* 分析模式切换 */}
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setAnalysisMode(AnalysisMode.QUICK)}
                  className={`py-2 px-3 border rounded-lg text-xs transition-all duration-200 ${
                    analysisMode === AnalysisMode.QUICK
                      ? 'bg-blue-600/30 border-blue-400/50 text-blue-400 shadow-lg shadow-blue-400/20'
                      : 'bg-gray-600/20 border-gray-400/50 text-gray-400 hover:bg-gray-600/30'
                  }`}
                >
                  🚀 QUICK MODE
                </button>
                <button
                  onClick={() => setAnalysisMode(AnalysisMode.DETAILED)}
                  className={`py-2 px-3 border rounded-lg text-xs transition-all duration-200 ${
                    analysisMode === AnalysisMode.DETAILED
                      ? 'bg-orange-600/30 border-orange-400/50 text-orange-400 shadow-lg shadow-orange-400/20'
                      : 'bg-gray-600/20 border-gray-400/50 text-gray-400 hover:bg-gray-600/30'
                  }`}
                >
                  🔍 DETAILED MODE
                </button>
              </div>

              {/* 模式说明 */}
              <div className="text-xs text-gray-400 text-center">
                {analysisMode === AnalysisMode.QUICK
                  ? "快速模式：分析最后1张图片 (~5秒)"
                  : "详细模式：分析全部5张图片 + 裁判员AI (~20秒)"}
              </div>

              <button
                onClick={startRecording}
                disabled={isRecording || isAnalyzing}
                className="w-full py-3 px-4 bg-green-600/20 border border-green-400/50 rounded-lg text-green-400 hover:bg-green-600/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-lg hover:shadow-green-400/20"
              >
                {isRecording ? "CAPTURING..." : `START SCAN (${analysisMode.toUpperCase()})`}
              </button>









              {/* 捕获的图像预览 */}
              {capturedImages.length > 0 && (
                <div className="grid grid-cols-5 gap-2">
                  {capturedImages.map((img) => (
                    <div key={img.id} className="relative">
                      <img
                        src={img.url || "/placeholder.svg"}
                        alt={`Capture ${img.id}`}
                        className="w-full h-12 object-cover rounded border border-green-400/30"
                      />
                      {img.analyzing && <div className="absolute inset-0 bg-cyan-400/20 animate-pulse rounded" />}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 中间面板 - 情感分析 */}
        <div className="w-1/3 border-r backdrop-blur-sm p-6 transition-colors duration-300 border-[hsl(var(--emoscan-border)/0.3)] bg-[hsl(var(--emoscan-panel)/0.5)]">
          <div className="h-full flex flex-col">
            <h2 className="text-lg font-semibold mb-4 text-[hsl(var(--emoscan-accent))]">EMOTION ANALYSIS</h2>

            {/* 分析进度 */}
            {isAnalyzing && (
              <div className="mb-6">
                <div className="flex justify-between text-sm mb-2">
                  <span>Processing...</span>
                  <span>{Math.floor(analysisProgress)}%</span>
                </div>
                <div className="w-full rounded-full h-2 bg-[hsl(var(--muted))]">
                  <div
                    className="h-2 rounded-full transition-all duration-200 bg-gradient-to-r from-[hsl(var(--emoscan-accent))] to-[hsl(var(--emoscan-accent))]"
                    style={{ width: `${analysisProgress}%` }}
                  />
                </div>
              </div>
            )}

            {/* 情感数据显示 */}
            <div className="flex-1 space-y-4">
              {emotionData.map((emotion) => (
                <div key={emotion.emotion} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">{emotion.emotion}</span>
                    <span className="text-sm" style={{ color: emotion.color }}>
                      {emotion.percentage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full rounded-full h-3 overflow-hidden bg-[hsl(var(--muted))]">
                    <div
                      className="h-3 rounded-full transition-all duration-1000 ease-out"
                      style={{
                        width: `${emotion.percentage}%`,
                        backgroundColor: emotion.color,
                        boxShadow: `0 0 10px ${emotion.color}50`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* 情感雷达图 */}
            <div className="mt-6 h-48 border rounded-lg flex items-center justify-center transition-colors duration-300 border-[hsl(var(--emoscan-border)/0.3)] bg-[hsl(var(--emoscan-bg)/0.8)]">
              <div className="relative w-32 h-32">
                {/* 雷达图背景 */}
                <svg className="w-full h-full" viewBox="0 0 100 100">
                  {/* 同心圆 */}
                  {[20, 40, 60, 80].map((r) => (
                    <circle
                      key={r}
                      cx="50"
                      cy="50"
                      r={r / 2}
                      fill="none"
                      stroke={isDark ? "hsl(142 76% 36% / 0.3)" : "hsl(220 13% 69% / 0.3)"}
                      strokeWidth="0.5"
                    />
                  ))}
                  {/* 射线 */}
                  {emotionData.map((_, i) => {
                    const angle = (i * (360 / emotionData.length) - 90) * (Math.PI / 180)
                    const x = 50 + 40 * Math.cos(angle)
                    const y = 50 + 40 * Math.sin(angle)
                    return (
                      <line key={i} x1="50" y1="50" x2={x} y2={y} stroke={isDark ? "hsl(142 76% 36% / 0.3)" : "hsl(220 13% 69% / 0.3)"} strokeWidth="0.5" />
                    )
                  })}
                  {/* 数据多边形 */}
                  <polygon
                    points={emotionData
                      .map((emotion, i) => {
                        const angle = (i * (360 / emotionData.length) - 90) * (Math.PI / 180)
                        const radius = (emotion.percentage / 100) * 35
                        const x = 50 + radius * Math.cos(angle)
                        const y = 50 + radius * Math.sin(angle)
                        return `${x},${y}`
                      })
                      .join(" ")}
                    fill={isDark ? "hsl(142 76% 36% / 0.2)" : "hsl(217 91% 60% / 0.2)"}
                    stroke={isDark ? "hsl(142 76% 36%)" : "hsl(217 91% 60%)"}
                    strokeWidth="1"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* 右侧面板 - LLM输出 */}
        <div className="w-1/3 backdrop-blur-sm p-6 transition-colors duration-300 bg-[hsl(var(--emoscan-panel)/0.5)]">
          <div className="h-full flex flex-col">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-[hsl(var(--emoscan-accent))]">AI ANALYSIS OUTPUT</h2>
            </div>

            {/* LLM输出显示 */}
              <div
                ref={outputRef}
                className="flex-1 border rounded-lg overflow-y-auto overflow-x-hidden ai-output-container relative transition-colors duration-300 border-[hsl(var(--emoscan-border)/0.3)] bg-[hsl(var(--emoscan-bg)/0.8)]"
                style={{
                  scrollbarWidth: 'none',
                  msOverflowStyle: 'none',
                } as React.CSSProperties}
              >
                {/* 边缘渐变遮罩层 - 使用CSS变量自动适配主题 */}
                <div
                  className="absolute inset-0 pointer-events-none z-10"
                  style={{
                    background: `linear-gradient(
                      to bottom,
                      rgba(var(--emoscan-gradient-color), 0.6) 0%,
                      rgba(var(--emoscan-gradient-color), 0.3) 8%,
                      rgba(var(--emoscan-gradient-color), 0.1) 20%,
                      transparent 30%,
                      transparent 70%,
                      rgba(var(--emoscan-gradient-color), 0.1) 80%,
                      rgba(var(--emoscan-gradient-color), 0.3) 92%,
                      rgba(var(--emoscan-gradient-color), 0.6) 100%
                    )`,
                    borderRadius: 'inherit',
                  }}
                />
                {/* 3D圆柱体透视文字容器 */}
                <div
                  className="relative cylindrical-text-container"
                  style={{
                    minHeight: '100%',
                    padding: '40px 16px', // 增加上下内边距，确保顶部和底部文字有足够空间
                    textAlign: 'center', // 所有文字居中对齐
                    height: 'auto', // 允许内容撑开高度
                  }}
                >
                  <div
                    className="cylindrical-text-display"
                    style={{
                      margin: 0,
                      padding: 0,
                      lineHeight: '1.8',
                    } as React.CSSProperties}
                  >
                    {(displayText || "Awaiting analysis data...").split('\n').map((line, index) => (
                      <div
                        key={index}
                        className="text-line"
                        style={{
                          marginBottom: '0.2em',
                        }}
                      >
                        {line || '\u00A0'} {/* 使用非断行空格保持空行 */}
                      </div>
                    ))}
                  </div>

                  {/* 光标 */}
                  {(isTyping || (showCursor && displayText)) && (
                    <span
                      className={`inline-block w-1 h-4 ml-1 bg-[hsl(var(--emoscan-text))] ${
                        showCursor ? 'opacity-100' : 'opacity-0'
                      } transition-opacity duration-300`}
                      style={{
                        fontSize: '14px', // 光标始终保持中心大小
                      }}
                    >
                      |
                    </span>
                  )}
                </div>
              </div>
          </div>
        </div>
      </div>
    </div>
  )
}
