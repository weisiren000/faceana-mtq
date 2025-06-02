const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

function createWindow () {
  // 创建浏览器窗口 - 适配EMOSCAN应用的尺寸
  const mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'), // 指定预加载脚本
      contextIsolation: true, // 推荐开启，增强安全性
      nodeIntegration: false, // 推荐关闭，通过 preload 暴露 API
      webSecurity: false, // 允许加载本地开发服务器
      allowRunningInsecureContent: true, // 允许HTTP内容
      experimentalFeatures: true, // 启用实验性功能
      enableRemoteModule: false, // 禁用remote模块（安全考虑）
      sandbox: false // 禁用沙盒模式以允许更多权限
    },
    titleBarStyle: 'default',
    icon: null // 可以后续添加应用图标
  });

  // 加载 Next.js 开发服务器
  const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

  // 设置权限处理
  mainWindow.webContents.session.setPermissionRequestHandler((webContents, permission, callback) => {
    // 自动授予摄像头、麦克风等权限
    if (permission === 'camera' || permission === 'microphone' || permission === 'media') {
      callback(true);
    } else {
      callback(false);
    }
  });

  // 处理权限检查
  mainWindow.webContents.session.setPermissionCheckHandler((webContents, permission, requestingOrigin, details) => {
    if (permission === 'camera' || permission === 'microphone' || permission === 'media') {
      return true;
    }
    return false;
  });

  if (isDev) {
    // 开发模式：加载Next.js开发服务器
    mainWindow.loadURL('http://localhost:3000');
    // 打开开发者工具
    mainWindow.webContents.openDevTools();
  } else {
    // 生产模式：加载打包后的文件
    mainWindow.loadFile('index.html');
  }
}

// Electron会在初始化完成并且准备好创建浏览器窗口时调用这个方法
app.whenReady().then(() => {
  // 设置应用级别的权限
  app.commandLine.appendSwitch('enable-features', 'VaapiVideoDecoder');
  app.commandLine.appendSwitch('disable-features', 'VizDisplayCompositor');
  app.commandLine.appendSwitch('enable-unsafe-webgpu');
  app.commandLine.appendSwitch('enable-webgl');
  app.commandLine.appendSwitch('enable-accelerated-2d-canvas');

  createWindow();

  app.on('activate', function () {
    // 在 macOS 系统上，当单击dock图标并且没有其他窗口打开时，
    // 通常在应用程序中重新创建一个窗口。
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// 当所有窗口都被关闭时退出程序。
app.on('window-all-closed', function () {
  // 在 macOS 上，除非用户用 Cmd + Q 确定地退出，
  // 否则绝大部分应用及其菜单栏会保持激活。
  if (process.platform !== 'darwin') app.quit();
});

// 你可以在这个文件中包含应用程序剩余的主进程代码。
// 也可以将它们放在单独的文件中并在这里 require。

// 示例：监听来自渲染进程的消息
ipcMain.on('say-hello', (event, arg) => {
  console.log(arg); // 会在 Node 控制台输出 "Hello from Renderer!"
  event.reply('hello-reply', 'Hello from Main!'); // 向渲染进程发送回复
});