class EmotionData {
  final String emotion;
  final double intensity;
  final double confidence;
  final DateTime timestamp;

  EmotionData({
    required this.emotion,
    required this.intensity,
    required this.confidence,
    required this.timestamp,
  });

  factory EmotionData.fromJson(Map<String, dynamic> json) {
    return EmotionData(
      emotion: json['emotion'] as String,
      intensity: (json['intensity'] as num).toDouble(),
      confidence: (json['confidence'] as num).toDouble(),
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'emotion': emotion,
      'intensity': intensity,
      'confidence': confidence,
      'timestamp': timestamp.toIso8601String(),
    };
  }

  @override
  String toString() {
    return 'EmotionData(emotion: $emotion, intensity: $intensity, confidence: $confidence)';
  }
}

class EmotionAnalysisResult {
  final List<EmotionData> emotions;
  final String dominantEmotion;
  final double overallConfidence;
  final String summary;
  final DateTime timestamp;

  EmotionAnalysisResult({
    required this.emotions,
    required this.dominantEmotion,
    required this.overallConfidence,
    required this.summary,
    required this.timestamp,
  });

  factory EmotionAnalysisResult.fromJson(Map<String, dynamic> json) {
    return EmotionAnalysisResult(
      emotions: (json['emotions'] as List)
          .map((e) => EmotionData.fromJson(e as Map<String, dynamic>))
          .toList(),
      dominantEmotion: json['dominant_emotion'] as String,
      overallConfidence: (json['overall_confidence'] as num).toDouble(),
      summary: json['summary'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'emotions': emotions.map((e) => e.toJson()).toList(),
      'dominant_emotion': dominantEmotion,
      'overall_confidence': overallConfidence,
      'summary': summary,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}
