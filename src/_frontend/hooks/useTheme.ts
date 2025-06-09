'use client'

import { useState, useEffect } from 'react'

export type Theme = 'dark' | 'light'

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    // 在初始化时就从localStorage读取主题
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem('emoscan-theme') as Theme
      if (savedTheme && (savedTheme === 'dark' || savedTheme === 'light')) {
        return savedTheme
      }
    }
    return 'dark'
  })
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return

    // 应用主题到document
    const root = document.documentElement

    // 清除所有主题类
    root.classList.remove('dark', 'light')

    // 添加当前主题类
    root.classList.add(theme)

    // 同时设置data属性用于CSS选择器
    root.setAttribute('data-theme', theme)

    // 保存到localStorage
    localStorage.setItem('emoscan-theme', theme)

    console.log('Theme applied:', theme, 'Classes:', root.classList.toString(), 'Data-theme:', root.getAttribute('data-theme'))
  }, [theme, mounted])

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark')
  }

  return {
    theme,
    setTheme,
    toggleTheme,
    isDark: theme === 'dark',
    isLight: theme === 'light',
    mounted
  }
}
