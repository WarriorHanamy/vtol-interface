.PHONY: build

TMP_SRC := /tmp/vtol-interface-src

build:
	@echo ">>> Copying src to $(TMP_SRC)..."
	@rm -rf $(TMP_SRC)
	@cp -r src $(TMP_SRC)
	docker compose run --rm \
		-v $(TMP_SRC):/home/ros/ros2_ws/src \
		ros2 bash -c "cp -r src/px4_msgs/msg/versioned/* src/px4_msgs/msg/ && source /opt/ros/humble/setup.bash && colcon build"

# =============================================================================
# Submodule Sync
# =============================================================================

.PHONY: sync-msg-submodule

REF_NEUPILOT_REMOTE ?= https://github.com/WarriorHanamy/PX4-Neupilot.git
MSG_SUBMODULE_PATH := src/px4_msgs/msg

sync-msg-submodule:
	@echo ">>> Syncing msg submodule to ref-neupilot..."
	@if ! git remote | grep -q '^ref-neupilot$$'; then \
		echo ">>> Adding ref-neupilot remote..."; \
		git remote add ref-neupilot $(REF_NEUPILOT_REMOTE); \
	fi
	@echo ">>> Fetching ref-neupilot..."
	git fetch ref-neupilot
	@MSG_COMMIT=$$(git ls-tree ref-neupilot/main msg | awk '{print $$3}'); \
	MSG_URL=$$(git show ref-neupilot/main:.gitmodules | grep -A3 '\[submodule "msg"\]' | grep 'url' | sed 's/.*= *//'); \
	echo ">>> Target commit: $$MSG_COMMIT"; \
	echo ">>> Target URL: $$MSG_URL"; \
	echo ">>> Updating submodule remote URL..."; \
	cd $(MSG_SUBMODULE_PATH) && git remote set-url origin $$MSG_URL && git fetch origin && git checkout $$MSG_COMMIT; \
	cd $(CURDIR) && git config -f .gitmodules submodule.$(MSG_SUBMODULE_PATH).url "$$MSG_URL"; \
	cd $(CURDIR) && git config submodule.$(MSG_SUBMODULE_PATH).url "$$MSG_URL"; \
	echo ">>> Submodule synced. Changes to commit:"; \
	git status --short $(MSG_SUBMODULE_PATH) .gitmodules

# =============================================================================
# Simulation Environment (tmux + docker compose)
# =============================================================================

.PHONY: sim sim-kill

TMUX_SESSION := vtol-sim

sim: sim-kill
	@which tmux >/dev/null || { echo "Error: tmux not installed"; exit 1; }
	@echo ">>> Starting simulation session: $(TMUX_SESSION)"
	tmux new-session -d -s $(TMUX_SESSION) -n sim -x 200 -y 50
	tmux send-keys -t $(TMUX_SESSION) 'docker compose up -d px4 qgc && docker compose attach ros2; docker compose down; tmux kill-session -t $(TMUX_SESSION)' C-m
	tmux attach -t $(TMUX_SESSION)

sim-kill:
	@echo ">>> Killing session: $(TMUX_SESSION)"
	tmux kill-session -t $(TMUX_SESSION) 2>/dev/null || echo "Session not found or already dead"

# =============================================================================
# Neural Services Management (systemd user services)
# =============================================================================

.PHONY: install neural-start neural-stop neural-status logs logs-web

install:
	@echo ">>> Installing neural services (neural_executor, neural_infer)..."
	@if [ "$(shell id -u)" -eq 0 ]; then \
		echo "Error: This target should NOT be run as root"; \
		echo "User services must be installed for the current user"; \
		exit 1; \
	fi
	@./install-neural-services.sh

neural-start:
	@echo ">>> Checking if ros2 container is running (required for neural services)..."
	@if ! docker ps --filter "name=ros2" --format "{{.Names}}" | grep -q .; then \
		echo "Error: ros2 container not found"; \
		echo ""; \
		echo "neural services require the ros2 container to be running."; \
		echo "Please run 'make sim' first to start the simulation environment."; \
		echo ""; \
		echo "Usage:"; \
		echo "  1. Run 'make sim' to start simulation (creates ros2 container)"; \
		echo "  2. Then run 'make neural-start' to start neural services"; \
		exit 1; \
	fi
	@echo ">>> ros2 container found, starting neural services..."
	@systemctl --user enable neural_executor.service neural_infer.service
	@systemctl --user start neural_executor.service neural_infer.service || true
	@echo ">>> Neural services started successfully"

neural-stop:
	@echo ">>> Stopping neural services..."
	@systemctl --user stop neural_executor.service neural_infer.service || true
	@echo ">>> Neural services stopped"

neural-status:
	@echo ">>> Checking neural services status..."
	@echo ""
	@systemctl --user status neural_executor.service --no-pager || true
	@echo ""
	@systemctl --user status neural_infer.service --no-pager || true

logs:
	@echo ">>> Streaming neural services logs (press Ctrl+C to exit)..."
	@echo ""
	@journalctl --user -u neural_executor.service -u neural_infer.service -f

logs-web:
	@echo ">>> Log streamer web endpoints (requires log_streamer service to be running):"
	@echo ""
	@echo "Neural Executor logs:   http://localhost:8000/logs/neural_executor"
	@echo "Neural Inference logs:  http://localhost:8000/logs/neural_infer"
	@echo "Merged logs:            http://localhost:8000/logs/merged"
	@echo "Service status:         http://localhost:8000/status"
	@echo "Health check:           http://localhost:8000/health"
	@echo ""
	@echo "To start log_streamer service:"
	@echo "  docker compose up -d log_streamer"
	@echo ""
	@echo "To stop log_streamer service:"
	@echo "  docker compose stop log_streamer"
