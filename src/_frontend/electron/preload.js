const { contextBridge, ipcRenderer } = require('electron')

// 暴露受保护的方法，允许渲染进程使用ipcRenderer，而不暴露整个对象
contextBridge.exposeInMainWorld('electronAPI', {
  // 应用信息
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getPlatform: () => ipcRenderer.invoke('get-platform'),
  
  // 应用控制
  quitApp: () => ipcRenderer.invoke('quit-app'),
  
  // 系统信息
  isElectron: true,
  
  // 文件系统操作（如果需要的话）
  // 注意：这些操作需要在主进程中实现相应的处理器
  
  // 通知系统
  showNotification: (title, body) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, { body })
    }
  },
  
  // 请求通知权限
  requestNotificationPermission: async () => {
    if ('Notification' in window) {
      return await Notification.requestPermission()
    }
    return 'denied'
  }
})

// 在窗口加载完成后执行
window.addEventListener('DOMContentLoaded', () => {
  // 可以在这里添加一些初始化代码
  console.log('EmoScan Electron App loaded')
  
  // 添加Electron特有的样式类
  document.body.classList.add('electron-app')
  
  // 设置应用标题
  document.title = 'EmoScan - 情感分析系统'
})
