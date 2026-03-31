from common.core.database import SessionLocal
from apps.simulator.engine.topology_generator import TopologyGenerator
from apps.simulator.engine.log_generator import LogGenerator
from apps.simulator.models import SimulationEnvironment, SimulationComponent, ComponentRelation

db = SessionLocal()

print("=" * 60)
print("日志联动机制测试")
print("=" * 60)

print("\n1. 创建测试环境...")
generator = TopologyGenerator(db)
try:
    result = generator.generate(
        name='日志联动测试环境',
        topology_type='standard',
        scale='small',
        ip_prefix='10.0.1',
        description='用于验证日志联动机制的测试环境',
        pushgateway_url='http://localhost:9091',
        log_path='simulator/logs',
    )
    env_id = result['environment']['id']
    print(f'   环境创建成功! ID: {env_id}')
    print(f'   组件数: {len(result["components"])}')
    print(f'   关系数: {len(result["relations"])}')
except Exception as e:
    print(f'   创建失败: {e}')
    import traceback
    traceback.print_exc()
    db.close()
    exit(1)

print("\n2. 查看组件和关系...")
components = db.query(SimulationComponent).filter(SimulationComponent.env_id == env_id).all()
relations = db.query(ComponentRelation).filter(ComponentRelation.env_id == env_id).all()

print(f"   组件列表 ({len(components)} 个):")
for comp in components:
    print(f"   - {comp.name} ({comp.component_type})")

print(f"\n   关系列表 ({len(relations)} 条):")
for rel in relations:
    source = db.query(SimulationComponent).filter(SimulationComponent.id == rel.source_id).first()
    target = db.query(SimulationComponent).filter(SimulationComponent.id == rel.target_id).first()
    print(f"   - {source.name} -> {target.name} ({rel.relation_type})")

print("\n3. 生成日志...")
log_gen = LogGenerator(db, 'simulator/logs')
log_gen.generate_and_write(env_id)
print("   日志生成完成!")

print("\n4. 检查日志文件内容...")
import os

log_dirs = ['nginx', 'app', 'database', 'cache', 'client', 'gateway']
found_logs = []

for dir_name in log_dirs:
    dir_path = os.path.join('simulator/logs', dir_name)
    if os.path.exists(dir_path):
        for filename in os.listdir(dir_path):
            if filename.endswith('.log'):
                filepath = os.path.join(dir_path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        found_logs.append((filepath, len(lines), lines[-3:]))

print(f"\n   找到 {len(found_logs)} 个日志文件:")
for filepath, count, sample_lines in found_logs:
    print(f"\n   [{filepath}] ({count} 行)")
    print("   最近3行:")
    for line in sample_lines:
        print(f"   {line.strip()[:120]}...")

print("\n5. 验证 trace_id 联动...")
trace_ids = {}
for filepath, count, sample_lines in found_logs:
    for line in sample_lines:
        if 'trace_id' in line or 'trace:' in line:
            import re
            match = re.search(r'trace[_:]?\s*["\']?([A-F0-9]{16})', line, re.IGNORECASE)
            if match:
                trace_id = match.group(1).upper()
                if trace_id not in trace_ids:
                    trace_ids[trace_id] = []
                trace_ids[trace_id].append(filepath)

print(f"\n   找到 {len(trace_ids)} 个唯一 trace_id:")
for trace_id, files in list(trace_ids.items())[:3]:
    print(f"\n   trace_id: {trace_id}")
    print(f"   出现在 {len(files)} 个文件中:")
    for f in files:
        print(f"   - {f}")

if len(trace_ids) > 0:
    max_files = max(len(files) for files in trace_ids.values())
    if max_files >= 2:
        print(f"\n   ✓ 日志联动验证成功! 同一 trace_id 出现在多个组件日志中")
    else:
        print(f"\n   ⚠ 警告: trace_id 仅出现在单个组件日志中")
else:
    print(f"\n   ✗ 未找到 trace_id，联动验证失败")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

db.close()
