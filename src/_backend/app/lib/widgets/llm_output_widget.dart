import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/app_theme.dart';
import '../models/llm_message.dart';
import '../providers/llm_provider.dart';

class LlmOutputWidget extends ConsumerStatefulWidget {
  const LlmOutputWidget({super.key});

  @override
  ConsumerState<LlmOutputWidget> createState() => _LlmOutputWidgetState();
}

class _LlmOutputWidgetState extends ConsumerState<LlmOutputWidget> {
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final messages = ref.watch(llmProvider);
    
    return Container(
      decoration: AppTheme.cardDecoration,
      child: Column(
        children: [
          // 标题栏
          Container(
            padding: const EdgeInsets.all(20),
            decoration: const BoxDecoration(
              border: Border(
                bottom: BorderSide(color: AppTheme.borderColor, width: 1),
              ),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.psychology,
                  color: AppTheme.accentColor,
                  size: 24,
                ),
                const SizedBox(width: 12),
                Text(
                  'LLM 分析输出',
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppTheme.successColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppTheme.successColor, width: 1),
                  ),
                  child: const Text(
                    'ACTIVE',
                    style: TextStyle(
                      color: AppTheme.successColor,
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          // 消息列表
          Expanded(
            child: messages.when(
              data: (messageList) => _buildMessageList(messageList),
              loading: () => _buildLoadingIndicator(),
              error: (error, stack) => _buildErrorIndicator(error.toString()),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageList(List<LlmMessage> messages) {
    if (messages.isEmpty) {
      return _buildEmptyState();
    }

    // 自动滚动到底部
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });

    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: messages.length,
      itemBuilder: (context, index) {
        final message = messages[index];
        return _buildMessageItem(message);
      },
    );
  }

  Widget _buildMessageItem(LlmMessage message) {
    Color statusColor;
    IconData statusIcon;
    
    switch (message.type) {
      case MessageType.info:
        statusColor = AppTheme.accentColor;
        statusIcon = Icons.info_outline;
        break;
      case MessageType.success:
        statusColor = AppTheme.successColor;
        statusIcon = Icons.check_circle_outline;
        break;
      case MessageType.warning:
        statusColor = AppTheme.warningColor;
        statusIcon = Icons.warning_outlined;
        break;
      case MessageType.error:
        statusColor = AppTheme.errorColor;
        statusIcon = Icons.error_outline;
        break;
      case MessageType.analysis:
        statusColor = AppTheme.accentColor;
        statusIcon = Icons.analytics;
        break;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppTheme.secondaryColor.withOpacity(0.5),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: statusColor.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 消息头部
          Row(
            children: [
              Icon(
                statusIcon,
                color: statusColor,
                size: 16,
              ),
              const SizedBox(width: 8),
              Text(
                _getMessageTypeLabel(message.type),
                style: TextStyle(
                  color: statusColor,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const Spacer(),
              Text(
                _formatTimestamp(message.timestamp),
                style: const TextStyle(
                  color: AppTheme.textSecondary,
                  fontSize: 10,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 8),
          
          // 消息内容
          Text(
            message.content,
            style: const TextStyle(
              color: AppTheme.textPrimary,
              fontSize: 14,
              height: 1.4,
            ),
          ),
          
          // 置信度（如果有）
          if (message.confidence != null) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                const Text(
                  '置信度: ',
                  style: TextStyle(
                    color: AppTheme.textSecondary,
                    fontSize: 12,
                  ),
                ),
                Text(
                  '${(message.confidence! * 100).toStringAsFixed(1)}%',
                  style: TextStyle(
                    color: statusColor,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.chat_bubble_outline,
            color: AppTheme.textSecondary,
            size: 48,
          ),
          SizedBox(height: 16),
          Text(
            '等待分析结果...',
            style: TextStyle(
              color: AppTheme.textSecondary,
              fontSize: 16,
            ),
          ),
          SizedBox(height: 8),
          Text(
            '开始录制后，AI分析结果将在这里显示',
            style: TextStyle(
              color: AppTheme.textSecondary,
              fontSize: 12,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
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
            '正在连接LLM服务...',
            style: TextStyle(color: AppTheme.textSecondary),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorIndicator(String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.error_outline,
            color: AppTheme.errorColor,
            size: 48,
          ),
          const SizedBox(height: 16),
          const Text(
            'LLM连接失败',
            style: TextStyle(
              color: AppTheme.errorColor,
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            error,
            style: const TextStyle(
              color: AppTheme.textSecondary,
              fontSize: 12,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  String _getMessageTypeLabel(MessageType type) {
    switch (type) {
      case MessageType.info:
        return '信息';
      case MessageType.success:
        return '成功';
      case MessageType.warning:
        return '警告';
      case MessageType.error:
        return '错误';
      case MessageType.analysis:
        return '分析';
    }
  }

  String _formatTimestamp(DateTime timestamp) {
    return '${timestamp.hour.toString().padLeft(2, '0')}:'
           '${timestamp.minute.toString().padLeft(2, '0')}:'
           '${timestamp.second.toString().padLeft(2, '0')}';
  }
}
