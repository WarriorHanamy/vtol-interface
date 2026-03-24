# Known Problems

## [2026-03-24] neural_infer 启动失败 - 缺少 transforms 模块

**错误**:
```
ModuleNotFoundError: No module named 'transforms'
```
在 `control/action_post_processor.py:20` 导入 `from transforms.math_utils import frd_flu_rotate` 时失败。

**相关文件**:
- `src/neural_manager/neural_inference/control/action_post_processor.py:20`
- `~/.config/systemd/user/neural_infer.service`

**状态**: 未解决
