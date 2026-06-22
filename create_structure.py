from pathlib import Path

# المجلدات الكاملة
dirs = [
    "config",
    "data/thread_colors",
    "data/machine_profiles",
    "data/training/my_dst_files",
    "data/training/models",
    "data/industry_specs",
    "infra/error_recovery",
    "layers/layer0_input",
    "layers/layer1_image",
    "layers/layer2_color",
    "layers/layer3_vector",
    "layers/layer4_digitizing",
    "layers/layer5_path",
    "layers/layer6_quality",
    "layers/layer7_output",
    "layers/layer8_ai",
    "bot",
    "feedback/grammar",
    "outputs",
    "samples",
    "tests",
    "notebooks",
]

# الملفات الفارغة (init + stubs)
files = [
    "config/__init__.py",
    "infra/__init__.py",
    "infra/error_recovery/__init__.py",
    "layers/__init__.py",
    "layers/layer0_input/__init__.py",
    "layers/layer1_image/__init__.py",
    "layers/layer2_color/__init__.py",
    "layers/layer3_vector/__init__.py",
    "layers/layer4_digitizing/__init__.py",
    "layers/layer5_path/__init__.py",
    "layers/layer6_quality/__init__.py",
    "layers/layer7_output/__init__.py",
    "layers/layer8_ai/__init__.py",
    "bot/__init__.py",
    "feedback/__init__.py",
    "feedback/grammar/__init__.py",
    "data/__init__.py",
]

# Stubs مؤقتة
stubs = {
    "layers/layer8_ai/region_desc.py": "# stub\ndef describe_regions(image): return {}\n",
    "feedback/style_learner.py": "# stub\ndef classify_style(features): return 'AUTO'\n",
    "feedback/grammar/grammar_learner.py": "# stub\ndef learn_grammar(patterns): return {}\n",
}

base = Path(".")

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)
    print(f"✅ مجلد: {d}")

for f in files:
    p = base / f
    if not p.exists():
        p.write_text("", encoding="utf-8")
        print(f"✅ ملف: {f}")

for path, content in stubs.items():
    p = base / path
    if not p.exists():
        p.write_text(content, encoding="utf-8")
        print(f"✅ stub: {path}")

print("\n✅ الهيكل مكتمل")
