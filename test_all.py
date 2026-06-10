#!/usr/bin/env python3
"""
完整测试脚本 - 验证CAN模拟器的所有功能
测试: DBC加载、编码/解码、信号仿真、TCP通信
"""

import subprocess
import time
import socket
import json
import sys
from pathlib import Path


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.base_path = Path(__file__).parent
    
    def print_header(self, text: str):
        print(f"\n{'='*70}")
        print(f"🧪 {text}")
        print(f"{'='*70}\n")
    
    def assert_true(self, condition: bool, message: str):
        if condition:
            self.passed += 1
            print(f"  ✅ {message}")
        else:
            self.failed += 1
            print(f"  ❌ {message}")
    
    def test_dbc_file(self):
        """测试1: DBC文件存在且有效"""
        self.print_header("测试1: DBC文件验证")
        
        dbc_file = self.base_path / 'Dashboard.dbc'
        self.assert_true(dbc_file.exists(), f"DBC文件存在: {dbc_file}")
        
        # 尝试加载DBC
        try:
            import cantools
            db = cantools.database.load_file(str(dbc_file))
            self.assert_true(True, f"DBC文件格式有效 ({len(db.messages)} 条消息)")
            
            # 检查期望的消息
            expected_msgs = ['EngineStatus', 'VehicleStatus', 'WarningLights']
            for msg_name in expected_msgs:
                msg = db.get_message_by_name(msg_name)
                self.assert_true(msg is not None, f"存在消息: {msg_name}")
        
        except ImportError:
            self.assert_true(False, "cantools库未安装")
        except Exception as e:
            self.assert_true(False, f"DBC加载失败: {e}")
    
    def test_can_simulator_startup(self):
        """测试2: CAN模拟器能否启动"""
        self.print_header("测试2: CAN模拟器启动测试")
        
        simulator_file = self.base_path / 'can_simulator.py'
        self.assert_true(simulator_file.exists(), f"模拟器脚本存在: {simulator_file}")
        
        # 检查导入
        try:
            import can_simulator
            self.assert_true(True, "can_simulator.py 可以导入")
            
            # 检查CANSimulator类
            self.assert_true(
                hasattr(can_simulator, 'CANSimulator'),
                "CANSimulator 类存在"
            )
        except ImportError as e:
            self.assert_true(False, f"导入失败: {e}")
    
    def test_tcp_connection(self):
        """测试3: TCP连接和数据接收"""
        self.print_header("测试3: TCP连接测试 (快速)")
        
        # 尝试连接到localhost:9999
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        
        try:
            result = sock.connect_ex(('127.0.0.1', 9999))
            if result == 0:
                self.assert_true(True, "TCP服务器在运行 (127.0.0.1:9999)")
                
                # 尝试接收一条消息
                sock.settimeout(2)
                data = sock.recv(4096)
                
                if data:
                    try:
                        json_data = json.loads(data.decode('utf-8').strip())
                        self.assert_true(
                            'timestamp' in json_data and 'messages' in json_data,
                            "接收到有效的JSON数据"
                        )
                        self.assert_true(
                            'EngineStatus' in json_data['messages'],
                            "消息包含 EngineStatus"
                        )
                    except json.JSONDecodeError:
                        self.assert_true(False, "接收到的数据不是有效JSON")
                else:
                    self.assert_true(False, "未能接收数据")
            else:
                self.assert_true(False, "TCP服务器未在运行 - 请先启动模拟器")
        
        except (socket.timeout, ConnectionRefusedError):
            self.assert_true(False, "无法连接到TCP服务器 - 请先启动模拟器")
        finally:
            sock.close()
    
    def test_signal_decoding(self):
        """测试4: 信号编码和解码"""
        self.print_header("测试4: 信号编解码测试")
        
        try:
            import cantools
            
            dbc_file = self.base_path / 'Dashboard.dbc'
            db = cantools.database.load_file(str(dbc_file))
            
            # 获取EngineStatus消息
            msg = db.get_message_by_name('EngineStatus')
            self.assert_true(msg is not None, "可以获取 EngineStatus 消息")
            
            # 测试编码
            signals = {
                'EngineRPM': 1500,
                'EngineTemp': 85,
                'FuelLevel': 90,
                'BatteryVoltage': 13.5,
            }
            
            encoded = msg.encode(signals)
            self.assert_true(len(encoded) > 0, f"信号编码成功 ({len(encoded)} 字节)")
            
            # 测试解码
            decoded = msg.decode(encoded)
            self.assert_true(decoded is not None, "信号解码成功")
            
            # 验证值
            rpm_match = abs(decoded['EngineRPM'] - 1500) < 1
            self.assert_true(rpm_match, f"RPM值正确 (编码: 1500, 解码: {decoded['EngineRPM']:.1f})")
            
            temp_match = abs(decoded['EngineTemp'] - 85) < 1
            self.assert_true(temp_match, f"温度值正确 (编码: 85, 解码: {decoded['EngineTemp']:.1f})")
        
        except Exception as e:
            self.assert_true(False, f"编解码测试失败: {e}")
    
    def test_client_script(self):
        """测试5: 客户端脚本"""
        self.print_header("测试5: 客户端脚本验证")
        
        client_file = self.base_path / 'can_client.py'
        self.assert_true(client_file.exists(), f"客户端脚本存在: {client_file}")
        
        try:
            import can_client
            self.assert_true(True, "can_client.py 可以导入")
            self.assert_true(
                hasattr(can_client, 'CANClient'),
                "CANClient 类存在"
            )
        except ImportError as e:
            self.assert_true(False, f"导入失败: {e}")
    
    def test_analyzer_script(self):
        """测试6: 分析器脚本"""
        self.print_header("测试6: DBC分析脚本验证")
        
        analyzer_file = self.base_path / 'dbc_analyzer.py'
        self.assert_true(analyzer_file.exists(), f"分析脚本存在: {analyzer_file}")
        
        # 检查脚本可执行性
        try:
            result = subprocess.run(
                ['python3', str(analyzer_file)],
                timeout=5,
                capture_output=True,
                text=True
            )
            self.assert_true(
                'DBC文件详细分析' in result.stdout or result.returncode == 0,
                "分析脚本可以正常执行"
            )
        except subprocess.TimeoutExpired:
            self.assert_true(False, "分析脚本执行超时")
        except Exception as e:
            self.assert_true(False, f"脚本执行失败: {e}")
    
    def test_python_dependencies(self):
        """测试7: Python依赖检查"""
        self.print_header("测试7: Python依赖检查")
        
        required_packages = {
            'cantools': 'CAN DBC解析',
        }
        
        for package, description in required_packages.items():
            try:
                __import__(package)
                self.assert_true(True, f"{package} ({description})")
            except ImportError:
                self.assert_true(False, f"{package} ({description})")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*70)
        print("🧪 车用仪表板 CAN模拟器 - 完整测试")
        print("="*70)
        
        self.test_python_dependencies()
        self.test_dbc_file()
        self.test_can_simulator_startup()
        self.test_signal_decoding()
        self.test_client_script()
        self.test_analyzer_script()
        
        # 只有在模拟器运行时才测试TCP
        print(f"\n{'='*70}")
        print("✓ 可选测试: TCP连接 (需要模拟器正在运行)")
        print(f"{'='*70}")
        self.test_tcp_connection()
        
        # 总结
        print(f"\n{'='*70}")
        print("📊 测试结果总结")
        print(f"{'='*70}")
        print(f"\n  ✅ 通过: {self.passed}")
        print(f"  ❌ 失败: {self.failed}")
        print(f"  📈 通过率: {self.passed/(self.passed+self.failed)*100:.1f}%\n")
        
        if self.failed == 0:
            print("  🎉 所有测试通过！系统已准备就绪。")
            print("\n  下一步:")
            print("    1. 启动模拟器:  python3 can_simulator.py")
            print("    2. 启动客户端:  python3 can_client.py")
            return True
        else:
            print(f"  ⚠️  有 {self.failed} 项测试失败。请检查上述错误。")
            return False


def main():
    runner = TestRunner()
    success = runner.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
