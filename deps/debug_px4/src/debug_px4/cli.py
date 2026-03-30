import argparse

from debug_px4.subscriber import ZenohSubscriber
from debug_px4.topics import get_topic_handler
from debug_px4.viz.plot import RealTimePlot


def main():
    parser = argparse.ArgumentParser(description="PX4 Zenoh debug subscriber")
    parser.add_argument("--topic", "-t", default="neupilot/debug/acc_rates_control", help="Zenoh keyexpr")
    parser.add_argument("--mode", "-m", default="peer", choices=["peer", "client"], help="Zenoh mode")
    parser.add_argument("--locator", "-l", default="", help="Zenoh locator (e.g., tcp/127.0.0.1:7447)")
    parser.add_argument("--plot", "-p", action="store_true", help="Enable matplotlib visualization")
    args = parser.parse_args()

    handler = get_topic_handler(args.topic)
    if handler is None:
        print(f"Unknown topic: {args.topic}")
        return 1

    if args.plot:
        plot = RealTimePlot(handler)
        with ZenohSubscriber() as sub:
            sub.connect(mode=args.mode, locator=args.locator)
            sub.subscribe(args.topic, plot.on_data)
            plot.show()
    else:

        def _print(data: bytes):
            msg = handler.decode(data)
            print(msg)

        with ZenohSubscriber() as sub:
            sub.connect(mode=args.mode, locator=args.locator)
            sub.subscribe(args.topic, _print)
            input("Press Enter to exit...")

    return 0


if __name__ == "__main__":
    exit(main())
