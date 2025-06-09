好的，直接通过外部程序调用 ComfyUI 的 API JSON 文件（如 "test.json"）来生成图片是完全可行的。这使你能够将 ComfyUI 的强大功能集成到自己的应用程序或自动化流程中，而无需手动操作 ComfyUI 界面。

核心思路是：你的外部程序将作为客户端，与正在运行的 ComfyUI 服务器进行 HTTP 通信。你将加载 "test.json"，根据需要修改其中的参数（如提示词、种子、LoRA 设置等），然后将修改后的 JSON 发送给 ComfyUI 的 `/prompt` API 端点来执行工作流。

以下是完整的方案指导：

---

## 准备工作

1.  **安装 Python 及所需库**:
    * 确保你安装了 Python (建议 3.8+)。
    * 安装必要的 Python 库：
        ```bash
        pip install requests websocket-client Pillow
        ```
        * `requests`: 用于发送 HTTP 请求。
        * `websocket-client`: 用于通过 WebSocket 接收实时反馈和结果。
        * `Pillow`: (可选，但推荐) 用于处理图片或进行上传前的校验。

2.  **运行 ComfyUI**:
    * 启动你的 ComfyUI。通常它会运行在 `http://127.0.0.1:8188`。确保 API 服务是可访问的。

3.  **导出 API JSON 工作流**:
    * 在 ComfyUI 界面中搭建好你的工作流。
    * 点击 "Save (API format)" 按钮，将工作流保存为 JSON 文件，例如命名为 "test.json"。这个文件就是我们将要操作的基础。

---

## 关键：识别和修改工作流中的节点

你的 "test.json" 文件描述了工作流中所有的节点、它们的设置以及它们之间的连接。当你想要动态改变某些参数（比如提示词、种子、LoRA）时，你需要在 Python 脚本中加载这个 JSON，找到对应的节点和输入字段，然后修改它们的值。

**如何找到正确的节点和输入？**

* **Node ID**: JSON 中的每个节点都有一个数字 ID (例如 `"3"`, `"5"`, `"10"`)。这些 ID 在你每次修改工作流并重新导出 API JSON 时可能会改变，所以直接硬编码 ID 不够灵活。
* **`class_type`**: 每个节点有一个 `class_type`，例如 `CLIPTextEncode` (用于文本编码), `KSampler` (采样器), `LoraLoader` (LoRA加载器), `LoadImage` (加载图片)。你可以通过类型来查找节点。
* **`_meta.title` (推荐)**: 为了更稳定地找到节点，**强烈建议**在 ComfyUI 中为你想要动态控制的关键节点设置一个**唯一的标题 (Title)**。例如，将正面提示词节点命名为 "PositivePromptNode"，LoRA 加载器节点命名为 "MyLoraLoader"。然后在你的代码中，通过这个标题来定位节点。

**示例：你需要修改的常见节点及其输入**
* **提示词 (CLIPTextEncode)**:
    * `class_type`: `"CLIPTextEncode"`
    * 输入字段: `"text"`
* **采样器 (KSampler)**:
    * `class_type`: `"KSampler"`
    * 输入字段: `"seed"`, `"steps"`, `"cfg"`, `"sampler_name"`, `"scheduler"`, `"denoise"`
* **LoRA 加载器 (LoraLoader)**:
    * `class_type`: `"LoraLoader"` (或其他类似名称，如 `LoraLoaderModelOnly`)
    * 输入字段: `"lora_name"`, `"strength_model"`, `"strength_clip"`
* **图像加载器 (LoadImage)**: (用于 img2img 或 ControlNet 等)
    * `class_type`: `"LoadImage"`
    * 输入字段: `"image"` (文件名，需要先上传图片到 ComfyUI 服务器)

---

## Python 脚本实现方案

下面是一个 Python 脚本的框架，演示了如何加载、修改、提交工作流，并通过 WebSocket 接收结果。

