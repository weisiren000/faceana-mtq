enum MessageType {
  info,
  success,
  warning,
  error,
  analysis,
}

class LlmMessage {
  final String id;
  final String content;
  final MessageType type;
  final DateTime timestamp;
  final double? confidence;
  final Map<String, dynamic>? metadata;

  LlmMessage({
    required this.id,
    required this.content,
    required this.type,
    required this.timestamp,
    this.confidence,
    this.metadata,
  });

  factory LlmMessage.info(String content, {double? confidence}) {
    return LlmMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      type: MessageType.info,
      timestamp: DateTime.now(),
      confidence: confidence,
    );
  }

  factory LlmMessage.success(String content, {double? confidence}) {
    return LlmMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      type: MessageType.success,
      timestamp: DateTime.now(),
      confidence: confidence,
    );
  }

  factory LlmMessage.warning(String content, {double? confidence}) {
    return LlmMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      type: MessageType.warning,
      timestamp: DateTime.now(),
      confidence: confidence,
    );
  }

  factory LlmMessage.error(String content, {double? confidence}) {
    return LlmMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      type: MessageType.error,
      timestamp: DateTime.now(),
      confidence: confidence,
    );
  }

  factory LlmMessage.analysis(String content, {double? confidence}) {
    return LlmMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      type: MessageType.analysis,
      timestamp: DateTime.now(),
      confidence: confidence,
    );
  }

  factory LlmMessage.fromJson(Map<String, dynamic> json) {
    return LlmMessage(
      id: json['id'] as String,
      content: json['content'] as String,
      type: MessageType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => MessageType.info,
      ),
      timestamp: DateTime.parse(json['timestamp'] as String),
      confidence: json['confidence'] != null 
          ? (json['confidence'] as num).toDouble() 
          : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'type': type.name,
      'timestamp': timestamp.toIso8601String(),
      'confidence': confidence,
      'metadata': metadata,
    };
  }

  @override
  String toString() {
    return 'LlmMessage(id: $id, type: $type, content: ${content.substring(0, content.length > 50 ? 50 : content.length)}...)';
  }
}
