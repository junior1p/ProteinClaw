#!/usr/bin/env python3
"""
RBX1 Binder Generation - Batch 1 (100 binders)
使用 BoltzGen 生成 alpha-rich binder

用法:
  python3 rbx1_boltzgen_batch1.py

参数已在脚本中预设，可根据需要修改。
"""

import modal
import os
import time
import json
from datetime import datetime
from pathlib import Path

# ============================================================================
# 配置参数
# ============================================================================

CONFIG = {
    # 目标结构
    "target_pdb": "rbx1_clean.pdb",
    
    # 生成参数
    "num_binders": 100,
    "binder_length_min": 90,
    "binder_length_max": 140,
    "topology": "alpha-rich",  # alpha-rich, beta-rich, mixed
    "temperature": 0.9,
    "batch_size": 4,
    "no_refine": True,  # True = 快速模式, False = 高质量模式
    
    # GPU 选择
    "preferred_gpu": "T4",  # T4 (最便宜) 或 L4 或 A100
    
    # 输出
    "output_dir": "out/boltzgen/rbx1_batch1",
}

# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 70)
    print("RBX1 Binder Generation - Batch 1")
    print("=" * 70)
    print()
    
    # 检查目标文件
    target_path = Path(CONFIG["target_pdb"])
    if not target_path.exists():
        print(f"❌ 错误: 未找到目标文件 {CONFIG['target_pdb']}")
        print(f"   当前目录: {os.getcwd()}")
        return 1
    
    print(f"✓ 目标结构: {CONFIG['target_pdb']}")
    print(f"  文件大小: {target_path.stat().st_size} bytes")
    print()
    
    # 显示参数
    print("📝 生成参数:")
    print("-" * 70)
    print(f"  Binder 数量:     {CONFIG['num_binders']}")
    print(f"  长度范围:        {CONFIG['binder_length_min']}-{CONFIG['binder_length_max']} aa")
    print(f"  拓扑结构:        {CONFIG['topology']}")
    print(f"  温度:            {CONFIG['temperature']}")
    print(f"  批次大小:        {CONFIG['batch_size']}")
    print(f"  精修模式:        {'关闭 (快速)' if CONFIG['no_refine'] else '开启 (高质量)'}")
    print(f"  优先 GPU:        {CONFIG['preferred_gpu']}")
    print()
    
    # 成本估算
    time_per_binder = 45  # 秒
    total_time_min = (CONFIG['num_binders'] * time_per_binder) / 60
    cost_t4_per_hour = 1.08
    estimated_cost = (total_time_min / 60) * cost_t4_per_hour
    
    print("💰 预估:")
    print("-" * 70)
    print(f"  时间:            ~{total_time_min:.1f} 分钟 ({total_time_min/60:.1f} 小时)")
    print(f"  成本:            ~${estimated_cost:.2f} (T4 GPU)")
    print()
    
    # 确认
    response = input("是否继续? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ 已取消")
        return 0
    
    print()
    print("🚀 开始生成...")
    print("=" * 70)
    print()
    
    # 创建输出目录
    output_dir = Path(CONFIG["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    start_time = time.time()
    
    try:
        # ====================================================================
        # 方式 1: 使用 Modal Function.lookup (如果知道函数名)
        # ====================================================================
        
        print("尝试方式 1: Modal Function.lookup")
        print("-" * 70)
        
        # 替换为实际的函数名
        # 常见可能: generate, predict, design_binder, run
        
        function_name = "generate"  # ⚠️ 需要替换为实际函数名
        
        try:
            func = modal.Function.lookup("boltzgen", function_name)
            print(f"✓ 找到函数: {function_name}")
            print()
            
            # 调用函数
            # 注意: 参数需要根据实际函数签名调整
            result = func.remote(
                target_pdb=str(target_path),
                num_designs=CONFIG["num_binders"],
                length_range=(CONFIG["binder_length_min"], CONFIG["binder_length_max"]),
                topology=CONFIG["topology"],
                temperature=CONFIG["temperature"],
                batch_size=CONFIG["batch_size"],
                no_refine=CONFIG["no_refine"],
            )
            
            print("✓ 生成完成!")
            print()
            print("结果:")
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(f"✗ 方式 1 失败: {e}")
            print()
            
            # ================================================================
            # 方式 2: 使用 modal run 命令行
            # ================================================================
            
            print("尝试方式 2: modal run 命令行")
            print("-" * 70)
            
            import subprocess
            
            cmd = [
                "modal", "run",
                "boltzgen.py::generate",  # ⚠️ 需要替换为实际路径和函数
                "--target-pdb", str(target_path),
                "--num-binders", str(CONFIG["num_binders"]),
                "--length-range", f"{CONFIG['binder_length_min']}-{CONFIG['binder_length_max']}",
                "--topology", CONFIG["topology"],
                "--temperature", str(CONFIG["temperature"]),
                "--batch-size", str(CONFIG["batch_size"]),
            ]
            
            if CONFIG["no_refine"]:
                cmd.append("--no-refine")
            
            print("执行命令:")
            print(" ".join(cmd))
            print()
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=total_time_min * 60 + 600  # 额外10分钟容错
            )
            
            if result.returncode == 0:
                print("✓ 生成完成!")
                print()
                print("输出:")
                print(result.stdout)
            else:
                print(f"✗ 命令执行失败 (返回码: {result.returncode})")
                print()
                print("错误信息:")
                print(result.stderr)
                return 1
    
    except KeyboardInterrupt:
        print()
        print("⚠️  用户中断")
        return 1
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        elapsed_time = time.time() - start_time
        print()
        print("=" * 70)
        print(f"⏱️  总耗时: {elapsed_time/60:.1f} 分钟")
        print("=" * 70)
    
    # 保存统计信息
    stats = {
        "config": CONFIG,
        "start_time": datetime.fromtimestamp(start_time).isoformat(),
        "end_time": datetime.now().isoformat(),
        "elapsed_seconds": elapsed_time,
        "elapsed_minutes": elapsed_time / 60,
        "estimated_cost": estimated_cost,
    }
    
    stats_file = output_dir / "batch1_stats.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"✓ 统计信息已保存: {stats_file}")
    
    return 0

if __name__ == "__main__":
    exit(main())
