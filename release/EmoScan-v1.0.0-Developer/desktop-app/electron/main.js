const { app, BrowserWindow, Menu, shell, ipcMain } = require('electron')
const path = require('path')
const isDev = process.env.NODE_ENV === 'development'
const http = require('http')
const waitOn = require('wait-on')

// 保持对窗口对象的全局引用，如果不这样做，当JavaScript对象被垃圾回收时，窗口将自动关闭
let mainWindow

// 检测可用的端口
async function findAvailablePort(startPort, endPort) {
  let port = startPort
  while (port <= endPort) {
    try {
      // 尝试连接到端口
      await new Promise((resolve, reject) => {
        const req = http.get(`http://localhost:${port}`, () => {
          // 如果连接成功，说明端口在使用中
          resolve(true)
        }).on('error', (err) => {
          // 如果连接失败，可能是端口未被使用
          if (err.code === 'ECONNREFUSED') {
            resolve(false)
          } else {
            reject(err)
          }
        })
        req.setTimeout(1000, () => {
          req.destroy()
          resolve(false)
        })
      })
      
      // 尝试下一个端口
      port++
    } catch (error) {
      console.error(`Error checking port ${port}:`, error)
      port++
    }
  }
  
  // 如果所有端口都在使用中，返回null
  return null
}

// 等待Next.js开发服务器启动并找到其端口
async function waitForNextServer() {
  // 尝试常用的Next.js端口
  const portsToCheck = [3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009, 3010]
  
  console.log('等待Next.js开发服务器启动...')
  
  // 增加重试次数
  const maxRetries = 3
  
  for (const port of portsToCheck) {
    for (let retry = 0; retry < maxRetries; retry++) {
      try {
        // 增加超时时间到2000ms
        await waitOn({
          resources: [`http://localhost:${port}`],
          timeout: 2000,
          interval: 200,
        })
        console.log(`Next.js开发服务器在端口 ${port} 上运行`)
        return port
      } catch (err) {
        console.log(`尝试 ${retry + 1}/${maxRetries}: 端口 ${port} 未运行Next.js服务`)
        
        // 最后一次重试失败后，等待一小段时间再继续
        if (retry === maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, 500))
        }
      }
    }
  }
  
  // 如果常规检测失败，尝试直接使用最后看到的端口（通常是3003或3004）
  const fallbackPorts = [3004, 3003, 3005]
  for (const port of fallbackPorts) {
    console.log(`常规检测失败，尝试直接使用端口${port}`)
    try {
      // 直接检查端口
      await waitOn({
        resources: [`http://localhost:${port}`],
        timeout: 3000,
        interval: 300,
      })
      console.log(`成功连接到端口${port}`)
      return port
    } catch (err) {
      console.log(`无法连接到端口${port}`)
    }
  }
  
  console.log('无法找到运行中的Next.js开发服务器')
  return null
}

