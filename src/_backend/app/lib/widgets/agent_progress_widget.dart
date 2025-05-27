import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/app_theme.dart';
import '../models/agent_status.dart';
import '../providers/agent_provider.dart';

class AgentProgressWidget extends ConsumerWidget {
  const AgentProgressWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final agentStatus = ref.watch(agentProvider);

    return Container(
      decoration: AppTheme.cardDecoration,
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题
          Text(
            '智能体分析',
            style: Theme.of(context).textTheme.headlineMedium,
          ),

          const SizedBox(height: 16),

          // 智能体进度圈
          Expanded(
            child: agentStatus.when(
              data: (status) => _buildAgentCircles(status),
              loading: () => _buildLoadingIndicator(),
              error: (error, stack) => _buildErrorIndicator(),
            ),
          ),

          const SizedBox(height: 16),

          // 总体进度条
          _buildOverallProgress(agentStatus),
        ],
      ),
    );
  }

  Widget _buildAgentCircles(AgentStatus status) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildAgentCircle(
          'DSA',
          '数据分析',
          status.dsaProgress,
          status.dsaStatus,
          status.dsaImage,
        ),
        _buildAgentCircle(
          'VSA',
          '视觉分析',
          status.vsaProgress,
          status.vsaStatus,
          status.vsaImage,
        ),
        _buildAgentCircle(
          'JSA',
          '综合判定',
          status.jsaProgress,
          status.jsaStatus,
          status.jsaImage,
        ),
      ],
    );
  }

  Widget _buildAgentCircle(
    String agentName,
    String description,
    double progress,
    AgentState state,
    String? imagePath,
  ) {
    Color circleColor;
    Color glowColor;
    bool isAnimating = false;

    switch (state) {
      case AgentState.idle:
        circleColor = AppTheme.textSecondary;
        glowColor = AppTheme.textSecondary;
        break;
      case AgentState.analyzing:
        circleColor = AppTheme.accentColor;
        glowColor = AppTheme.accentColor;
        isAnimating = true;
        break;
      case AgentState.completed:
        circleColor = AppTheme.successColor;
        glowColor = AppTheme.successColor;
        break;
      case AgentState.error:
        circleColor = AppTheme.errorColor;
        glowColor = AppTheme.errorColor;
        break;
    }

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // 圆形进度指示器
        SizedBox(
          width: 80,
          height: 80,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // 背景圆圈
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppTheme.cardBackground,
                  border: Border.all(
                    color: AppTheme.borderColor,
                    width: 2,
                  ),
                ),
              ),

              // 进度圆圈
              SizedBox(
                width: 76,
                height: 76,
                child: CircularProgressIndicator(
                  value: progress / 100,
                  strokeWidth: 4,
                  backgroundColor: Colors.transparent,
                  valueColor: AlwaysStoppedAnimation<Color>(circleColor),
                ),
              ),

              // 发光效果（分析中时）
              if (isAnimating)
                AnimatedContainer(
                  duration: const Duration(milliseconds: 1000),
                  width: 84,
                  height: 84,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: glowColor.withOpacity(0.5),
                        blurRadius: 12,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                ),

              // 中心内容
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppTheme.cardBackground,
                  border: Border.all(
                    color: circleColor,
                    width: 1,
                  ),
                ),
                child: _buildAgentIcon(agentName, circleColor),
              ),
            ],
          ),
        ),

        const SizedBox(height: 8),

        // 智能体名称
        Text(
          agentName,
          style: TextStyle(
            color: circleColor,
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),

        // 描述
        Text(
          description,
          style: const TextStyle(
            color: AppTheme.textSecondary,
            fontSize: 10,
          ),
        ),

        // 进度百分比
        Text(
          '${progress.toInt()}%',
          style: TextStyle(
            color: circleColor,
            fontSize: 12,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildAgentIcon(String agentName, Color color) {
    IconData icon;
    switch (agentName) {
      case 'DSA':
        icon = Icons.analytics;
        break;
      case 'VSA':
        icon = Icons.visibility;
        break;
      case 'JSA':
        icon = Icons.psychology;
        break;
      default:
        icon = Icons.smart_toy;
    }

    return Icon(
      icon,
      color: color,
      size: 24,
    );
  }

  Widget _buildLoadingIndicator() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(color: AppTheme.accentColor),
          SizedBox(height: 16),
          Text(
            '初始化智能体...',
            style: TextStyle(color: AppTheme.textSecondary),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorIndicator() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, color: AppTheme.errorColor, size: 48),
          SizedBox(height: 16),
          Text(
            '智能体连接失败',
            style: TextStyle(color: AppTheme.errorColor),
          ),
        ],
      ),
    );
  }

  Widget _buildOverallProgress(AsyncValue<AgentStatus> agentStatus) {
    return agentStatus.when(
      data: (status) {
        final overallProgress = (status.dsaProgress + status.vsaProgress + status.jsaProgress) / 3;
        return Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  '总体进度',
                  style: TextStyle(
                    color: AppTheme.textSecondary,
                    fontSize: 12,
                  ),
                ),
                Text(
                  '${overallProgress.toInt()}%',
                  style: const TextStyle(
                    color: AppTheme.accentColor,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: overallProgress / 100,
              backgroundColor: AppTheme.borderColor,
              valueColor: const AlwaysStoppedAnimation<Color>(AppTheme.accentColor),
              minHeight: 4,
            ),
          ],
        );
      },
      loading: () => const SizedBox.shrink(),
      error: (error, stack) => const SizedBox.shrink(),
    );
  }
}
