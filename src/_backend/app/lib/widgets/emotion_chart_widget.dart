import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import '../utils/app_theme.dart';
import '../models/emotion_data.dart';
import '../providers/emotion_provider.dart';

class EmotionChartWidget extends ConsumerWidget {
  const EmotionChartWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final emotionData = ref.watch(emotionProvider);
    
    return Container(
      decoration: AppTheme.cardDecoration,
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题
          Text(
            '情绪分析',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          
          const SizedBox(height: 16),
          
          // 柱状图
          Expanded(
            child: emotionData.when(
              data: (data) => _buildChart(data),
              loading: () => _buildLoadingChart(),
              error: (error, stack) => _buildErrorChart(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChart(List<EmotionData> data) {
    if (data.isEmpty) {
      return _buildEmptyChart();
    }

    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.spaceAround,
        maxY: 100,
        barTouchData: BarTouchData(
          enabled: true,
          touchTooltipData: BarTouchTooltipData(
            tooltipBgColor: AppTheme.cardBackground,
            tooltipBorder: BorderSide(color: AppTheme.borderColor),
            tooltipRoundedRadius: 8,
            getTooltipItem: (group, groupIndex, rod, rodIndex) {
              return BarTooltipItem(
                '${data[groupIndex].emotion}\n${rod.toY.toStringAsFixed(1)}%',
                const TextStyle(
                  color: AppTheme.textPrimary,
                  fontWeight: FontWeight.w600,
                ),
              );
            },
          ),
        ),
        titlesData: FlTitlesData(
          show: true,
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                if (value.toInt() < data.length) {
                  return Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      _getEmotionShortName(data[value.toInt()].emotion),
                      style: const TextStyle(
                        color: AppTheme.textSecondary,
                        fontSize: 12,
                      ),
                    ),
                  );
                }
                return const Text('');
              },
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 40,
              getTitlesWidget: (value, meta) {
                return Text(
                  '${value.toInt()}%',
                  style: const TextStyle(
                    color: AppTheme.textSecondary,
                    fontSize: 10,
                  ),
                );
              },
            ),
          ),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
        barGroups: data.asMap().entries.map((entry) {
          final index = entry.key;
          final emotion = entry.value;
          
          return BarChartGroupData(
            x: index,
            barRods: [
              BarChartRodData(
                toY: emotion.intensity,
                color: _getEmotionColor(emotion.emotion),
                width: 20,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(4),
                  topRight: Radius.circular(4),
                ),
                gradient: LinearGradient(
                  begin: Alignment.bottomCenter,
                  end: Alignment.topCenter,
                  colors: [
                    _getEmotionColor(emotion.emotion).withOpacity(0.7),
                    _getEmotionColor(emotion.emotion),
                  ],
                ),
              ),
            ],
          );
        }).toList(),
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: 20,
          getDrawingHorizontalLine: (value) {
            return FlLine(
              color: AppTheme.borderColor.withOpacity(0.3),
              strokeWidth: 1,
            );
          },
        ),
      ),
    );
  }

  Widget _buildLoadingChart() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(color: AppTheme.accentColor),
          SizedBox(height: 16),
          Text(
            '正在分析情绪...',
            style: TextStyle(color: AppTheme.textSecondary),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorChart() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, color: AppTheme.errorColor, size: 48),
          SizedBox(height: 16),
          Text(
            '分析失败',
            style: TextStyle(color: AppTheme.errorColor),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyChart() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.bar_chart, color: AppTheme.textSecondary, size: 48),
          SizedBox(height: 16),
          Text(
            '等待分析数据...',
            style: TextStyle(color: AppTheme.textSecondary),
          ),
        ],
      ),
    );
  }

  String _getEmotionShortName(String emotion) {
    switch (emotion.toLowerCase()) {
      case 'happy':
      case 'happiness':
        return '高兴';
      case 'sad':
      case 'sadness':
        return '悲伤';
      case 'angry':
      case 'anger':
        return '愤怒';
      case 'fear':
      case 'fearful':
        return '恐惧';
      case 'surprise':
      case 'surprised':
        return '惊讶';
      case 'disgust':
      case 'disgusted':
        return '厌恶';
      case 'neutral':
        return '平静';
      default:
        return emotion.substring(0, 2);
    }
  }

  Color _getEmotionColor(String emotion) {
    switch (emotion.toLowerCase()) {
      case 'happy':
      case 'happiness':
        return const Color(0xFF00FF88);
      case 'sad':
      case 'sadness':
        return const Color(0xFF4A90E2);
      case 'angry':
      case 'anger':
        return const Color(0xFFFF4757);
      case 'fear':
      case 'fearful':
        return const Color(0xFF9B59B6);
      case 'surprise':
      case 'surprised':
        return const Color(0xFFFFB800);
      case 'disgust':
      case 'disgusted':
        return const Color(0xFF2ECC71);
      case 'neutral':
        return const Color(0xFF95A5A6);
      default:
        return AppTheme.accentColor;
    }
  }
}
