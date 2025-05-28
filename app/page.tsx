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
  ])
  const [llmOutput, setLlmOutput] = useState("")
  const [scanLine, setScanLine] = useState(0)

  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)

  // 扫描线动画
  useEffect(() => {
    const interval = setInterval(() => {
      setScanLine((prev) => (prev + 1) % 100)
    }, 50)
    return () => clearInterval(interval)
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

  const startAnalysis = (images: CapturedImage[]) => {
    setIsRecording(false)
    setIsAnalyzing(true)
    stopCamera()

    let progress = 0
    const progressInterval = setInterval(() => {
      progress += Math.random() * 15
      if (progress >= 100) {
        progress = 100
        clearInterval(progressInterval)
        completeAnalysis()
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

  const completeAnalysis = () => {
    setIsAnalyzing(false)

    const newEmotionData = [
      { emotion: "Happy", percentage: Math.random() * 40 + 30, color: "#00ff88" },
      { emotion: "Sad", percentage: Math.random() * 20 + 5, color: "#0099ff" },
      { emotion: "Angry", percentage: Math.random() * 15 + 5, color: "#ff0066" },
      { emotion: "Surprised", percentage: Math.random() * 20 + 10, color: "#ffaa00" },
      { emotion: "Neutral", percentage: Math.random() * 25 + 15, color: "#888888" },
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
      "ANALYSIS TIMESTAMP: " + new Date().toLocaleString(),
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
            <div className="text-xs text-green-400/70">{new Date().toLocaleTimeString()}</div>
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
              <button
                onClick={startRecording}
                disabled={isRecording || isAnalyzing}
                className="w-full py-3 px-4 bg-green-600/20 border border-green-400/50 rounded-lg text-green-400 hover:bg-green-600/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-lg hover:shadow-green-400/20"
              >
                {isRecording ? "CAPTURING..." : "START SCAN"}
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
                    const angle = (i * 72 - 90) * (Math.PI / 180)
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
                        const angle = (i * 72 - 90) * (Math.PI / 180)
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

            <div className="flex-1 border border-green-400/30 rounded-lg bg-black/80 p-4 overflow-auto">
              <pre className="text-xs text-green-400 whitespace-pre-wrap font-mono leading-relaxed">
                {llmOutput || "Awaiting analysis data..."}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
