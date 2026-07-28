"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import sys
import re
from datetime import datetime
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("test_cases", [])


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}")
    
    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")


def log_trace(trace_str: str):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    trace_file = os.path.join(base_dir, "docs", "trace_eval.md")
    os.makedirs(os.path.dirname(trace_file), exist_ok=True)
    with open(trace_file, "a", encoding="utf-8") as f:
        f.write(trace_str + "\n")


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) có Guardrails.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    step = 0
    
    trace_log = f"\n## 🔍 TRACE LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    trace_log += f"**Câu hỏi**: *{user_query}*\n\n"
    
    # Khởi tạo context với câu hỏi của người dùng
    context = f"Question: {user_query}\n"
    
    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")
        
        # Gọi LLM Provider thực hiện sinh câu trả lời theo context
        response = provider.generate(context, system_prompt=REACT_SYSTEM_PROMPT)
        
        # In ra phản hồi của LLM để theo dõi
        print(response)
        
        # Thêm response vào context
        context += response + "\n"
        trace_log += f"### Step {step}\n{response}\n"
        
        # Kiểm tra xem có Final Answer không
        if "Final Answer:" in response:
            print(f"🏁 Đã tìm thấy Final Answer. Kết thúc!")
            trace_log += "\n**KẾT LUẬN**: Hoàn thành xuất sắc nhiệm vụ nhờ sự kết hợp giữa suy luận và công cụ.\n"
            break
            
        # Tìm Action
        action_match = re.search(r"Action:\s*([a-zA-Z0-9_]+)\[(.*?)\]", response)
        
        if action_match:
            tool_name = action_match.group(1).strip()
            tool_args_str = action_match.group(2).strip()
            
            print(f"🛠️ Phát hiện Action: {tool_name} với args: {tool_args_str}")
            
            # Xử lý tham số truyền vào
            args = [arg.strip(" '\"") for arg in tool_args_str.split(",") if arg.strip()]
            
            # Thực thi tool
            if tool_name in AVAILABLE_TOOLS:
                tool_func = AVAILABLE_TOOLS[tool_name]
                try:
                    obs = tool_func(*args)
                except Exception as e:
                    obs = f"LỖI KHI GỌI TOOL: {str(e)}"
            else:
                obs = f"LỖI: Tool '{tool_name}' không tồn tại. Vui lòng chọn tool từ danh sách cho phép."
                
            print(f"👁️ Observation: {obs}")
            
            # Thêm Observation vào context cho vòng lặp tiếp theo
            context += f"Observation: {obs}\n"
            trace_log += f"\n* **Observation {step}**: `{obs}`\n"
            
        else:
            print("⚠️ Không tìm thấy Action hay Final Answer đúng định dạng. Ép buộc LLM tuân thủ...")
            obs = "LỖI: Phản hồi sai định dạng. Bạn phải cung cấp 'Action: tool_name[args]' hoặc 'Final Answer: ...'."
            context += f"Observation: {obs}\n"
            trace_log += f"\n* **Observation {step}**: `{obs}`\n"
            
    if step >= MAX_ITERATIONS:
        print(f"🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!")
        trace_log += f"\n**KẾT LUẬN**: 🛡️ GUARDRAIL TRIGGERED - Ngắt lặp an toàn sau {MAX_ITERATIONS} bước.\n"
        
    # Ghi log ra file
    log_trace(trace_log)


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("==================================================")
    
    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")
    
    if len(tests) > 2:
        # Chạy thử câu test số 3 (TC-03)
        sample_query = tests[4]["question"]
        
        print("--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
        run_baseline_chatbot(sample_query, provider)
        
        print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
        run_react_agent(sample_query, provider)
    else:
        print("❌ Lỗi: Không đủ test cases.")
