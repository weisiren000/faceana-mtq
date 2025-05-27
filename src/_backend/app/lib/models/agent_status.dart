enum AgentState {
  idle,
  analyzing,
  completed,
  error,
}

class AgentStatus {
  final double dsaProgress;
  final AgentState dsaStatus;
  final String? dsaImage;
  
  final double vsaProgress;
  final AgentState vsaStatus;
  final String? vsaImage;
  
  final double jsaProgress;
  final AgentState jsaStatus;
  final String? jsaImage;
  
  final DateTime lastUpdate;

  AgentStatus({
    required this.dsaProgress,
    required this.dsaStatus,
    this.dsaImage,
    required this.vsaProgress,
    required this.vsaStatus,
    this.vsaImage,
    required this.jsaProgress,
    required this.jsaStatus,
    this.jsaImage,
    required this.lastUpdate,
  });

  factory AgentStatus.initial() {
    return AgentStatus(
      dsaProgress: 0.0,
      dsaStatus: AgentState.idle,
      vsaProgress: 0.0,
      vsaStatus: AgentState.idle,
      jsaProgress: 0.0,
      jsaStatus: AgentState.idle,
      lastUpdate: DateTime.now(),
    );
  }

  factory AgentStatus.fromJson(Map<String, dynamic> json) {
    return AgentStatus(
      dsaProgress: (json['dsa_progress'] as num).toDouble(),
      dsaStatus: AgentState.values.firstWhere(
        (e) => e.name == json['dsa_status'],
        orElse: () => AgentState.idle,
      ),
      dsaImage: json['dsa_image'] as String?,
      vsaProgress: (json['vsa_progress'] as num).toDouble(),
      vsaStatus: AgentState.values.firstWhere(
        (e) => e.name == json['vsa_status'],
        orElse: () => AgentState.idle,
      ),
      vsaImage: json['vsa_image'] as String?,
      jsaProgress: (json['jsa_progress'] as num).toDouble(),
      jsaStatus: AgentState.values.firstWhere(
        (e) => e.name == json['jsa_status'],
        orElse: () => AgentState.idle,
      ),
      jsaImage: json['jsa_image'] as String?,
      lastUpdate: DateTime.parse(json['last_update'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'dsa_progress': dsaProgress,
      'dsa_status': dsaStatus.name,
      'dsa_image': dsaImage,
      'vsa_progress': vsaProgress,
      'vsa_status': vsaStatus.name,
      'vsa_image': vsaImage,
      'jsa_progress': jsaProgress,
      'jsa_status': jsaStatus.name,
      'jsa_image': jsaImage,
      'last_update': lastUpdate.toIso8601String(),
    };
  }

  AgentStatus copyWith({
    double? dsaProgress,
    AgentState? dsaStatus,
    String? dsaImage,
    double? vsaProgress,
    AgentState? vsaStatus,
    String? vsaImage,
    double? jsaProgress,
    AgentState? jsaStatus,
    String? jsaImage,
    DateTime? lastUpdate,
  }) {
    return AgentStatus(
      dsaProgress: dsaProgress ?? this.dsaProgress,
      dsaStatus: dsaStatus ?? this.dsaStatus,
      dsaImage: dsaImage ?? this.dsaImage,
      vsaProgress: vsaProgress ?? this.vsaProgress,
      vsaStatus: vsaStatus ?? this.vsaStatus,
      vsaImage: vsaImage ?? this.vsaImage,
      jsaProgress: jsaProgress ?? this.jsaProgress,
      jsaStatus: jsaStatus ?? this.jsaStatus,
      jsaImage: jsaImage ?? this.jsaImage,
      lastUpdate: lastUpdate ?? this.lastUpdate,
    );
  }

  double get overallProgress => (dsaProgress + vsaProgress + jsaProgress) / 3;

  bool get isAnalyzing => 
      dsaStatus == AgentState.analyzing ||
      vsaStatus == AgentState.analyzing ||
      jsaStatus == AgentState.analyzing;

  bool get isCompleted =>
      dsaStatus == AgentState.completed &&
      vsaStatus == AgentState.completed &&
      jsaStatus == AgentState.completed;

  bool get hasError =>
      dsaStatus == AgentState.error ||
      vsaStatus == AgentState.error ||
      jsaStatus == AgentState.error;
}
