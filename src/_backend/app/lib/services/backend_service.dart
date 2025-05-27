import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';
import '../models/emotion_data.dart';
import '../models/agent_status.dart';
import '../models/llm_message.dart';

class BackendService {
  static const String baseUrl = 'http://localhost:8000';
  static const String wsUrl = 'ws://localhost:8001';
  
  WebSocketChannel? _wsChannel;
  final StreamController<List<EmotionData>> _emotionController = StreamController.broadcast();
  final StreamController<AgentStatus> _agentStatusController = StreamController.broadcast();
  final StreamController<LlmMessage> _messageController = StreamController.broadcast();

  // 公开的流
  Stream<List<EmotionData>> get emotionStream => _emotionController.stream;
  Stream<AgentStatus> get agentStatusStream => _agentStatusController.stream;
  Stream<LlmMessage> get messageStream => _messageController.stream;

  BackendService() {
    _initializeWebSocket();
  }

  void _initializeWebSocket() {
    try {
      _wsChannel = WebSocketChannel.connect(Uri.parse(wsUrl));
      
      _wsChannel!.stream.listen(
        (data) {
          _handleWebSocketMessage(data);
        },
        onError: (error) {
          print('WebSocket错误: $error');
          _messageController.add(LlmMessage.error('WebSocket连接错误: $error'));
        },
        onDone: () {
          print('WebSocket连接关闭');
          _reconnectWebSocket();
        },
      );
      
      _messageController.add(LlmMessage.info('已连接到后端服务'));
    } catch (e) {
      print('WebSocket连接失败: $e');
      _messageController.add(LlmMessage.error('无法连接到后端服务: $e'));
    }
  }

  void _handleWebSocketMessage(dynamic data) {
    try {
      final Map<String, dynamic> message = jsonDecode(data);
      final String type = message['type'] ?? '';

      switch (type) {
        case 'emotion_update':
          final List<dynamic> emotionsJson = message['data'] ?? [];
          final emotions = emotionsJson
              .map((e) => EmotionData.fromJson(e as Map<String, dynamic>))
              .toList();
          _emotionController.add(emotions);
          break;

        case 'agent_status':
          final agentStatus = AgentStatus.fromJson(message['data']);
          _agentStatusController.add(agentStatus);
          break;

        case 'llm_message':
          final llmMessage = LlmMessage.fromJson(message['data']);
          _messageController.add(llmMessage);
          break;

        case 'system_message':
          final content = message['content'] ?? '';
          final messageType = message['message_type'] ?? 'info';
          final confidence = message['confidence']?.toDouble();
          
          LlmMessage systemMessage;
          switch (messageType) {
            case 'success':
              systemMessage = LlmMessage.success(content, confidence: confidence);
              break;
            case 'warning':
              systemMessage = LlmMessage.warning(content, confidence: confidence);
              break;
            case 'error':
              systemMessage = LlmMessage.error(content, confidence: confidence);
              break;
            case 'analysis':
              systemMessage = LlmMessage.analysis(content, confidence: confidence);
              break;
            default:
              systemMessage = LlmMessage.info(content, confidence: confidence);
          }
          _messageController.add(systemMessage);
          break;

        default:
          print('未知消息类型: $type');
      }
    } catch (e) {
      print('解析WebSocket消息失败: $e');
    }
  }

  void _reconnectWebSocket() {
    // 5秒后尝试重连
    Timer(const Duration(seconds: 5), () {
      _initializeWebSocket();
    });
  }

  // API调用方法
  Future<bool> startEmotionAnalysis() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/start_analysis'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        _messageController.add(LlmMessage.info('开始情绪分析...'));
        return true;
      } else {
        _messageController.add(LlmMessage.error('启动分析失败: ${response.statusCode}'));
        return false;
      }
    } catch (e) {
      _messageController.add(LlmMessage.error('网络请求失败: $e'));
      return false;
    }
  }

  Future<bool> stopEmotionAnalysis() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/stop_analysis'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        _messageController.add(LlmMessage.info('停止情绪分析'));
        return true;
      } else {
        _messageController.add(LlmMessage.error('停止分析失败: ${response.statusCode}'));
        return false;
      }
    } catch (e) {
      _messageController.add(LlmMessage.error('网络请求失败: $e'));
      return false;
    }
  }

  Future<Map<String, dynamic>?> getSystemStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/status'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        return null;
      }
    } catch (e) {
      print('获取系统状态失败: $e');
      return null;
    }
  }

  Future<bool> uploadImage(String imagePath) async {
    try {
      final file = File(imagePath);
      if (!await file.exists()) {
        _messageController.add(LlmMessage.error('图片文件不存在'));
        return false;
      }

      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/api/upload_image'),
      );

      request.files.add(await http.MultipartFile.fromPath('image', imagePath));

      final response = await request.send();

      if (response.statusCode == 200) {
        _messageController.add(LlmMessage.success('图片上传成功'));
        return true;
      } else {
        _messageController.add(LlmMessage.error('图片上传失败: ${response.statusCode}'));
        return false;
      }
    } catch (e) {
      _messageController.add(LlmMessage.error('图片上传失败: $e'));
      return false;
    }
  }

  void sendCommand(String command, [Map<String, dynamic>? params]) {
    if (_wsChannel != null) {
      final message = {
        'command': command,
        'params': params ?? {},
        'timestamp': DateTime.now().toIso8601String(),
      };
      _wsChannel!.sink.add(jsonEncode(message));
    }
  }

  void dispose() {
    _wsChannel?.sink.close();
    _emotionController.close();
    _agentStatusController.close();
    _messageController.close();
  }
}

final backendServiceProvider = Provider<BackendService>((ref) {
  final service = BackendService();
  
  // 当Provider被销毁时清理资源
  ref.onDispose(() {
    service.dispose();
  });
  
  return service;
});