```python
import websocket # pip install websocket-client
import uuid
import json
import urllib.request
import urllib.parse
import random
import os
import requests # For easier file uploads

# --- 配置 ---
COMFYUI_SERVER_ADDRESS = "127.0.0.1:8188" # ComfyUI 服务器地址和端口
CLIENT_ID = str(uuid.uuid4())             # 生成一个唯一的客户端ID
OUTPUT_DIRECTORY = "output_images"        # 图片保存目录

# --- 辅助函数 ---

def load_workflow_api_json(filepath: str) -> dict | None:
    """加载导出的 API JSON 工作流文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误：找不到工作流文件 {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"错误：无法解析 JSON 文件 {filepath}")
        return None

def find_node_by_title(workflow_data: dict, target_title: str) -> str | None:
    """通过节点标题查找节点 ID"""
    for node_id, node_info in workflow_data.items():
        if node_info.get("_meta", {}).get("title") == target_title:
            return node_id
    print(f"警告：未找到标题为 '{target_title}' 的节点")
    return None

def find_node_by_class_type(workflow_data: dict, class_type: str) -> str | None:
    """(备选方案) 通过 class_type 查找节点 ID (如果只有一个该类型的节点)"""
    found_nodes = [node_id for node_id, node_info in workflow_data.items() if node_info["class_type"] == class_type]
    if len(found_nodes) == 1:
        return found_nodes[0]
    elif len(found_nodes) > 1:
        print(f"警告：找到多个 '{class_type}' 类型的节点。请使用标题来区分。")
    else:
        print(f"警告：未找到 '{class_type}' 类型的节点。")
    return None

def modify_workflow_parameters(
    workflow_data: dict,
    positive_prompt: str | None = None,
    negative_prompt: str | None = None,
    seed: int | None = None,
    lora_name: str | None = None,
    lora_strength: float | None = None,
    input_image_filename: str | None = None # 服务器上的图片文件名
) -> dict:
    """
    修改工作流中的参数。
    建议通过在 ComfyUI 中为节点设置明确的标题 (Title) 来定位它们。
    """
    if positive_prompt:
        # 假设你的正面提示词节点在 ComfyUI 中标题设置为 "PositivePromptNode"
        pos_prompt_node_id = find_node_by_title(workflow_data, "PositivePromptNode")
        if not pos_prompt_node_id: # 备选：如果没找到，尝试找第一个 CLIPTextEncode
            pos_prompt_node_id = find_node_by_class_type(workflow_data, "CLIPTextEncode")

        if pos_prompt_node_id and workflow_data[pos_prompt_node_id]["class_type"] == "CLIPTextEncode":
            workflow_data[pos_prompt_node_id]["inputs"]["text"] = positive_prompt
            print(f"设置正面提示词节点 '{pos_prompt_node_id}' 的文本。")
        else:
            print("警告：未能设置正面提示词。请检查节点标题或类型。")


    if negative_prompt:
        # 假设你的负面提示词节点在 ComfyUI 中标题设置为 "NegativePromptNode"
        neg_prompt_node_id = find_node_by_title(workflow_data, "NegativePromptNode")
        # (可以添加备选逻辑，比如找第二个CLIPTextEncode，但这更不可靠)
        if neg_prompt_node_id and workflow_data[neg_prompt_node_id]["class_type"] == "CLIPTextEncode":
            workflow_data[neg_prompt_node_id]["inputs"]["text"] = negative_prompt
            print(f"设置负面提示词节点 '{neg_prompt_node_id}' 的文本。")

        else:
            print("警告：未能设置负面提示词。请检查节点标题或类型。")


    if seed is not None:
        # 假设你的 KSampler 节点在 ComfyUI 中标题设置为 "MainKSampler"
        ksampler_node_id = find_node_by_title(workflow_data, "MainKSampler")
        if not ksampler_node_id: # 备选
            ksampler_node_id = find_node_by_class_type(workflow_data, "KSampler")

        if ksampler_node_id and workflow_data[ksampler_node_id]["class_type"] in ["KSampler", "KSamplerAdvanced"]:
            workflow_data[ksampler_node_id]["inputs"]["seed"] = seed
            print(f"设置采样器节点 '{ksampler_node_id}' 的种子为 {seed}。")
        else:
            print("警告：未能设置种子。请检查 KSampler 节点标题或类型。")


    if lora_name and lora_strength is not None:
        # 假设你的 LoRA 加载节点在 ComfyUI 中标题设置为 "MyLoraLoader"
        lora_loader_node_id = find_node_by_title(workflow_data, "MyLoraLoader")
        if not lora_loader_node_id: # 备选
             lora_loader_node_id = find_node_by_class_type(workflow_data, "LoraLoader") # 或其他LoRA加载器类型

        if lora_loader_node_id and "LoraLoader" in workflow_data[lora_loader_node_id]["class_type"]:
            workflow_data[lora_loader_node_id]["inputs"]["lora_name"] = lora_name
            workflow_data[lora_loader_node_id]["inputs"]["strength_model"] = lora_strength
            workflow_data[lora_loader_node_id]["inputs"]["strength_clip"] = lora_strength # 通常 CLIP strength 和 model strength 一致
            print(f"设置 LoRA 节点 '{lora_loader_node_id}'：名称 '{lora_name}', 强度 {lora_strength}。")
        else:
            print(f"警告：未能设置 LoRA '{lora_name}'。请检查 LoRA 加载器节点标题或类型。")

    if input_image_filename:
        # 假设你的图像加载节点在 ComfyUI 中标题设置为 "InputImageNode"
        load_image_node_id = find_node_by_title(workflow_data, "InputImageNode")
        if not load_image_node_id: # 备选
            load_image_node_id = find_node_by_class_type(workflow_data, "LoadImage")

        if load_image_node_id and workflow_data[load_image_node_id]["class_type"] == "LoadImage":
            workflow_data[load_image_node_id]["inputs"]["image"] = input_image_filename
            print(f"设置图像加载节点 '{load_image_node_id}' 的图像为 '{input_image_filename}'。")
        else:
            print(f"警告：未能设置输入图像 '{input_image_filename}'。请检查 LoadImage 节点。")

    return workflow_data


def queue_prompt_on_server(prompt_workflow: dict, server_address: str, client_id: str) -> dict | None:
    """将工作流发送到 ComfyUI 服务器的 /prompt 端点"""
    payload = {"prompt": prompt_workflow, "client_id": client_id}
    data = json.dumps(payload).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    
    print(f"正在向 http://{server_address}/prompt 发送请求...")
    try:
        req = urllib.request.Request(f"http://{server_address}/prompt", data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return json.loads(response.read())
            else:
                print(f"错误：服务器返回状态 {response.status}: {response.read().decode()}")
                return None
    except urllib.error.URLError as e:
        print(f"错误：连接 ComfyUI 服务器失败: {e.reason}")
        return None
    except Exception as e:
        print(f"错误：排队提示时发生未知错误: {e}")
        return None


def upload_image_to_server(image_path: str, server_address: str, subfolder: str = "", image_type: str = "input", overwrite: bool = False) -> str | None:
    """上传图片到 ComfyUI 服务器的 /upload/image 端点"""
    if not os.path.exists(image_path):
        print(f"错误：图片文件 {image_path} 不存在。")
        return None

    url = f"http://{server_address}/upload/image"
    filename = os.path.basename(image_path)
    
    try:
        with open(image_path, 'rb') as f_image:
            files = {'image': (filename, f_image)}
            data = {'subfolder': subfolder, 'type': image_type, 'overwrite': str(overwrite).lower()}
            
            print(f"正在上传图片 '{filename}' 到 {url}...")
            response = requests.post(url, files=files, data=data)
            response.raise_for_status() # 如果HTTP请求返回了不成功的状态码，则抛出HTTPError异常
            
            upload_response_data = response.json()
            print(f"图片上传成功: {upload_response_data}")
            return upload_response_data.get('name') # 返回服务器上的文件名
            
    except requests.exceptions.RequestException as e:
        print(f"错误：上传图片失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"服务器响应: {e.response.text}")
        return None
    except Exception as e:
        print(f"错误：上传图片时发生未知错误: {e}")
        return None


def get_image_from_server(filename: str, subfolder: str, image_type: str, server_address: str) -> bytes | None:
    """从 ComfyUI 服务器的 /view 端点获取生成的图片"""
    params = {"filename": filename, "subfolder": subfolder, "type": image_type}
    url = f"http://{server_address}/view?{urllib.parse.urlencode(params)}"
    print(f"正在从 {url} 获取图片...")
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                return response.read()
            else:
                print(f"错误：获取图片失败，状态码 {response.status}")
                return None
    except urllib.error.URLError as e:
        print(f"错误：连接服务器获取图片失败: {e.reason}")
        return None

def handle_websocket_messages(ws_url: str, prompt_id_to_wait_for: str, output_dir: str, server_address: str):
    """连接 WebSocket 并处理消息，直到目标 prompt 完成并保存图片"""
    ws = websocket.WebSocket()
    try:
        ws.connect(ws_url)
        print(f"已连接到 WebSocket: {ws_url}")
    except Exception as e:
        print(f"WebSocket 连接错误: {e}")
        return

    image_counter = 0
    execution_finished_for_prompt = False
    try:
        while True:
            message_str = ws.recv()
            if not isinstance(message_str, str): # 有时可能是二进制预览图，这里主要关心JSON消息
                continue

            message = json.loads(message_str)
            # print(f"WebSocket 消息: {message['type']}") # 调试用

            if message['type'] == 'status':
                status_data = message['data']
                queue_remaining = status_data.get('status', {}).get('exec_info', {}).get('queue_remaining', -1)
                if queue_remaining == 0:
                    print("WebSocket: 队列已空。")
                    # 如果我们已经处理完目标 prompt_id 的输出，可以考虑退出
                    if execution_finished_for_prompt:
                        break


            elif message['type'] == 'executing':
                data = message['data']
                # 当 'node' 为 null 时，表示当前 prompt_id 的所有节点已执行完毕
                if data.get('node') is None and data.get('prompt_id') == prompt_id_to_wait_for:
                    print(f"WebSocket: Prompt ID '{prompt_id_to_wait_for}' 执行完毕。")
                    execution_finished_for_prompt = True
                    # 等待 'executed' 消息来获取最终输出，或者如果队列也空了就退出

            elif message['type'] == 'executed':
                data = message['data']
                if data.get('prompt_id') != prompt_id_to_wait_for: # 确保是我们关心的prompt
                    continue

                node_id = data['node']
                outputs = data.get('outputs', {})
                
                if 'images' in outputs:
                    print(f"WebSocket: 节点 '{node_id}' (Prompt ID: {prompt_id_to_wait_for}) 生成了图片。")
                    for image_info in outputs['images']:
                        # 通常我们只关心 'output' 类型的最终图像，而不是 'temp' 预览图
                        if image_info.get('type') == 'output':
                            image_counter += 1
                            filename = image_info['filename']
                            subfolder = image_info.get('subfolder', '')
                            img_type = image_info['type']
                            
                            print(f"  正在下载图片: {filename} (subfolder: '{subfolder}', type: '{img_type}')")
                            image_data = get_image_from_server(filename, subfolder, img_type, server_address)
                            if image_data:
                                if not os.path.exists(output_dir):
                                    os.makedirs(output_dir)
                                
                                output_filename = f"{prompt_id_to_wait_for}_{image_counter}_{filename}"
                                output_path = os.path.join(output_dir, output_filename)
                                try:
                                    with open(output_path, "wb") as f_img:
                                        f_img.write(image_data)
                                    print(f"  图片已保存到: {output_path}")
                                except IOError as e:
                                    print(f"  错误：保存图片失败: {e}")
                            else:
                                print(f"  错误：未能下载图片 {filename}")
            
            # 如果执行完毕且队列为空，可以安全退出
            if execution_finished_for_prompt and 'status_data' in locals() and status_data.get('status', {}).get('exec_info', {}).get('queue_remaining', -1) == 0:
                 print("WebSocket: 目标 Prompt 执行完毕且队列已空，准备断开。")
                 break


    except websocket.WebSocketConnectionClosedException:
        print("WebSocket 连接已关闭。")
    except ConnectionRefusedError:
        print(f"WebSocket 连接被拒绝。ComfyUI 是否在 {server_address} 运行?")
    except Exception as e:
        print(f"WebSocket 通信期间发生错误: {e}")
    finally:
        print("关闭 WebSocket 连接。")
        ws.close()

# --- 主执行逻辑 ---
def generate_image_from_workflow(
    workflow_api_json_path: str,
    positive_prompt: str | None = None,
    negative_prompt: str | None = None,
    seed: int | None = None,
    lora_details: dict | None = None, # 例如: {"name": "my_lora.safetensors", "strength": 0.7}
    input_image_local_path: str | None = None # 本地图片路径，用于上传
):
    """
    完整流程：加载、修改、上传（如果需要）、排队、通过 WebSocket 获取结果。
    """
    print(f"🏞️ 开始生成任务，工作流文件: {workflow_api_json_path}")

    # 1. 加载基础工作流
    base_workflow = load_workflow_api_json(workflow_api_json_path)
    if not base_workflow:
        return

    # 2. (如果需要) 上传输入图片
    server_input_image_filename = None
    if input_image_local_path:
        print(f"需要输入图片: {input_image_local_path}")
        server_input_image_filename = upload_image_to_server(
            image_path=input_image_local_path,
            server_address=COMFYUI_SERVER_ADDRESS,
            # subfolder="my_inputs", # 可以指定子文件夹
            # overwrite=True
        )
        if not server_input_image_filename:
            print("错误：输入图片上传失败，任务中止。")
            return
        print(f"图片已上传到服务器，文件名: {server_input_image_filename}")


    # 3. 修改工作流参数
    print("⚙️ 正在修改工作流参数...")
    modified_workflow = modify_workflow_parameters(
        workflow_data=base_workflow.copy(), # 操作副本以防意外修改原始加载数据
        positive_prompt=positive_prompt,
        negative_prompt=negative_prompt,
        seed=seed if seed is not None else random.randint(0, 2**32 - 1), # 如果未提供种子，则随机生成
        lora_name=lora_details.get("name") if lora_details else None,
        lora_strength=lora_details.get("strength") if lora_details else None,
        input_image_filename=server_input_image_filename # 使用服务器上的文件名
    )

    # 4. 将修改后的工作流加入队列
    print("▶️ 正在将任务加入 ComfyUI 队列...")
    response_data = queue_prompt_on_server(modified_workflow, COMFYUI_SERVER_ADDRESS, CLIENT_ID)

    if response_data and 'prompt_id' in response_data:
        prompt_id = response_data['prompt_id']
        print(f"✅ 任务已成功加入队列！Prompt ID: {prompt_id}")

        # 5. 通过 WebSocket 监听执行状态和结果
        ws_url = f"ws://{COMFYUI_SERVER_ADDRESS}/ws?clientId={CLIENT_ID}"
        handle_websocket_messages(ws_url, prompt_id, OUTPUT_DIRECTORY, COMFYUI_SERVER_ADDRESS)
        print(f"🖼️ 任务 {prompt_id} 处理完毕。")
    else:
        print("❌ 任务加入队列失败。请检查 ComfyUI 服务器状态和日志。")
        if response_data and 'error' in response_data:
            print(f"  错误详情: {response_data['error']}")
            if 'node_errors' in response_data:
                 for node_id, node_error_info in response_data['node_errors'].items():
                     print(f"    节点 {node_id} 错误: {node_error_info.get('errors', [])}")


# --- 示例用法 ---
if __name__ == "__main__":
    # 在 ComfyUI 中，请确保你的节点有以下标题，或相应修改 find_node_by_title 的参数：
    # - 正面提示词节点: "PositivePromptNode"
    # - 负面提示词节点: "NegativePromptNode"
    # - KSampler 节点: "MainKSampler"
    # - LoRA Loader 节点 (如果使用): "MyLoraLoader"
    # - Load Image 节点 (如果使用): "InputImageNode"

    workflow_file = "test.json" # 你的 API JSON 文件路径

    # 检查 test.json 是否存在，如果不存在，则提示用户
    if not os.path.exists(workflow_file):
        print(f"错误: 工作流文件 '{workflow_file}' 未找到。")
        print("请先从 ComfyUI 导出 API JSON 格式的工作流，并命名为 test.json (或修改脚本中的文件名)。")
        print("在 ComfyUI 中，建议为关键节点（如提示词、采样器、LoRA加载器）设置明确的标题 (Title) 以便脚本能准确找到它们。")
        # 创建一个非常基础的、可能无法运行的 test.json 结构示例，以便用户了解格式
        # 实际使用时，用户必须替换为自己从ComfyUI导出的有效文件
        dummy_workflow_content = {
            "1": {"class_type": "CheckpointLoaderSimple", "_meta": {"title": "Load Checkpoint"}, "inputs": {"ckpt_name": "your_checkpoint.safetensors"}},
            "2": {"class_type": "CLIPTextEncode", "_meta": {"title": "PositivePromptNode"}, "inputs": {"text": "beautiful scenery", "clip": ["1", 1]}},
            "3": {"class_type": "CLIPTextEncode", "_meta": {"title": "NegativePromptNode"}, "inputs": {"text": "ugly, blurry", "clip": ["1", 1]}},
            "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
            "5": {"class_type": "KSampler", "_meta": {"title": "MainKSampler"}, "inputs": {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0], "seed": 0, "steps": 20, "cfg": 7.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0}},
            "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
            "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "ComfyUI"}}
        }
        try:
            with open(workflow_file, 'w') as f_dummy:
                json.dump(dummy_workflow_content, f_dummy, indent=4)
            print(f"\n已创建一个示例 '{workflow_file}'。请务必用你自己的有效工作流替换它。")
        except Exception:
            pass #忽略创建示例文件时的错误
    else:
        # --- 场景1: 基本的文生图 ---
        print("\n--- 🚀 场景1: 基本文生图 ---")
        generate_image_from_workflow(
            workflow_api_json_path=workflow_file,
            positive_prompt="a majestic cat, cyberpunk style, neon lights, highly detailed",
            negative_prompt="blurry, low quality, watermark, text, bad art",
            seed=123456789
        )

        # --- 场景2: 使用 LoRA ---
        # 确保你的 "test.json" 包含一个 LoRA Loader 节点，并且其标题为 "MyLoraLoader"
        # 并且 'your_lora_name.safetensors' 存在于 ComfyUI 的 loras 文件夹中
        print("\n--- 🚀 场景2: 使用 LoRA ---")
        generate_image_from_workflow(
            workflow_api_json_path=workflow_file,
            positive_prompt="photo of a woman (character_lora:0.8) wearing a red dress",
            negative_prompt="cartoon, painting, illustration, (worst quality, low quality, normal quality:2)",
            seed=987654321,
            lora_details={"name": "your_lora_name.safetensors", "strength": 0.75} # LoRA文件名和强度
        )

        # --- 场景3: 图生图 (或使用 ControlNet 的输入图片) ---
        # 确保你的 "test.json" 包含一个 LoadImage 节点，并且其标题为 "InputImageNode"
        # 并且 "my_input_image.png" 是一个有效的本地图片文件路径
        local_image_for_img2img = "my_input_image.png" # 替换为你的本地图片路径
        if os.path.exists(local_image_for_img2img):
            print("\n--- 🚀 场景3: 图生图 ---")
            generate_image_from_workflow(
                workflow_api_json_path=workflow_file,
                positive_prompt="make this image into a vibrant oil painting, impressionist style",
                negative_prompt="photo, realistic, ugly",
                seed=555555555,
                input_image_local_path=local_image_for_img2img
            )
        else:
            print(f"\n--- ⚠️ 场景3 跳过: 输入图片 '{local_image_for_img2img}' 未找到。 ---")
```

