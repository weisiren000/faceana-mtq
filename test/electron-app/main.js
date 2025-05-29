const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

function createWindow () {
  // 创建浏览器窗口
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'), // 指定预加载脚本
      contextIsolation: true, // 推荐开启，增强安全性
      nodeIntegration: false // 推荐关闭，通过 preload 暴露 API
    }
  });

  // 加载 index.html
  mainWindow.loadFile('index.html');

  // 打开开发者工具 (可选)
  // mainWindow.webContents.openDevTools();
}

// Electron会在初始化完成并且准备好创建浏览器窗口时调用这个方法
app.whenReady().then(() => {
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