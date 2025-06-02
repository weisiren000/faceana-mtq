'use client'

import { useEffect } from 'react'

export default function ClientBodyClass() {
  useEffect(() => {
    // 检查是否在Electron环境中
    if (typeof window !== 'undefined' && window.electronAPI) {
      // 安全地添加electron-app类，避免hydration不匹配
      document.body.classList.add('electron-app')
    }
  }, [])

  // 这个组件不渲染任何内容
  return null
}
