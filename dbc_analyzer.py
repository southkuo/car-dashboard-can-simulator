#!/usr/bin/env python3
"""
DBC解析和轉換工具 - 詳細示範cantools庫的功能
用於理解DBC的結構和訊號轉換
"""

import cantools
import json
from pathlib import Path


def analyze_dbc(dbc_file: str):
    """詳細分析DBC文件"""
    
    print("=" * 80)
    print("🔍 DBC文件詳細分析")
    print("=" * 80)
    
    db = cantools.database.load_file(dbc_file)
    
    print(f"\n📄 文件: {dbc_file}")
    print(f"📊 總訊息數: {len(db.messages)}")
    print(f"🔌 ECU節點: {len(db.nodes)} - {', '.join([n.name for n in db.nodes])}")
    
    # 詳細信息
    print(f"\n{'訊息名':<20} {'ID':<8} {'DLC':<6} {'週期':<8} {'訊號數':<8}")
    print("-" * 80)
    
    for message in db.messages:
        cycle_time = message.cycle_time or 0
        print(f"{message.name:<20} {f'0x{message.frame_id:X}':<8} {message.length:<6} {cycle_time:<8}ms {len(message.signals):<8}")
        
        # 顯示訊號詳情
        for signal in message.signals:
            scale = signal.scale if signal.scale != 1 else ""
            offset = signal.offset if signal.offset != 0 else ""
            
            print(f"  └─ {signal.name:<18} [{signal.start}:{signal.length}] "
                  f"min={signal.minimum:<8} max={signal.maximum:<8} "
                  f"unit={signal.unit or 'N/A':<8}")
            
            if signal.receivers:
                print(f"     ├─ 接收者: {', '.join(signal.receivers)}")
            
            if scale or offset:
                print(f"     └─ 轉換: value = raw * {scale} + {offset}")
    
    print("\n" + "=" * 80)
    return db


def demonstrate_encoding(db):
    """示範訊號編碼"""
    
    print("\n" + "=" * 80)
    print("📝 訊號編碼示範 - 如何將資料編碼為CAN訊息")
    print("=" * 80)
    
    # 取得EngineStatus訊息
    msg = db.get_message_by_name('EngineStatus')
    
    print(f"\n訊息: {msg.name} (ID: 0x{msg.frame_id:X})")
    print("-" * 80)
    
    # 准备訊號數据
    signals = {
        'EngineRPM': 1500,        # rpm
        'EngineTemp': 85,         # °C
        'FuelLevel': 90,          # %
        'BatteryVoltage': 13.5,   # V
    }
    
    print("\n📤 輸入訊號值:")
    for name, value in signals.items():
        signal = msg.get_signal_by_name(name)
        print(f"  {name:<20} = {value:<10} {signal.unit}")
    
    # 編碼
    encoded_data = msg.encode(signals)
    print(f"\n✅ 編碼後的原始資料 (hex): {encoded_data.hex().upper()}")
    print(f"   二進位: {' '.join(format(b, '08b') for b in encoded_data)}")
    
    # 解碼驗證
    decoded = msg.decode(encoded_data)
    print(f"\n🔄 解碼驗證:")
    for name, value in decoded.items():
        signal = msg.get_signal_by_name(name)
        original = signals.get(name)
        match = "✅" if abs(value - original) < 0.1 else "⚠️"
        print(f"  {match} {name:<20} = {value:<10.2f} (原值: {original})")


def demonstrate_decoding(db):
    """示範訊號解碼"""
    
    print("\n" + "=" * 80)
    print("📖 訊號解碼示範 - 如何從CAN訊息提取資料")
    print("=" * 80)
    
    msg = db.get_message_by_name('VehicleStatus')
    
    print(f"\n訊息: {msg.name} (ID: 0x{msg.frame_id:X})")
    print("-" * 80)
    
    # 模拟CAN原始資料
    raw_data = bytes([0x5A, 0x00, 0x03, 0x00, 0x64, 0x00, 0x16, 0x00])
    
    print(f"\n📥 接收的原始資料 (hex): {raw_data.hex().upper()}")
    print(f"   二進位: {' '.join(format(b, '08b') for b in raw_data)}")
    
    # 解碼
    decoded = msg.decode(raw_data)
    
    print(f"\n✅ 解碼後的訊號值:")
    for name, value in decoded.items():
        signal = msg.get_signal_by_name(name)
        print(f"  {name:<20} = {value:<10.2f} {signal.unit}")


def export_signal_mapping(db):
    """匯出訊號映射為JSON"""
    
    print("\n" + "=" * 80)
    print("💾 匯出訊號映射 - 用於前端顯示")
    print("=" * 80)
    
    mapping = {}
    
    for message in db.messages:
        msg_entry = {
            'frame_id': message.frame_id,
            'name': message.name,
            'length': message.length,
            'cycle_time': message.cycle_time,
            'signals': {}
        }
        
        for signal in message.signals:
            msg_entry['signals'][signal.name] = {
                'start_bit': signal.start,
                'length': signal.length,
                'byte_order': signal.byte_order,
                'is_signed': signal.is_signed,
                'scale': signal.scale,
                'offset': signal.offset,
                'minimum': signal.minimum,
                'maximum': signal.maximum,
                'unit': signal.unit or '',
                'receivers': signal.receivers,
            }
        
        mapping[message.name] = msg_entry
    
    # 顯示JSON
    json_str = json.dumps(mapping, indent=2)
    print("\n📋 訊號映射JSON:")
    print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
    
    # 儲存到文件
    output_file = Path(__file__).parent / 'signal_mapping.json'
    with open(output_file, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"\n✅ 已儲存到: {output_file}")
    
    return mapping


def main():
    dbc_file = Path(__file__).parent / 'Dashboard.dbc'
    
    if not dbc_file.exists():
        print(f"❌ DBC文件未找到: {dbc_file}")
        return
    
    # 執行分析
    db = analyze_dbc(str(dbc_file))
    
    # 示範編碼
    demonstrate_encoding(db)
    
    # 示範解碼
    demonstrate_decoding(db)
    
    # 匯出映射
    export_signal_mapping(db)
    
    print("\n" + "=" * 80)
    print("✅ 分析完成！")
    print("=" * 80)
    print("""
💡 關鍵學習點:

1. DBC格式定義CAN網路的靜態結構
   - 訊息 (messages): 由ECU週期发送
   - 訊號 (signals): 訊息內的具體資料欄位

2. 訊號轉換公式: 
   value = (raw_value * scale) + offset

3. 位元組順序 (Byte Order):
   - Motorola (Big Endian): MSB first, 常見於歐洲车企
   - Intel (Little Endian): LSB first, 常見於日系车企

4. 接收者 (Receivers):
   定義哪些ECU需要接收該訊號

5. 在儀表板中使用:
   - 解析DBC取得訊號定義
   - 從CAN資料解碼出人類可读的值
   - 顯示在QML UI上
""")


if __name__ == "__main__":
    main()
