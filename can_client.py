#!/usr/bin/env python3
"""
CAN模拟器客户端 - 用于测试和调试
连接到模拟器并实时显示接收的数据
"""

import socket
import json
import time
from datetime import datetime


class CANClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 9999):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self):
        """连接到CAN模拟器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"✅ 已连接到 {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def receive_messages(self):
        """接收并显示CAN消息"""
        buffer = ""
        
        try:
            while True:
                # 接收数据
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    print("❌ 连接已关闭")
                    break
                
                buffer += data
                
                # 处理完整的JSON行
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self._process_message(line)
        
        except KeyboardInterrupt:
            print("\n👋 停止接收")
        except Exception as e:
            print(f"❌ 接收错误: {e}")
        finally:
            self.close()
    
    def _process_message(self, json_line: str):
        """处理单条消息"""
        try:
            data = json.loads(json_line)
            timestamp = datetime.fromtimestamp(data['timestamp']).strftime('%H:%M:%S.%f')[:-3]
            
            print(f"\n⏱️  {timestamp}")
            print("=" * 80)
            
            for msg_name, msg_data in data['messages'].items():
                print(f"\n📨 {msg_name} (0x{msg_data['frame_id']:03X})")
                print("-" * 40)
                
                for signal_name, signal_info in msg_data['signals'].items():
                    value = signal_info['value']
                    unit = signal_info['unit']
                    
                    # 美化输出
                    value_str = f"{value:>10.2f}" if isinstance(value, (int, float)) else str(value)
                    unit_str = f" {unit}" if unit else ""
                    
                    print(f"  {signal_name:<25} = {value_str}{unit_str}")
        
        except json.JSONDecodeError:
            print(f"❌ JSON解析错误: {json_line[:100]}")
        except Exception as e:
            print(f"❌ 处理错误: {e}")
    
    def close(self):
        """关闭连接"""
        if self.socket:
            self.socket.close()
            print("✅ 连接已关闭")


def main():
    print("🚗 CAN模拟器客户端")
    print("-" * 40)
    
    client = CANClient()
    
    if client.connect():
        print("\n💡 数据格式: JSON (消息 -> 信号 -> 值+单位)")
        print("💡 按 Ctrl+C 停止接收\n")
        client.receive_messages()


if __name__ == "__main__":
    main()
