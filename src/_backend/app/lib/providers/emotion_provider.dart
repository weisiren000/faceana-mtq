import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/emotion_data.dart';
import '../services/backend_service.dart';

class EmotionNotifier extends StateNotifier<AsyncValue<List<EmotionData>>> {
  EmotionNotifier(this._backendService) : super(const AsyncValue.data([]));

  final BackendService _backendService;

  Future<void> startAnalysis() async {
    state = const AsyncValue.loading();
    
    try {
      // 这里会调用后端服务开始情绪分析
      await _backendService.startEmotionAnalysis();
      
      // 监听分析结果
      _backendService.emotionStream.listen(
        (emotions) {
          state = AsyncValue.data(emotions);
        },
        onError: (error, stackTrace) {
          state = AsyncValue.error(error, stackTrace);
        },
      );
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  void updateEmotions(List<EmotionData> emotions) {
    state = AsyncValue.data(emotions);
  }

  void clearEmotions() {
    state = const AsyncValue.data([]);
  }

  void addEmotion(EmotionData emotion) {
    state.whenData((emotions) {
      final updatedEmotions = [...emotions, emotion];
      state = AsyncValue.data(updatedEmotions);
    });
  }
}

final emotionProvider = StateNotifierProvider<EmotionNotifier, AsyncValue<List<EmotionData>>>((ref) {
  final backendService = ref.watch(backendServiceProvider);
  return EmotionNotifier(backendService);
});

// 主导情绪Provider
final dominantEmotionProvider = Provider<String?>((ref) {
  final emotionsAsync = ref.watch(emotionProvider);
  
  return emotionsAsync.when(
    data: (emotions) {
      if (emotions.isEmpty) return null;
      
      // 找到强度最高的情绪
      emotions.sort((a, b) => b.intensity.compareTo(a.intensity));
      return emotions.first.emotion;
    },
    loading: () => null,
    error: (_, __) => null,
  );
});

// 整体置信度Provider
final overallConfidenceProvider = Provider<double>((ref) {
  final emotionsAsync = ref.watch(emotionProvider);
  
  return emotionsAsync.when(
    data: (emotions) {
      if (emotions.isEmpty) return 0.0;
      
      // 计算平均置信度
      final totalConfidence = emotions.fold<double>(
        0.0, 
        (sum, emotion) => sum + emotion.confidence,
      );
      return totalConfidence / emotions.length;
    },
    loading: () => 0.0,
    error: (_, __) => 0.0,
  );
});