function createWindow() {
  // 创建浏览器窗口
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    title: 'EmoScan', // 设置窗口标题
    webPreferences: {
      nodeIntegration: false, // 出于安全考虑
      contextIsolation: true, // 启用上下文隔离
      enableRemoteModule: false, // 禁用远程模块
      preload: path.join(__dirname, 'preload.js'), // 预加载脚本
      webSecurity: true, // 启用web安全
    },
    icon: path.join(__dirname, '../public/placeholder-logo.png'), // 应用图标
    show: false, // 先不显示，等准备好后再显示
    titleBarStyle: 'default', // 使用默认标题栏
    frame: true, // 显示窗口框架
  })

  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()

    // 确保窗口标题为EmoScan
    mainWindow.setTitle('EmoScan')

    // 开发模式下打开开发者工具
    if (isDev) {
      mainWindow.webContents.openDevTools()
    }
  })

  // 加载应用
  if (isDev) {
    // 开发模式：连接到Next.js开发服务器
    // 延迟一段时间等待Next.js服务器启动
    console.log('等待Next.js服务器启动...')
    setTimeout(() => {
      // 动态检测Next.js开发服务器端口
      waitForNextServer().then(port => {
        if (port) {
          console.log(`加载Next.js开发服务器: http://localhost:${port}`)
          mainWindow.loadURL(`http://localhost:${port}`)
        } else {
          console.error('无法找到Next.js开发服务器，尝试使用备用端口')
          // 尝试多个备用端口
          const tryLoadPort = (ports, index = 0) => {
            if (index >= ports.length) {
              console.error('所有备用端口都失败了')
              return
            }
            
            const port = ports[index]
            console.log(`尝试备用端口: ${port}`)
            
            mainWindow.loadURL(`http://localhost:${port}`)
              .then(() => {
                console.log(`成功加载端口 ${port}`)
              })
              .catch(() => {
                console.log(`端口 ${port} 加载失败，尝试下一个端口`)
                tryLoadPort(ports, index + 1)
              })
          }
          
          tryLoadPort([3004, 3003, 3005, 3002])
        }
      }).catch(err => {
        console.error('加载Next.js开发服务器时出错:', err)
        mainWindow.loadURL('http://localhost:3004')
      })
    }, 5000) // 等待5秒，给Next.js服务器足够的启动时间
    
    // 开发模式下的热重载
    try {
      require('electron-reload')(__dirname, {
        electron: path.join(__dirname, '..', 'node_modules', '.bin', 'electron'),
        hardResetMethod: 'exit'
      })
    } catch (error) {
      console.log('electron-reload not available in production')
    }
  } else {
    // 生产模式：加载构建后的文件
    mainWindow.loadFile(path.join(__dirname, '../out/index.html'))
  }

  // 当窗口关闭时触发
  mainWindow.on('closed', () => {
    // 取消引用window对象，如果你的应用支持多窗口，通常会把多个window对象存放在一个数组里，与此同时，你应该删除相应的元素
    mainWindow = null
  })

  // 处理外部链接
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  // 阻止导航到外部URL
  mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {
    const parsedUrl = new URL(navigationUrl)
    
    // 允许导航到localhost上的任何端口
    if (isDev && parsedUrl.hostname === 'localhost') {
      return
    }
    
    if (parsedUrl.origin !== 'http://localhost:3000' && !isDev) {
      event.preventDefault()
    }
  })

  // 监听页面标题变化，确保始终显示EmoScan
  mainWindow.webContents.on('page-title-updated', (event) => {
    event.preventDefault() // 阻止页面更改标题
    mainWindow.setTitle('EmoScan')
  })
}

// 当Electron完成初始化并准备创建浏览器窗口时调用此方法
app.whenReady().then(() => {
  createWindow()

  // 在macOS上，当点击dock图标并且没有其他窗口打开时，通常会重新创建一个窗口
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })

  // 设置应用菜单
  createMenu()
})

// 当所有窗口都关闭时退出应用
app.on('window-all-closed', () => {
  // 在macOS上，应用和它们的菜单栏通常会保持活跃状态，直到用户使用Cmd + Q明确退出
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// 创建应用菜单
function createMenu() {
  const template = [
    {
      label: 'EmoScan',
      submenu: [
        {
          label: '关于 EmoScan',
          role: 'about'
        },
        { type: 'separator' },
        {
          label: '退出',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit()
          }
        }
      ]
    },
    {
      label: '编辑',
      submenu: [
        { label: '撤销', accelerator: 'CmdOrCtrl+Z', role: 'undo' },
        { label: '重做', accelerator: 'Shift+CmdOrCtrl+Z', role: 'redo' },
        { type: 'separator' },
        { label: '剪切', accelerator: 'CmdOrCtrl+X', role: 'cut' },
        { label: '复制', accelerator: 'CmdOrCtrl+C', role: 'copy' },
        { label: '粘贴', accelerator: 'CmdOrCtrl+V', role: 'paste' }
      ]
    },
    {
      label: '视图',
      submenu: [
        { label: '重新加载', accelerator: 'CmdOrCtrl+R', role: 'reload' },
        { label: '强制重新加载', accelerator: 'CmdOrCtrl+Shift+R', role: 'forceReload' },
        { label: '开发者工具', accelerator: 'F12', role: 'toggleDevTools' },
        { type: 'separator' },
        { label: '实际大小', accelerator: 'CmdOrCtrl+0', role: 'resetZoom' },
        { label: '放大', accelerator: 'CmdOrCtrl+Plus', role: 'zoomIn' },
        { label: '缩小', accelerator: 'CmdOrCtrl+-', role: 'zoomOut' },
        { type: 'separator' },
        { label: '全屏', accelerator: 'F11', role: 'togglefullscreen' }
      ]
    },
    {
      label: '窗口',
      submenu: [
        { label: '最小化', accelerator: 'CmdOrCtrl+M', role: 'minimize' },
        { label: '关闭', accelerator: 'CmdOrCtrl+W', role: 'close' }
      ]
    }
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

// IPC通信处理
ipcMain.handle('get-app-version', () => {
  return app.getVersion()
})

ipcMain.handle('get-platform', () => {
  return process.platform
})

// 处理应用退出
ipcMain.handle('quit-app', () => {
  app.quit()
})

// 错误处理
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error)
})

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason)
})
