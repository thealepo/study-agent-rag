from dotenv import load_dotenv

from study_agent.ui import build_demo


load_dotenv()


def main() -> None:
    demo = build_demo()
    demo.launch()


if __name__ == "__main__":
    main()
