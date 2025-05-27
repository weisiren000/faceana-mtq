# EmoScan Flutter Desktop Application

一个基于Flutter的专业情绪分析桌面应用，集成多智能体AI协作系统。

## 功能特性

### 🎯 核心功能
- **实时摄像头预览**: 支持多摄像头切换和实时人脸检测
- **情绪分析可视化**: 动态柱状图展示情绪强度分布
- **多智能体协作**: DSA、VSA、JSA三智能体并行分析
- **LLM输出展示**: 实时显示AI分析结果和系统状态
- **响应式设计**: 自适应屏幕尺寸，优雅的深色主题

### 🤖 智能体系统
- **DSA (Data Sentiment Analysis)**: 结构化数据分析智能体
- **VSA (Visual Sentiment Analysis)**: 视觉分析智能体  
- **JSA (Joint Sentiment Analysis)**: 综合判定智能体

### 🎨 UI设计特色
- 基于Figma设计稿的1:1还原
- 深色科技主题，渐变背景
- 圆形进度指示器和发光效果
- 实时数据更新和动画效果

## 技术栈

### 前端框架
- **Flutter**: 跨平台UI框架
- **Riverpod**: 状态管理
- **fl_chart**: 图表可视化
- **camera**: 摄像头控制

### 后端通信
- **HTTP**: RESTful API调用
- **WebSocket**: 实时数据推送
- **JSON**: 数据序列化

### 开发工具
- **window_manager**: 桌面窗口管理
- **google_fonts**: 字体管理
- **lottie**: 动画效果

## 项目结构

```
lib/
├── main.dart                 # 应用入口
├── pages/                    # 页面
│   └── main_page.dart       # 主页面
├── widgets/                  # UI组件
│   ├── top_navigation.dart  # 顶部导航
│   ├── camera_preview_widget.dart    # 摄像头预览
│   ├── emotion_chart_widget.dart     # 情绪图表
│   ├── agent_progress_widget.dart    # 智能体进度
│   └── llm_output_widget.dart        # LLM输出
├── models/                   # 数据模型
│   ├── emotion_data.dart    # 情绪数据
│   ├── agent_status.dart    # 智能体状态
│   └── llm_message.dart     # LLM消息
├── providers/                # 状态管理
│   ├── camera_provider.dart # 摄像头状态
│   ├── emotion_provider.dart # 情绪数据
│   ├── agent_provider.dart  # 智能体状态
│   └── llm_provider.dart    # LLM消息
├── services/                 # 服务层
│   └── backend_service.dart # 后端通信
└── utils/                    # 工具类
    └── app_theme.dart       # 主题配置
```

## 快速开始

### 环境要求
- Flutter SDK >= 3.10.0
- Dart SDK >= 3.0.0
- 支持桌面开发的IDE (VS Code / Android Studio)

### 安装依赖
```bash
flutter pub get
```

### 运行应用
```bash
# 开发模式
flutter run -d windows  # Windows
flutter run -d macos    # macOS
flutter run -d linux    # Linux

# 发布模式
flutter run --release -d windows
```

### 构建应用
```bash
# Windows
flutter build windows

# macOS
flutter build macos

# Linux
flutter build linux
```

## 配置说明

### 后端服务配置
在 `lib/services/backend_service.dart` 中配置后端服务地址：

```dart
static const String baseUrl = 'http://localhost:8000';  # HTTP API
static const String wsUrl = 'ws://localhost:8001';      # WebSocket
```

### 摄像头权限
确保应用具有摄像头访问权限：

**Windows**: 在系统设置中允许应用访问摄像头
**macOS**: 在 `macos/Runner/Info.plist` 中添加摄像头权限
**Linux**: 确保用户在 `video` 组中

## API接口

### HTTP接口
- `POST /api/start_analysis` - 开始情绪分析
- `POST /api/stop_analysis` - 停止情绪分析  
- `GET /api/status` - 获取系统状态
- `POST /api/upload_image` - 上传图片

### WebSocket消息
- `emotion_update` - 情绪数据更新
- `agent_status` - 智能体状态更新
- `llm_message` - LLM消息推送
- `system_message` - 系统消息

## 开发指南

### 添加新功能
1. 在 `models/` 中定义数据模型
2. 在 `providers/` 中创建状态管理
3. 在 `widgets/` 中实现UI组件
4. 在 `services/` 中添加后端通信

### 自定义主题
在 `utils/app_theme.dart` 中修改颜色和样式：

```dart
static const Color primaryColor = Color(0xFF1E1E2E);
static const Color accentColor = Color(0xFF00D4FF);
```

### 调试技巧
- 使用 `flutter inspector` 查看UI结构
- 使用 `print()` 输出调试信息
- 使用 `flutter logs` 查看运行日志

## 部署说明

### 桌面应用打包
```bash
# 生成可执行文件
flutter build windows --release
flutter build macos --release  
flutter build linux --release
```

### 依赖库处理
确保目标系统安装了必要的运行时库：
- Windows: Visual C++ Redistributable
- Linux: 相关的系统库

## 故障排除

### 常见问题
1. **摄像头无法访问**: 检查权限设置
2. **后端连接失败**: 确认后端服务运行状态
3. **WebSocket断开**: 检查网络连接和防火墙设置
4. **构建失败**: 清理缓存 `flutter clean && flutter pub get`

### 性能优化
- 使用 `const` 构造函数减少重建
- 合理使用 `Provider` 避免不必要的更新
- 优化图片和动画资源

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目地址: [GitHub Repository]
- 问题反馈: [Issues]
- 技术支持: [Email]

---

**EmoScan** - 让情绪分析更智能、更直观！
