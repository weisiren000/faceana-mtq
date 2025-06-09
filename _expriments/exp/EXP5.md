# EXP5 - Electron应用权限配置与3D文字透视效果实现

## 项目背景
在Electron桌面应用开发中，遇到了两个关键技术挑战：
1. **权限配置问题**：应用无法访问摄像头和网络API
2. **UI视觉效果**：需要实现强烈的3D透视文字轮子效果

## 核心技术问题

### 1. Electron权限配置
**问题现象**：
- TypeError: Failed to fetch 错误
- 摄像头访问被拒绝
- HTTP请求被阻止

**根本原因**：
- Electron默认安全策略过于严格
- 缺少媒体设备权限处理
- 混合内容（HTTPS/HTTP）被阻止

### 2. 3D文字透视效果
**问题现象**：
- CSS渐变无法实现真正的每行大小变化
- 文字显示在固定容器内而非流动效果
- 透视效果不够强烈

**根本原因**：
- 使用CSS background-clip模拟而非真实DOM操作
- 缺少每行独立的样式控制
- 透视参数设置不当

## 解决方案

### 1. Electron权限配置完整方案

#### webPreferences配置
```javascript
webPreferences: {
  nodeIntegration: true,
  contextIsolation: false,
  allowRunningInsecureContent: true,  // 允许HTTP内容
  webSecurity: false,                 // 禁用web安全策略
  sandbox: false,                     // 禁用沙盒模式
  experimentalFeatures: true,         // 启用实验性功能
}
```

#### 权限处理器
```javascript
// 自动授予媒体权限
session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
  if (permission === 'media' || permission === 'camera' || permission === 'microphone') {
    callback(true)
  } else {
    callback(false)
  }
})

// 权限检查处理
session.defaultSession.setPermissionCheckHandler((webContents, permission, requestingOrigin) => {
  if (permission === 'media' || permission === 'camera' || permission === 'microphone') {
    return true
  }
  return false
})
```

#### 应用级别权限
```javascript
app.whenReady().then(() => {
  // 硬件加速和WebGL支持
  app.commandLine.appendSwitch('enable-features', 'VaapiVideoDecoder')
  app.commandLine.appendSwitch('disable-features', 'VizDisplayCompositor')
  app.commandLine.appendSwitch('enable-unsafe-webgpu')
  app.commandLine.appendSwitch('enable-webgl')
  app.commandLine.appendSwitch('enable-accelerated-2d-canvas')
})
```

### 2. 3D文字透视效果实现

#### 核心思路
- 将文本按行分割为独立DOM元素
- 每行根据距离中心位置计算透视参数
- 实时动态调整字体大小、透明度、宽度

#### 关键实现
```javascript
// 为每一行计算透视效果
textLines.forEach((line) => {
  const lineRect = line.getBoundingClientRect()
  const lineCenter = lineRect.top + lineRect.height / 2 - containerRect.top
  
  // 计算距离容器中心的距离 (0-1)
  const distanceFromCenter = Math.abs(lineCenter - containerCenter) / containerCenter
  const clampedDistance = Math.min(distanceFromCenter, 1)
  
  // 透视效果参数
  const fontSize = 18 - (clampedDistance * 10)      // 8px-18px
  const opacity = 1.0 - (clampedDistance * 0.9)     // 0.1-1.0
  const width = 100 - (clampedDistance * 40)        // 60%-100%
  const translateZ = -clampedDistance * 50          // Z轴深度
  const rotateX = clampedDistance * 15              // X轴旋转
  
  // 应用样式
  line.style.fontSize = `${fontSize}px`
  line.style.opacity = `${opacity}`
  line.style.width = `${width}%`
  line.style.transform = `translateZ(${translateZ}px) rotateX(${rotateX}deg)`
  line.style.color = `rgba(0, 255, 136, ${opacity})`
})
```

#### DOM结构优化
```jsx
// 从单一pre元素改为分行div结构
<div className="cylindrical-text-display">
  {text.split('\n').map((line, index) => (
    <div key={index} className="text-line">
      {line || '\u00A0'}
    </div>
  ))}
</div>
```

## 技术要点

### 1. Electron安全策略
- **webSecurity: false** - 开发环境必需，生产环境需谨慎
- **allowRunningInsecureContent** - 允许HTTPS页面加载HTTP资源
- **权限处理器** - 自动化权限授予，避免用户交互

### 2. 3D透视计算
- **距离计算** - 使用getBoundingClientRect()获取精确位置
- **参数映射** - 线性插值实现平滑过渡效果
- **性能优化** - 使用clamp限制计算范围

### 3. DOM操作优化
- **MutationObserver** - 监听DOM变化自动更新样式
- **防抖处理** - setTimeout延迟执行避免频繁计算
- **事件管理** - 正确清理事件监听器防止内存泄漏

## 最佳实践

### 1. 开发环境配置
```javascript
// 开发环境宽松配置
if (process.env.NODE_ENV === 'development') {
  webPreferences.webSecurity = false
  webPreferences.allowRunningInsecureContent = true
}
```

### 2. 权限处理模式
```javascript
// 统一权限处理函数
const setupPermissions = (session) => {
  const mediaPermissions = ['media', 'camera', 'microphone']
  
  session.setPermissionRequestHandler((webContents, permission, callback) => {
    callback(mediaPermissions.includes(permission))
  })
  
  session.setPermissionCheckHandler((webContents, permission) => {
    return mediaPermissions.includes(permission)
  })
}
```

### 3. 3D效果性能优化
```javascript
// 使用requestAnimationFrame优化动画
const updateTextLines = () => {
  requestAnimationFrame(() => {
    // 透视效果计算
    handleScroll()
  })
}
```

## 经验总结

### 成功要素
1. **系统性思考** - 同时解决权限和视觉效果问题
2. **渐进式开发** - 先解决基础功能再优化效果
3. **实时调试** - 通过Electron DevTools实时验证效果

### 避免的坑
1. **权限配置不全** - 仅设置webSecurity=false不够，需要完整权限链
2. **CSS局限性** - 复杂3D效果需要JavaScript动态计算
3. **性能问题** - 频繁DOM操作需要优化和防抖

### 可复用模式
1. **Electron权限配置模板** - 标准化的权限设置方案
2. **3D文字效果组件** - 可封装为独立React组件
3. **动态样式计算框架** - 基于位置的样式计算模式

## 技术栈
- **Electron** - 桌面应用框架
- **React + TypeScript** - 前端框架
- **CSS 3D Transforms** - 3D视觉效果
- **MutationObserver** - DOM变化监听
- **getBoundingClientRect** - 精确位置计算

## 适用场景
- 需要摄像头/麦克风权限的Electron应用
- 需要强烈视觉效果的桌面应用
- 混合内容（HTTP/HTTPS）的应用
- 实时数据展示的科技感界面
