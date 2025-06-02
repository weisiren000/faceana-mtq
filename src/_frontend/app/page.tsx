"use client"

import { useState, useRef, useEffect } from "react"

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
  const [currentTime, setCurrentTime] = useState("")
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>(AnalysisMode.QUICK)

  // 使用打字机效果
  const { displayText, isTyping, showCursor, typingProgress } = useTypewriter(llmOutput, 25)

  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const outputRef = useRef<HTMLDivElement>(null)

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

  // 时间更新
  useEffect(() => {
    const updateTime = () => {
      setCurrentTime(new Date().toLocaleTimeString())
    }

    // 立即更新一次
    updateTime()

    // 每秒更新
    const interval = setInterval(updateTime, 1000)
    return () => clearInterval(interval)
  }, [])

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
          scroll-behavior: smooth;
          will-change: scroll-position;
          -webkit-overflow-scrolling: touch;
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
            line.style.color = `rgba(0, 255, 136, ${opacity})`
            line.style.textShadow = `
              0 0 ${12 * opacity}px rgba(0,255,136,${opacity * 0.5}),
              0 ${1.5 * opacity}px ${6 * opacity}px rgba(0,0,0,0.3),
              0 0 ${25 * opacity}px rgba(0,255,136,${opacity * 0.25})
            `
          })
        })
      }

      // 丝滑滚动处理
      let isScrolling = false
      let scrollTimeout: number

      const handleWheel = (e: WheelEvent) => {
        e.preventDefault()

        const scrollAmount = e.deltaY * 0.8 // 调整滚动灵敏度
        const currentScrollTop = element.scrollTop
        const scrollHeight = element.scrollHeight
        const clientHeight = element.clientHeight
        const maxScroll = scrollHeight - clientHeight

        if (maxScroll <= 0) return // 内容不够长，不需要滚动

        let newScrollTop = Math.max(0, Math.min(maxScroll, currentScrollTop + scrollAmount))

        // 使用requestAnimationFrame实现丝滑滚动
        if (!isScrolling) {
          isScrolling = true

          const smoothScroll = () => {
            const diff = newScrollTop - element.scrollTop
            const step = diff * 0.15 // 缓动系数，值越小越平滑

            if (Math.abs(diff) > 0.5) {
              element.scrollTop += step
              requestAnimationFrame(smoothScroll)
            } else {
              element.scrollTop = newScrollTop
              isScrolling = false
            }
          }

          requestAnimationFrame(smoothScroll)
        } else {
          // 如果正在滚动，更新目标位置
          newScrollTop = Math.max(0, Math.min(maxScroll, newScrollTop + scrollAmount))
        }

        // 清除之前的超时，设置新的超时来重置滚动状态
        clearTimeout(scrollTimeout)
        scrollTimeout = window.setTimeout(() => {
          isScrolling = false
        }, 150)
      }

      // 初始化文本行样式
      const initializeTextLines = () => {
        // 延迟执行，确保DOM已更新
        setTimeout(() => {
          handleScroll()
        }, 50)
      }

      // 添加滚动监听器
      element.addEventListener('scroll', handleScroll, { passive: true })
      element.addEventListener('wheel', handleWheel, { passive: false })

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
        element.removeEventListener('wheel', handleWheel)
        observer.disconnect()
        document.head.removeChild(style)

        // 清理动画帧和超时
        if (animationId) {
          cancelAnimationFrame(animationId)
        }
        if (scrollTimeout) {
          clearTimeout(scrollTimeout)
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
    setIsRecording(false)
    setIsAnalyzing(true)
    stopCamera()

    // 根据分析模式选择不同的处理方式
    if (analysisMode === AnalysisMode.DETAILED) {
      // 详细模式：分析所有图像
      await analyzeBatchImages(images)
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
            await analyzeImageWithAPI(blob)
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

            return
          } catch (error) {
            console.error('图像转换失败:', error)
          }
        }
      }
    }

    // 如果API调用失败，使用模拟数据
    let progress = 0
    const progressInterval = setInterval(() => {
      progress += Math.random() * 15
      if (progress >= 100) {
        progress = 100
        clearInterval(progressInterval)
        completeAnalysisWithMockData()
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
        setLlmOutput(result.analysis_text)
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

  // 调用后端API进行情绪分析
  const analyzeImageWithAPI = async (imageBlob: Blob) => {
    try {
      const formData = new FormData()
      formData.append('file', imageBlob, 'capture.jpg')

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
        setLlmOutput(result.analysis_text)
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
    <div className="min-h-screen bg-black text-green-400 font-mono overflow-hidden relative">
      {/* 背景网格 */}
      <div className="absolute inset-0 opacity-10">
        <div className="grid grid-cols-20 grid-rows-20 h-full w-full">
          {Array.from({ length: 400 }).map((_, i) => (
            <div key={i} className="border border-green-400/20" />
          ))}
        </div>
      </div>

      {/* 顶部导航栏 */}
      <header className="relative z-10 border-b border-green-400/30 bg-black/80 backdrop-blur-sm">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-4">
            <div className="text-2xl font-bold text-cyan-400 animate-pulse">EMOSCAN</div>
            <div className="text-sm text-green-400/70">Neural Emotion Analysis System</div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-xs">SYSTEM ONLINE</span>
            </div>
            <div className="text-xs text-green-400/70">{currentTime}</div>
          </div>
        </div>
      </header>

      {/* 主要内容区域 */}
      <div className="flex h-[calc(100vh-80px)] relative z-10">
        {/* 左侧面板 - 摄像头区域 */}
        <div className="w-1/3 border-r border-green-400/30 bg-black/50 backdrop-blur-sm p-6">
          <div className="h-full flex flex-col">
            <h2 className="text-lg font-semibold mb-4 text-cyan-400">VISUAL INPUT</h2>

            {/* 摄像头显示区域 */}
            <div className="flex-1 relative border border-green-400/50 rounded-lg overflow-hidden bg-black/80">
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
                  className="absolute left-0 w-full h-0.5 bg-cyan-400 shadow-lg shadow-cyan-400/50"
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

              {/* 测试按钮 */}
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => {
                    const testText = ">>> TESTING TYPEWRITER EFFECT <<<\n\nThis is a test of the typewriter effect.\nEach character should appear one by one,\nwith natural pauses at punctuation marks.\n\nThe cursor should blink at the end!"
                    setLlmOutput(testText)
                  }}
                  className="py-2 px-3 bg-cyan-600/20 border border-cyan-400/50 rounded-lg text-cyan-400 hover:bg-cyan-600/30 transition-all duration-200 text-xs"
                >
                  TEST TYPEWRITER
                </button>
                <button
                  onClick={() => setLlmOutput("")}
                  className="py-2 px-3 bg-red-600/20 border border-red-400/50 rounded-lg text-red-400 hover:bg-red-600/30 transition-all duration-200 text-xs"
                >
                  CLEAR OUTPUT
                </button>
              </div>

              {/* API测试按钮 */}
              <button
                onClick={async () => {
                  setLlmOutput(">>> 测试后端API连接 <<<\n\n正在连接到后端服务器...")
                  try {
                    const response = await fetch('http://localhost:8000/health')
                    if (response.ok) {
                      const data = await response.json()
                      setLlmOutput(`>>> API连接成功 <<<\n\n服务状态: ${data.status}\n服务名称: ${data.service}\n版本: ${data.version}\n\n后端API已就绪，可以进行情绪分析！`)
                    } else {
                      setLlmOutput(`>>> API连接失败 <<<\n\n状态码: ${response.status}\n\n请确保后端服务器正在运行。`)
                    }
                  } catch (error) {
                    setLlmOutput(`>>> API连接异常 <<<\n\n错误信息: ${error}\n\n请检查:\n1. 后端服务器是否启动\n2. 端口8000是否可用\n3. 网络连接是否正常`)
                  }
                }}
                className="w-full py-2 px-3 bg-purple-600/20 border border-purple-400/50 rounded-lg text-purple-400 hover:bg-purple-600/30 transition-all duration-200 text-xs"
              >
                TEST API CONNECTION
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
        <div className="w-1/3 border-r border-green-400/30 bg-black/50 backdrop-blur-sm p-6">
          <div className="h-full flex flex-col">
            <h2 className="text-lg font-semibold mb-4 text-cyan-400">EMOTION ANALYSIS</h2>

            {/* 分析进度 */}
            {isAnalyzing && (
              <div className="mb-6">
                <div className="flex justify-between text-sm mb-2">
                  <span>Processing...</span>
                  <span>{Math.floor(analysisProgress)}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-cyan-400 to-green-400 h-2 rounded-full transition-all duration-200"
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
                  <div className="w-full bg-gray-800 rounded-full h-3 overflow-hidden">
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
            <div className="mt-6 h-48 border border-green-400/30 rounded-lg bg-black/80 flex items-center justify-center">
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
                      stroke="rgb(34 197 94 / 0.3)"
                      strokeWidth="0.5"
                    />
                  ))}
                  {/* 射线 */}
                  {emotionData.map((_, i) => {
                    const angle = (i * (360 / emotionData.length) - 90) * (Math.PI / 180)
                    const x = 50 + 40 * Math.cos(angle)
                    const y = 50 + 40 * Math.sin(angle)
                    return (
                      <line key={i} x1="50" y1="50" x2={x} y2={y} stroke="rgb(34 197 94 / 0.3)" strokeWidth="0.5" />
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
                    fill="rgb(34 197 94 / 0.2)"
                    stroke="rgb(34 197 94)"
                    strokeWidth="1"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* 右侧面板 - LLM输出 */}
        <div className="w-1/3 bg-black/50 backdrop-blur-sm p-6">
          <div className="h-full flex flex-col">
            <h2 className="text-lg font-semibold mb-4 text-cyan-400">AI ANALYSIS OUTPUT</h2>

            <div
              ref={outputRef}
              className="flex-1 border border-green-400/30 rounded-lg bg-black/80 overflow-y-auto overflow-x-hidden ai-output-container relative"
              style={{
                scrollbarWidth: 'none',
                msOverflowStyle: 'none',
              } as React.CSSProperties}
            >
              {/* 边缘渐变遮罩层 - 调整为更温和的渐变，确保内容可见 */}
              <div
                className="absolute inset-0 pointer-events-none z-10"
                style={{
                  background: `linear-gradient(
                    to bottom,
                    rgba(0,0,0,0.6) 0%,
                    rgba(0,0,0,0.3) 8%,
                    rgba(0,0,0,0.1) 20%,
                    transparent 30%,
                    transparent 70%,
                    rgba(0,0,0,0.1) 80%,
                    rgba(0,0,0,0.3) 92%,
                    rgba(0,0,0,0.6) 100%
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
                    className={`inline-block w-1 h-4 ml-1 bg-green-400 ${
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
