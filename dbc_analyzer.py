#!/usr/bin/env python3
"""
DBC解析和转换工具 - 详细演示cantools库的功能
用于理解DBC的结构和信号转换
"""

import cantools
import json
from pathlib import Path


def analyze_dbc(dbc_file: str):
    """详细分析DBC文件"""
    
    print("=" * 80)
    print("🔍 DBC文件详细分析")
    print("=" * 80)
    
    db = cantools.database.load_file(dbc_file)
    
    print(f"\n📄 文件: {dbc_file}")
    print(f"📊 总消息数: {len(db.messages)}")
    print(f"🔌 ECU节点: {len(db.nodes)} - {', '.join([n.name for n in db.nodes])}")
    
    # 详细信息
    print(f"\n{'消息名':<20} {'ID':<8} {'DLC':<6} {'周期':<8} {'信号数':<8}")
    print("-" * 80)
    
    for message in db.messages:
        cycle_time = message.cycle_time or 0
        print(f"{message.name:<20} {f'0x{message.frame_id:X}':<8} {message.length:<6} {cycle_time:<8}ms {len(message.signals):<8}")
        
        # 显示信号详情
        for signal in message.signals:
            scale = signal.scale if signal.scale != 1 else ""
            offset = signal.offset if signal.offset != 0 else ""
            
            print(f"  └─ {signal.name:<18} [{signal.start}:{signal.length}] "
                  f"min={signal.minimum:<8} max={signal.maximum:<8} "
                  f"unit={signal.unit or 'N/A':<8}")
            
            if signal.receivers:
                print(f"     ├─ 接收者: {', '.join(signal.receivers)}")
            
            if scale or offset:
                print(f"     └─ 转换: value = raw * {scale} + {offset}")
    
    print("\n" + "=" * 80)
    return db


def demonstrate_encoding(db):
    """演示信号编码"""
    
    print("\n" + "=" * 80)
    print("📝 信号编码演示 - 如何将数据编码为CAN消息")
    print("=" * 80)
    
    # 获取EngineStatus消息
    msg = db.get_message_by_name('EngineStatus')
    
    print(f"\n消息: {msg.name} (ID: 0x{msg.frame_id:X})")
    print("-" * 80)
    
    # 准备信号数据
    signals = {
        'EngineRPM': 1500,        # rpm
        'EngineTemp': 85,         # °C
        'FuelLevel': 90,          # %
        'BatteryVoltage': 13.5,   # V
    }
    
    print("\n📤 输入信号值:")
    for name, value in signals.items():
        signal = msg.get_signal_by_name(name)
        print(f"  {name:<20} = {value:<10} {signal.unit}")
    
    # 编码
    encoded_data = msg.encode(signals)
    print(f"\n✅ 编码后的原始数据 (hex): {encoded_data.hex().upper()}")
    print(f"   二进制: {' '.join(format(b, '08b') for b in encoded_data)}")
    
    # 解码验证
    decoded = msg.decode(encoded_data)
    print(f"\n🔄 解码验证:")
    for name, value in decoded.items():
        signal = msg.get_signal_by_name(name)
        original = signals.get(name)
        match = "✅" if abs(value - original) < 0.1 else "⚠️"
        print(f"  {match} {name:<20} = {value:<10.2f} (原值: {original})")


def demonstrate_decoding(db):
    """演示信号解码"""
    
    print("\n" + "=" * 80)
    print("📖 信号解码演示 - 如何从CAN消息提取数据")
    print("=" * 80)
    
    msg = db.get_message_by_name('VehicleStatus')
    
    print(f"\n消息: {msg.name} (ID: 0x{msg.frame_id:X})")
    print("-" * 80)
    
    # 模拟CAN原始数据
    raw_data = bytes([0x5A, 0x00, 0x03, 0x00, 0x64, 0x00, 0x16, 0x00])
    
    print(f"\n📥 接收的原始数据 (hex): {raw_data.hex().upper()}")
    print(f"   二进制: {' '.join(format(b, '08b') for b in raw_data)}")
    
    # 解码
    decoded = msg.decode(raw_data)
    
    print(f"\n✅ 解码后的信号值:")
    for name, value in decoded.items():
        signal = msg.get_signal_by_name(name)
        print(f"  {name:<20} = {value:<10.2f} {signal.unit}")


def export_signal_mapping(db):
    """导出信号映射为JSON"""
    
    print("\n" + "=" * 80)
    print("💾 导出信号映射 - 用于前端显示")
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
    
    # 显示JSON
    json_str = json.dumps(mapping, indent=2)
    print("\n📋 信号映射JSON:")
    print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
    
    # 保存到文件
    output_file = Path(__file__).parent / 'signal_mapping.json'
    with open(output_file, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"\n✅ 已保存到: {output_file}")
    
    return mapping


def main():
    dbc_file = Path(__file__).parent / 'Dashboard.dbc'
    
    if not dbc_file.exists():
        print(f"❌ DBC文件未找到: {dbc_file}")
        return
    
    # 运行分析
    db = analyze_dbc(str(dbc_file))
    
    # 演示编码
    demonstrate_encoding(db)
    
    # 演示解码
    demonstrate_decoding(db)
    
    # 导出映射
    export_signal_mapping(db)
    
    print("\n" + "=" * 80)
    print("✅ 分析完成！")
    print("=" * 80)
    print("""
💡 关键学习点:

1. DBC格式定义CAN网络的静态结构
   - 消息 (messages): 由ECU周期发送
   - 信号 (signals): 消息内的具体数据字段

2. 信号转换公式: 
   value = (raw_value * scale) + offset

3. 字节顺序 (Byte Order):
   - Motorola (Big Endian): MSB first, 常见于欧洲车企
   - Intel (Little Endian): LSB first, 常见于日系车企

4. 接收者 (Receivers):
   定义哪些ECU需要接收该信号

5. 在仪表板中使用:
   - 解析DBC获取信号定义
   - 从CAN数据解码出人类可读的值
   - 显示在QML UI上
""")


if __name__ == "__main__":
    main()
