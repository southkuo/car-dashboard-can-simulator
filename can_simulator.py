#!/usr/bin/env python3
"""
車用儀表板CAN模擬器
- 解析DBC文件
- 生成逼真的CAN訊號
- 通過TCP Socket发送JSON資料给Qt应用
"""

import socket
import json
import time
import math
import threading
from typing import Dict, Any
import os
import sys

try:
    import cantools
except ImportError:
    print("❌ 需要安裝cantools庫：pip install cantools")
    sys.exit(1)


class CANSimulator:
    def __init__(self, dbc_file: str, host: str = "127.0.0.1", port: int = 9999):
        """
        初始化CAN模擬器
        
        Args:
            dbc_file: DBC文件路径
            host: TCP服务器地址
            port: TCP服务器端口
        """
        self.dbc_file = dbc_file
        self.host = host
        self.port = port
        self.running = False
        self.clients = []
        self.server_socket = None
        
        # 載入DBC資料庫
        self.load_dbc()
        
        # 初始化訊號值（模拟狀態）
        self.signal_values = self._init_signal_values()
        self.message_timestamps = {}
        
        # 模擬参数
        self.engine_running = True
        self.vehicle_speed_target = 0
        self.acceleration = 0
        
    def load_dbc(self):
        """載入並解析DBC文件"""
        if not os.path.exists(self.dbc_file):
            raise FileNotFoundError(f"DBC文件未找到: {self.dbc_file}")
        
        self.db = cantools.database.load_file(self.dbc_file)
        print(f"✅ 已載入DBC文件: {self.dbc_file}")
        print(f"   訊息数: {len(self.db.messages)}")
        for msg in self.db.messages:
            print(f"   - {msg.name} (ID: 0x{msg.frame_id:X})")
    
    def _init_signal_values(self) -> Dict[str, Dict[str, float]]:
        """初始化所有訊號的初始值"""
        values = {}
        for message in self.db.messages:
            values[message.name] = {}
            for signal in message.signals:
                # 為每个訊號設定合理的初始值
                values[message.name][signal.name] = signal.initial or self._get_default_value(signal.name)
        return values
    
    def _get_default_value(self, signal_name: str) -> float:
        """為不同訊號返回合理的預設值"""
        defaults = {
            'EngineRPM': 0,
            'EngineTemp': 20,
            'FuelLevel': 80,
            'BatteryVoltage': 13.5,
            'VehicleSpeed': 0,
            'GearPosition': 0,  # P
            'BrakePressure': 0,
            'AmbientTemp': 20,
            'CheckEngineLight': 0,
            'ABS_Active': 0,
            'BatteryWarning': 0,
            'OilPressureWarning': 0,
            'HighBeam': 0,
        }
        return defaults.get(signal_name, 0)
    
    def _simulate_signals(self):
        """模拟逼真的CAN訊號變化"""
        # 模拟引擎转速 - 怠速~3000rpm，带隨機波动
        if self.engine_running:
            idle_rpm = 700
            rpm_variation = 100 * math.sin(time.time() * 0.5)  # 低頻波动
            target_rpm = idle_rpm + rpm_variation
            
            # 模拟加速
            if self.vehicle_speed_target > self.signal_values['VehicleStatus']['VehicleSpeed']:
                target_rpm = min(5000, idle_rpm + 2000)
                self.acceleration = 2  # km/h²
            else:
                self.acceleration = -1  # 減速
            
            # 平滑過渡RPM
            current_rpm = self.signal_values['EngineStatus']['EngineRPM']
            self.signal_values['EngineStatus']['EngineRPM'] = current_rpm * 0.95 + target_rpm * 0.05
        else:
            self.signal_values['EngineStatus']['EngineRPM'] = 0
        
        # 模拟油溫 - 從冷啟動到正常溫度
        engine_temp = self.signal_values['EngineStatus']['EngineTemp']
        if self.engine_running:
            # 逐漸升温到90°C
            self.signal_values['EngineStatus']['EngineTemp'] = engine_temp * 0.99 + 90 * 0.01
        else:
            # 逐漸冷却
            self.signal_values['EngineStatus']['EngineTemp'] = engine_temp * 0.98 + 20 * 0.02
        
        # 模拟燃油液位 - 缓慢下降
        self.signal_values['EngineStatus']['FuelLevel'] -= 0.001
        self.signal_values['EngineStatus']['FuelLevel'] = max(0, self.signal_values['EngineStatus']['FuelLevel'])
        
        # 模拟電池电压 - 在12.5~14.5V之間波动
        voltage_noise = 0.5 * math.sin(time.time() * 0.3)
        self.signal_values['EngineStatus']['BatteryVoltage'] = 13.5 + voltage_noise
        
        # 模拟车速 - 平滑加速/減速
        current_speed = self.signal_values['VehicleStatus']['VehicleSpeed']
        speed_change = self.acceleration * 0.1  # 每次更新的速度變化
        new_speed = max(0, min(180, current_speed + speed_change))
        self.signal_values['VehicleStatus']['VehicleSpeed'] = new_speed
        
        # 根據车速設定檔位
        if new_speed == 0:
            self.signal_values['VehicleStatus']['GearPosition'] = 0  # P
        elif new_speed > 0:
            self.signal_values['VehicleStatus']['GearPosition'] = 3  # D
        
        # 模拟煞車压力 - 当減速时
        if self.acceleration < -0.5:
            brake_pressure = 200 + 100 * math.sin(time.time())
            self.signal_values['VehicleStatus']['BrakePressure'] = brake_pressure
        else:
            self.signal_values['VehicleStatus']['BrakePressure'] *= 0.9
        
        # 環境溫度 - 随时间缓慢變化
        self.signal_values['VehicleStatus']['AmbientTemp'] = 20 + 10 * math.sin(time.time() * 0.01)
        
        # 警告燈 - 基于條件判斷
        self.signal_values['WarningLights']['CheckEngineLight'] = 0
        self.signal_values['WarningLights']['BatteryWarning'] = 1 if self.signal_values['EngineStatus']['BatteryVoltage'] < 12 else 0
        self.signal_values['WarningLights']['OilPressureWarning'] = 0
        self.signal_values['WarningLights']['ABS_Active'] = 1 if self.signal_values['VehicleStatus']['BrakePressure'] > 500 else 0
    
    def get_can_messages(self) -> Dict[str, Any]:
        """取得格式化的CAN訊息（用於发送）"""
        messages = {}
        for message in self.db.messages:
            msg_dict = {
                'frame_id': message.frame_id,
                'name': message.name,
                'timestamp': time.time(),
                'signals': {}
            }
            
            for signal in message.signals:
                value = self.signal_values[message.name].get(signal.name, 0)
                msg_dict['signals'][signal.name] = {
                    'value': round(value, 3),
                    'unit': signal.unit or ''
                }
            
            messages[message.name] = msg_dict
        
        return messages
    
    def start_tcp_server(self):
        """啟動TCP服务器"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"✅ TCP服务器啟動: {self.host}:{self.port}")
            
            # 接受客戶端連線
            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_socket, client_addr = self.server_socket.accept()
                    print(f"📱 新客戶端連線: {client_addr}")
                    self.clients.append(client_socket)
                except socket.timeout:
                    continue
        except Exception as e:
            print(f"❌ TCP服务器錯誤: {e}")
        finally:
            self.server_socket.close()
    
    def broadcast_messages(self):
        """廣播CAN訊息给所有連線的客戶端"""
        while self.running:
            try:
                # 更新訊號值
                self._simulate_signals()
                
                # 取得訊息
                messages = self.get_can_messages()
                
                # 转為JSON並发送
                json_data = json.dumps({
                    'timestamp': time.time(),
                    'messages': messages
                })
                
                # 廣播给所有客戶端
                dead_clients = []
                for client in self.clients:
                    try:
                        client.sendall((json_data + '\n').encode('utf-8'))
                    except (BrokenPipeError, ConnectionResetError):
                        dead_clients.append(client)
                
                # 清除已斷開的連線
                for client in dead_clients:
                    self.clients.remove(client)
                    print(f"❌ 客戶端斷開連線")
                
                # 按DBC中定義的週期发送（這里簡化為100ms）
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ 廣播錯誤: {e}")
    
    def run(self):
        """執行模擬器"""
        self.running = True
        
        # 啟動TCP服务器线程
        server_thread = threading.Thread(target=self.start_tcp_server, daemon=True)
        server_thread.start()
        
        # 啟動廣播线程
        broadcast_thread = threading.Thread(target=self.broadcast_messages, daemon=True)
        broadcast_thread.start()
        
        print(f"\n🚗 CAN模擬器執行中...")
        print(f"   DBC: {self.dbc_file}")
        print(f"   地址: {self.host}:{self.port}")
        print(f"\n💡 使用範例:")
        print(f"   nc {self.host} {self.port}  # 在另一個終端中查看資料")
        print(f"   按 Ctrl+C 停止\n")
        
        try:
            # 互動式命令
            while True:
                cmd = input("輸入命令 (start/stop/speed/quit): ").strip().lower()
                
                if cmd == 'start':
                    self.engine_running = True
                    print("🏁 引擎啟動")
                elif cmd == 'stop':
                    self.engine_running = False
                    self.vehicle_speed_target = 0
                    print("🛑 引擎關閉")
                elif cmd.startswith('speed '):
                    try:
                        speed = float(cmd.split()[1])
                        self.vehicle_speed_target = max(0, min(180, speed))
                        print(f"🚗 目标速度: {self.vehicle_speed_target} km/h")
                    except:
                        print("❌ 無效速度，用法: speed 60")
                elif cmd == 'quit' or cmd == 'exit':
                    print("👋 關閉模擬器...")
                    self.running = False
                    break
                else:
                    print("❓ 未知命令")
        
        except KeyboardInterrupt:
            print("\n👋 關閉模擬器...")
            self.running = False
        finally:
            # 關閉所有客戶端連線
            for client in self.clients:
                client.close()
            if self.server_socket:
                self.server_socket.close()


def main():
    # 取得DBC文件路径
    dbc_file = os.path.dirname(__file__) + '/Dashboard.dbc'
    
    # 建立並執行模擬器
    simulator = CANSimulator(dbc_file)
    simulator.run()


if __name__ == "__main__":
    main()
