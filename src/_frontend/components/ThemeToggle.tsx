'use client'

import { useTheme } from '@/hooks/useTheme'

export function ThemeToggle() {
  const { theme, toggleTheme, isDark, mounted } = useTheme()

  // 防止服务端渲染不匹配 - 简化处理
  if (!mounted) {
    return (
      <button
        className="w-12 h-6 rounded-full bg-gray-300 border border-gray-400 animate-pulse"
        disabled
        title="加载中..."
      />
    )
  }

  const handleToggle = () => {
    console.log('Theme toggle clicked, current theme:', theme)
    console.log('Document classes before:', document.documentElement.classList.toString())
    toggleTheme()
    setTimeout(() => {
      console.log('Document classes after:', document.documentElement.classList.toString())
    }, 100)
  }

  return (
    <button
      onClick={handleToggle}
      className={`
        relative inline-flex items-center justify-center
        w-12 h-6 rounded-full transition-all duration-300
        ${isDark 
          ? 'bg-green-600/30 border border-green-400/50 hover:bg-green-600/40' 
          : 'bg-gray-300 border border-gray-400 hover:bg-gray-400'
        }
        focus:outline-none focus:ring-2 focus:ring-offset-2
        ${isDark ? 'focus:ring-green-400' : 'focus:ring-blue-400'}
      `}
      title={`切换到${isDark ? '浅色' : '深色'}主题`}
    >
      {/* 滑块 */}
      <div
        className={`
          absolute w-4 h-4 rounded-full transition-all duration-300 transform
          ${isDark 
            ? 'translate-x-3 bg-green-400 shadow-lg shadow-green-400/50' 
            : '-translate-x-3 bg-white shadow-lg'
          }
        `}
      />
      
      {/* 图标 */}
      <div className="flex items-center justify-between w-full px-1">
        {/* 太阳图标 */}
        <div className={`text-xs transition-opacity duration-300 ${isDark ? 'opacity-50' : 'opacity-100'}`}>
          ☀️
        </div>
        
        {/* 月亮图标 */}
        <div className={`text-xs transition-opacity duration-300 ${isDark ? 'opacity-100' : 'opacity-50'}`}>
          🌙
        </div>
      </div>
    </button>
  )
}
