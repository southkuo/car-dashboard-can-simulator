#!/usr/bin/env python3
"""
完整測試腳本 - 驗證CAN模擬器的所有功能
測試: DBC載入、編碼/解碼、訊號模擬、TCP通訊
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
        """測試1: DBC文件存在且有效"""
        self.print_header("測試1: DBC文件驗證")
        
        dbc_file = self.base_path / 'Dashboard.dbc'
        self.assert_true(dbc_file.exists(), f"DBC文件存在: {dbc_file}")
        
        # 嘗試載入DBC
        try:
            import cantools
            db = cantools.database.load_file(str(dbc_file))
            self.assert_true(True, f"DBC文件格式有效 ({len(db.messages)} 條訊息)")
            
            # 檢查期望的訊息
            expected_msgs = ['EngineStatus', 'VehicleStatus', 'WarningLights']
            for msg_name in expected_msgs:
                msg = db.get_message_by_name(msg_name)
                self.assert_true(msg is not None, f"存在訊息: {msg_name}")
        
        except ImportError:
            self.assert_true(False, "cantools庫未安裝")
        except Exception as e:
            self.assert_true(False, f"DBC載入失敗: {e}")
    
    def test_can_simulator_startup(self):
        """測試2: CAN模擬器能否啟動"""
        self.print_header("測試2: CAN模擬器啟動測試")
        
        simulator_file = self.base_path / 'can_simulator.py'
        self.assert_true(simulator_file.exists(), f"模擬器腳本存在: {simulator_file}")
        
        # 檢查匯入
        try:
            import can_simulator
            self.assert_true(True, "can_simulator.py 可以匯入")
            
            # 檢查CANSimulator类
            self.assert_true(
                hasattr(can_simulator, 'CANSimulator'),
                "CANSimulator 类存在"
            )
        except ImportError as e:
            self.assert_true(False, f"匯入失敗: {e}")
    
    def test_tcp_connection(self):
        """測試3: TCP連線和資料接收"""
        self.print_header("測試3: TCP連線測試 (快速)")
        
        # 嘗試連線到localhost:9999
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        
        try:
            result = sock.connect_ex(('127.0.0.1', 9999))
            if result == 0:
                self.assert_true(True, "TCP服务器在執行 (127.0.0.1:9999)")
                
                # 嘗試接收一條訊息
                sock.settimeout(2)
                data = sock.recv(4096)
                
                if data:
                    try:
                        json_data = json.loads(data.decode('utf-8').strip())
                        self.assert_true(
                            'timestamp' in json_data and 'messages' in json_data,
                            "接收到有效的JSON資料"
                        )
                        self.assert_true(
                            'EngineStatus' in json_data['messages'],
                            "訊息包含 EngineStatus"
                        )
                    except json.JSONDecodeError:
                        self.assert_true(False, "接收到的資料不是有效JSON")
                else:
                    self.assert_true(False, "未能接收資料")
            else:
                self.assert_true(False, "TCP服务器未在執行 - 請先啟動模擬器")
        
        except (socket.timeout, ConnectionRefusedError):
            self.assert_true(False, "无法連線到TCP服务器 - 請先啟動模擬器")
        finally:
            sock.close()
    
    def test_signal_decoding(self):
        """測試4: 訊號編碼和解碼"""
        self.print_header("測試4: 訊號编解碼測試")
        
        try:
            import cantools
            
            dbc_file = self.base_path / 'Dashboard.dbc'
            db = cantools.database.load_file(str(dbc_file))
            
            # 取得EngineStatus訊息
            msg = db.get_message_by_name('EngineStatus')
            self.assert_true(msg is not None, "可以取得 EngineStatus 訊息")
            
            # 測試編碼
            signals = {
                'EngineRPM': 1500,
                'EngineTemp': 85,
                'FuelLevel': 90,
                'BatteryVoltage': 13.5,
            }
            
            encoded = msg.encode(signals)
            self.assert_true(len(encoded) > 0, f"訊號編碼成功 ({len(encoded)} 字节)")
            
            # 測試解碼
            decoded = msg.decode(encoded)
            self.assert_true(decoded is not None, "訊號解碼成功")
            
            # 驗證值
            rpm_match = abs(decoded['EngineRPM'] - 1500) < 1
            self.assert_true(rpm_match, f"RPM值正確 (編碼: 1500, 解碼: {decoded['EngineRPM']:.1f})")
            
            temp_match = abs(decoded['EngineTemp'] - 85) < 1
            self.assert_true(temp_match, f"溫度值正確 (編碼: 85, 解碼: {decoded['EngineTemp']:.1f})")
        
        except Exception as e:
            self.assert_true(False, f"编解碼測試失敗: {e}")
    
    def test_client_script(self):
        """測試5: 客戶端腳本"""
        self.print_header("測試5: 客戶端腳本驗證")
        
        client_file = self.base_path / 'can_client.py'
        self.assert_true(client_file.exists(), f"客戶端腳本存在: {client_file}")
        
        try:
            import can_client
            self.assert_true(True, "can_client.py 可以匯入")
            self.assert_true(
                hasattr(can_client, 'CANClient'),
                "CANClient 类存在"
            )
        except ImportError as e:
            self.assert_true(False, f"匯入失敗: {e}")
    
    def test_analyzer_script(self):
        """測試6: 分析器腳本"""
        self.print_header("測試6: DBC分析腳本驗證")
        
        analyzer_file = self.base_path / 'dbc_analyzer.py'
        self.assert_true(analyzer_file.exists(), f"分析腳本存在: {analyzer_file}")
        
        # 檢查腳本可執行性
        try:
            result = subprocess.run(
                ['python3', str(analyzer_file)],
                timeout=5,
                capture_output=True,
                text=True
            )
            self.assert_true(
                'DBC文件詳細分析' in result.stdout or result.returncode == 0,
                "分析腳本可以正常執行"
            )
        except subprocess.TimeoutExpired:
            self.assert_true(False, "分析腳本執行逾時")
        except Exception as e:
            self.assert_true(False, f"腳本执行失敗: {e}")
    
    def test_python_dependencies(self):
        """測試7: Python依賴檢查"""
        self.print_header("測試7: Python依賴檢查")
        
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
        """執行所有測試"""
        print("\n" + "="*70)
        print("🧪 車用儀表板 CAN模擬器 - 完整測試")
        print("="*70)
        
        self.test_python_dependencies()
        self.test_dbc_file()
        self.test_can_simulator_startup()
        self.test_signal_decoding()
        self.test_client_script()
        self.test_analyzer_script()
        
        # 只有在模擬器執行时才測試TCP
        print(f"\n{'='*70}")
        print("✓ 可选測試: TCP連線 (需要模擬器正在執行)")
        print(f"{'='*70}")
        self.test_tcp_connection()
        
        # 總結
        print(f"\n{'='*70}")
        print("📊 測試結果總結")
        print(f"{'='*70}")
        print(f"\n  ✅ 通過: {self.passed}")
        print(f"  ❌ 失敗: {self.failed}")
        print(f"  📈 通過率: {self.passed/(self.passed+self.failed)*100:.1f}%\n")
        
        if self.failed == 0:
            print("  🎉 所有測試通過！系統已准备就緒。")
            print("\n  下一步:")
            print("    1. 啟動模擬器:  python3 can_simulator.py")
            print("    2. 啟動客戶端:  python3 can_client.py")
            return True
        else:
            print(f"  ⚠️  有 {self.failed} 項測試失敗。請檢查上述錯誤。")
            return False


def main():
    runner = TestRunner()
    success = runner.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
