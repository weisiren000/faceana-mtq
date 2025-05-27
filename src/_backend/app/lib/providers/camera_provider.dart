import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:camera/camera.dart';

class CameraNotifier extends StateNotifier<AsyncValue<CameraController?>> {
  CameraNotifier() : super(const AsyncValue.loading()) {
    _initializeCamera();
  }

  CameraController? _controller;
  List<CameraDescription>? _cameras;

  Future<void> _initializeCamera() async {
    try {
      // 获取可用摄像头
      _cameras = await availableCameras();
      
      if (_cameras == null || _cameras!.isEmpty) {
        state = AsyncValue.error('没有找到可用的摄像头', StackTrace.current);
        return;
      }

      // 选择前置摄像头（如果有的话）
      CameraDescription camera = _cameras!.first;
      for (final cam in _cameras!) {
        if (cam.lensDirection == CameraLensDirection.front) {
          camera = cam;
          break;
        }
      }

      // 初始化摄像头控制器
      _controller = CameraController(
        camera,
        ResolutionPreset.high,
        enableAudio: false,
      );

      await _controller!.initialize();
      state = AsyncValue.data(_controller);
    } catch (e, stackTrace) {
      state = AsyncValue.error('摄像头初始化失败: $e', stackTrace);
    }
  }

  Future<void> switchCamera() async {
    if (_cameras == null || _cameras!.length < 2) return;

    try {
      state = const AsyncValue.loading();
      
      // 释放当前控制器
      await _controller?.dispose();

      // 找到下一个摄像头
      final currentIndex = _cameras!.indexOf(_controller!.description);
      final nextIndex = (currentIndex + 1) % _cameras!.length;
      final nextCamera = _cameras![nextIndex];

      // 初始化新的控制器
      _controller = CameraController(
        nextCamera,
        ResolutionPreset.high,
        enableAudio: false,
      );

      await _controller!.initialize();
      state = AsyncValue.data(_controller);
    } catch (e, stackTrace) {
      state = AsyncValue.error('切换摄像头失败: $e', stackTrace);
    }
  }

  Future<String?> takePicture() async {
    if (_controller == null || !_controller!.value.isInitialized) {
      return null;
    }

    try {
      final XFile image = await _controller!.takePicture();
      return image.path;
    } catch (e) {
      print('拍照失败: $e');
      return null;
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }
}

final cameraProvider = StateNotifierProvider<CameraNotifier, AsyncValue<CameraController?>>((ref) {
  return CameraNotifier();
});

// 录制状态Provider
final recordingStateProvider = StateProvider<bool>((ref) => false);

// 录制进度Provider
final recordingProgressProvider = StateProvider<double>((ref) => 0.0);
