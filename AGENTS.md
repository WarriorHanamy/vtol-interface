# Development Environment

The development OS is Arch Linux. ROS cannot be used natively and must run in Docker.

# Build Information

When you need compilation logs to decide next steps:

- Use `make docker-offload-build` to build in Docker
- Logs are written to `build/compile.log`
- Do NOT attempt native `colcon build` on Arch Linux

# LINT & FORMAT
## python codes

Run
```bash
uv run ruff check --fix .
```

Never use Optional for type hinting.