**如何使用此脚本**:

1.  **保存脚本**: 将上面的代码保存为一个 Python 文件，例如 `comfy_api_runner.py`。
2.  **放置 `test.json`**: 将你从 ComfyUI 导出的 API JSON 文件（例如 "test.json"）与此 Python 脚本放在同一目录下，或者在脚本中修改 `workflow_file` 变量指向正确路径。
3.  **(重要!) 配置节点标题**:
    * 在 ComfyUI 中，为你想要通过脚本控制的节点（如正面/负面提示词、KSampler、LoraLoader、LoadImage等）设置清晰的**标题 (Title)**。右键点击节点 -> "Properties" -> "Node title"。
    * 确保脚本中 `find_node_by_title` 函数调用时使用的标题与你在 ComfyUI 中设置的标题一致。例如，如果你的正面提示词节点标题是 "My Positive Prompt"，那么在 `modify_workflow_parameters` 中查找时就要用 `"My Positive Prompt"`。脚本中的示例标题是 `"PositivePromptNode"`, `"NegativePromptNode"`, `"MainKSampler"`, `"MyLoraLoader"`, `"InputImageNode"`，你需要根据自己的设置进行调整。
4.  **运行脚本**:
    ```bash
    python comfy_api_runner.py
    ```
5.  **查看结果**: 生成的图片将保存在 `output_images` 文件夹中（如果该文件夹不存在，脚本会自动创建）。

---

## 适应不同的工作流

脚本中的 `modify_workflow_parameters` 函数是适应性的关键。

* **通过标题定位节点**: 如前所述，使用节点标题 (`_meta.title`) 是最灵活的方式。只要你在不同的工作流中对同类功能的节点使用一致的标题（例如，正面提示词节点总是叫 "PositivePromptNode"），脚本就能找到它们。
* **通过 `class_type` 定位**: 如果某个类型的节点在工作流中是唯一的（例如，通常只有一个 `KSampler`），你可以通过 `class_type` 来查找。但如果存在多个同类型节点，就需要更精确的定位方式（如标题）。
* **条件化参数修改**: 你可以扩展 `modify_workflow_parameters` 函数，使其仅在特定节点存在时才尝试修改。例如，仅当找到 "MyLoraLoader" 节点时才尝试设置 LoRA 参数。
* **动态加载不同的 JSON 文件**: 你的外部程序可以根据需要选择加载不同的 `workflow_*.json` 文件。

通过这种方式，你可以编写一个相对通用的外部程序，通过传入不同的参数和选择不同的基础 JSON 文件来调用各种 ComfyUI 工作流。