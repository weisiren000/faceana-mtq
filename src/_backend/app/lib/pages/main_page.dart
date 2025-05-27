import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../widgets/top_navigation.dart';
import '../widgets/camera_preview_widget.dart';
import '../widgets/emotion_chart_widget.dart';
import '../widgets/agent_progress_widget.dart';
import '../widgets/llm_output_widget.dart';
import '../utils/app_theme.dart';

class MainPage extends ConsumerStatefulWidget {
  const MainPage({super.key});

  @override
  ConsumerState<MainPage> createState() => _MainPageState();
}

class _MainPageState extends ConsumerState<MainPage> {
  @override
  void initState() {
    super.initState();
    // 初始化后端连接
    WidgetsBinding.instance.addPostFrameCallback((_) {
      // 这里可以初始化与Python后端的连接
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.primaryGradient,
        ),
        child: Column(
          children: [
            // 顶部导航栏
            const TopNavigation(),
            
            // 主内容区域
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Row(
                  children: [
                    // 左侧：摄像头区域
                    Expanded(
                      flex: 2,
                      child: Column(
                        children: [
                          // 摄像头预览
                          const Expanded(
                            flex: 4,
                            child: CameraPreviewWidget(),
                          ),
                          
                          const SizedBox(height: 16),
                          
                          // 开始按钮
                          SizedBox(
                            width: double.infinity,
                            height: 60,
                            child: ElevatedButton(
                              onPressed: () {
                                // 触发摄像事件
                                _startRecording();
                              },
                              style: ElevatedButton.styleFrom(
                                backgroundColor: AppTheme.successColor,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(30),
                                ),
                              ),
                              child: const Text(
                                'START',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    const SizedBox(width: 20),
                    
                    // 中间：情绪分析和智能体进度
                    Expanded(
                      flex: 2,
                      child: Column(
                        children: [
                          // 情绪柱状图
                          const Expanded(
                            flex: 3,
                            child: EmotionChartWidget(),
                          ),
                          
                          const SizedBox(height: 16),
                          
                          // 智能体进度
                          const Expanded(
                            flex: 2,
                            child: AgentProgressWidget(),
                          ),
                        ],
                      ),
                    ),
                    
                    const SizedBox(width: 20),
                    
                    // 右侧：LLM输出
                    const Expanded(
                      flex: 2,
                      child: LlmOutputWidget(),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _startRecording() {
    // 实现录制逻辑
    print('开始录制...');
    // 这里会调用后端API开始情绪分析流程
  }
}
