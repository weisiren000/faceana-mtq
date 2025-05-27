import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/agent_status.dart';
import '../services/backend_service.dart';

class AgentNotifier extends StateNotifier<AsyncValue<AgentStatus>> {
  AgentNotifier(this._backendService) : super(AsyncValue.data(AgentStatus.initial()));

  final BackendService _backendService;

  Future<void> startMonitoring() async {
    try {
      // 监听智能体状态更新
      _backendService.agentStatusStream.listen(
        (status) {
          state = AsyncValue.data(status);
        },
        onError: (error, stackTrace) {
          state = AsyncValue.error(error, stackTrace);
        },
      );
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  void updateAgentStatus(AgentStatus status) {
    state = AsyncValue.data(status);
  }

  void updateDSAProgress(double progress, AgentState status) {
    state.whenData((currentStatus) {
      final updatedStatus = currentStatus.copyWith(
        dsaProgress: progress,
        dsaStatus: status,
        lastUpdate: DateTime.now(),
      );
      state = AsyncValue.data(updatedStatus);
    });
  }

  void updateVSAProgress(double progress, AgentState status) {
    state.whenData((currentStatus) {
      final updatedStatus = currentStatus.copyWith(
        vsaProgress: progress,
        vsaStatus: status,
        lastUpdate: DateTime.now(),
      );
      state = AsyncValue.data(updatedStatus);
    });
  }

  void updateJSAProgress(double progress, AgentState status) {
    state.whenData((currentStatus) {
      final updatedStatus = currentStatus.copyWith(
        jsaProgress: progress,
        jsaStatus: status,
        lastUpdate: DateTime.now(),
      );
      state = AsyncValue.data(updatedStatus);
    });
  }

  void resetStatus() {
    state = AsyncValue.data(AgentStatus.initial());
  }

  void simulateAnalysis() {
    // 模拟分析过程，用于测试
    _simulateDSAAnalysis();
    Future.delayed(const Duration(seconds: 1), () => _simulateVSAAnalysis());
    Future.delayed(const Duration(seconds: 2), () => _simulateJSAAnalysis());
  }

  void _simulateDSAAnalysis() {
    updateDSAProgress(0, AgentState.analyzing);
    
    // 模拟进度更新
    for (int i = 1; i <= 10; i++) {
      Future.delayed(Duration(milliseconds: i * 200), () {
        updateDSAProgress(i * 10.0, AgentState.analyzing);
        if (i == 10) {
          updateDSAProgress(100, AgentState.completed);
        }
      });
    }
  }

  void _simulateVSAAnalysis() {
    updateVSAProgress(0, AgentState.analyzing);
    
    // 模拟进度更新
    for (int i = 1; i <= 10; i++) {
      Future.delayed(Duration(milliseconds: i * 300), () {
        updateVSAProgress(i * 10.0, AgentState.analyzing);
        if (i == 10) {
          updateVSAProgress(100, AgentState.completed);
        }
      });
    }
  }

  void _simulateJSAAnalysis() {
    updateJSAProgress(0, AgentState.analyzing);
    
    // 模拟进度更新
    for (int i = 1; i <= 10; i++) {
      Future.delayed(Duration(milliseconds: i * 150), () {
        updateJSAProgress(i * 10.0, AgentState.analyzing);
        if (i == 10) {
          updateJSAProgress(100, AgentState.completed);
        }
      });
    }
  }
}

final agentProvider = StateNotifierProvider<AgentNotifier, AsyncValue<AgentStatus>>((ref) {
  final backendService = ref.watch(backendServiceProvider);
  return AgentNotifier(backendService);
});

// 总体进度Provider
final overallProgressProvider = Provider<double>((ref) {
  final agentStatusAsync = ref.watch(agentProvider);
  
  return agentStatusAsync.when(
    data: (status) => status.overallProgress,
    loading: () => 0.0,
    error: (_, __) => 0.0,
  );
});

// 分析状态Provider
final analysisStateProvider = Provider<String>((ref) {
  final agentStatusAsync = ref.watch(agentProvider);
  
  return agentStatusAsync.when(
    data: (status) {
      if (status.isCompleted) return '分析完成';
      if (status.isAnalyzing) return '分析中...';
      if (status.hasError) return '分析失败';
      return '等待开始';
    },
    loading: () => '初始化中...',
    error: (_, __) => '连接失败',
  );
});
