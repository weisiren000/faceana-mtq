const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  sendMessage: (channel, data) => ipcRenderer.send(channel, data),
  onReply: (channel, func) => {
    // Deliberately strip event as it includes `sender`
    ipcRenderer.on(channel, (event, ...args) => func(...args));
  },
  // 你可以在这里暴露更多你需要的 API
  getAppVersion: () => ipcRenderer.invoke('get-app-version') // 假设主进程有对应的 handle
});

// 示例：主进程可以通过 'get-app-version' channel 调用这个
ipcRenderer.handle('get-app-version', async () => {
  const { app } = require('electron');
  return app.getVersion();
});