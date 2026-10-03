import json
import os

CONFIG = os.path.join(os.path.dirname(__file__), "config.json")


def load_config():
    with open(CONFIG) as f:
        return json.load(f)


def run_stage(i, cfg):
    # every stage logs a lot of noise
    for j in range(150):
        print(f"[stage {i:03d}] step {j:03d} ok checksum={((i * 7919 + j * 104729) % 1000003):07d} WARN deprecated flag --legacy ignored")
    if i == cfg["checkpoint_stage"]:
        window = cfg["window"]
        if not isinstance(window, int):
            raise TypeError(f"stage {i}: window must be int, got {type(window).__name__} ({window!r})")
    return True


def main():
    cfg = load_config()
    for i in range(cfg["stages"]):
        run_stage(i, cfg)
    print("PIPELINE OK")


if __name__ == "__main__":
    main()
