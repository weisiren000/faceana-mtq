import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/llm_message.dart';
import '../services/backend_service.dart';

class LlmNotifier extends StateNotifier<AsyncValue<List<LlmMessage>>> {
  LlmNotifier(this._backendService) : super(const AsyncValue.data([])) {
    _initializeMessages();
  }

  final BackendService _backendService;
  static const int maxMessages = 100; // 最大消息数量

  void _initializeMessages() {
    // 添加初始欢迎消息
    final welcomeMessage = LlmMessage.info(
      '欢迎使用 EmoScan 情绪分析系统！\n点击 START 按钮开始分析。',
    );
    state = AsyncValue.data([welcomeMessage]);

    // 监听后端消息流
    _backendService.messageStream.listen(
      (message) {
        addMessage(message);
      },
      onError: (error, stackTrace) {
        final errorMessage = LlmMessage.error('连接错误: $error');
        addMessage(errorMessage);
      },
    );
  }

  void addMessage(LlmMessage message) {
    state.whenData((messages) {
      final updatedMessages = [...messages, message];
      
      // 限制消息数量，移除最旧的消息
      if (updatedMessages.length > maxMessages) {
        updatedMessages.removeRange(0, updatedMessages.length - maxMessages);
      }
      
      state = AsyncValue.data(updatedMessages);
    });
  }

  void addInfoMessage(String content, {double? confidence}) {
    final message = LlmMessage.info(content, confidence: confidence);
    addMessage(message);
  }

  void addSuccessMessage(String content, {double? confidence}) {
    final message = LlmMessage.success(content, confidence: confidence);
    addMessage(message);
  }

  void addWarningMessage(String content, {double? confidence}) {
    final message = LlmMessage.warning(content, confidence: confidence);
    addMessage(message);
  }

  void addErrorMessage(String content, {double? confidence}) {
    final message = LlmMessage.error(content, confidence: confidence);
    addMessage(message);
  }

  void addAnalysisMessage(String content, {double? confidence}) {
    final message = LlmMessage.analysis(content, confidence: confidence);
    addMessage(message);
  }

  void clearMessages() {
    state = const AsyncValue.data([]);
    _initializeMessages();
  }

  void simulateAnalysisFlow() {
    // 模拟分析流程，用于测试
    addInfoMessage('开始情绪分析流程...');
    
    Future.delayed(const Duration(seconds: 1), () {
      addInfoMessage('正在捕获图像...');
    });
    
    Future.delayed(const Duration(seconds: 2), () {
      addSuccessMessage('图像捕获完成，共5张图片');
    });
    
    Future.delayed(const Duration(seconds: 3), () {
      addInfoMessage('DSA智能体开始分析结构化数据...');
    });
    
    Future.delayed(const Duration(seconds: 5), () {
      addAnalysisMessage(
        'DSA分析结果：检测到主导情绪为"高兴"，置信度85.2%',
        confidence: 0.852,
      );
    });
    
    Future.delayed(const Duration(seconds: 6), () {
      addInfoMessage('VSA智能体开始视觉分析...');
    });
    
    Future.delayed(const Duration(seconds: 8), () {
      addAnalysisMessage(
        'VSA分析结果：多模型融合显示积极情绪，平均置信度78.9%',
        confidence: 0.789,
      );
    });
    
    Future.delayed(const Duration(seconds: 9), () {
      addInfoMessage('JSA智能体进行综合判定...');
    });
    
    Future.delayed(const Duration(seconds: 11), () {
      addSuccessMessage(
        '最终分析结果：用户当前情绪状态为积极乐观，建议继续保持良好心态。综合置信度：82.1%',
        confidence: 0.821,
      );
    });
  }
}

final llmProvider = StateNotifierProvider<LlmNotifier, AsyncValue<List<LlmMessage>>>((ref) {
  final backendService = ref.watch(backendServiceProvider);
  return LlmNotifier(backendService);
});

// 最新消息Provider
final latestMessageProvider = Provider<LlmMessage?>((ref) {
  final messagesAsync = ref.watch(llmProvider);
  
  return messagesAsync.when(
    data: (messages) => messages.isNotEmpty ? messages.last : null,
    loading: () => null,
    error: (_, __) => null,
  );
});

// 消息统计Provider
final messageStatsProvider = Provider<Map<String, int>>((ref) {
  final messagesAsync = ref.watch(llmProvider);
  
  return messagesAsync.when(
    data: (messages) {
      final stats = <String, int>{};
      for (final message in messages) {
        final type = message.type.name;
        stats[type] = (stats[type] ?? 0) + 1;
      }
      return stats;
    },
    loading: () => {},
    error: (_, __) => {},
  );
});
