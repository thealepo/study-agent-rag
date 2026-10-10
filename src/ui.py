from __future__ import annotations

from typing import Any

import gradio as gr

from .agent import (
    DEFAULT_MODEL,
    create_client,
    study_agent,
)

from .rag import (
    build_knowledge_base,
    load_embedding_model,
)


CSS = """
#title {
    text-align: center;
    margin-bottom: 0;
}

#subtitle {
    text-align: center;
    opacity: 0.72;
    margin-bottom: 18px;
}

#sidebar {
    padding: 8px;
}
"""


def build_demo(
    model_name: str = DEFAULT_MODEL,
) -> gr.Blocks:
    """Build the Gradio application."""

    embedding_model = (
        load_embedding_model()
    )

    client = create_client()

    def process_pdf(
        file_path: str | None
    ):
        if not file_path:
            return (
                "Please upload a PDF first.",
                None,
                [],
            )

        try:
            knowledge_base = (
                build_knowledge_base(
                    file_path,
                    embedding_model,
                )
            )

        except Exception as exc:
            return (
                f"Could not process this PDF: {exc}",
                None,
                [],
            )

        status = (
            "**Notes are ready!**  \n"
            f"**File:** {knowledge_base['filename']}  \n"
            f"**Pages:** {knowledge_base['pages']}  \n"
            f"**Chunks:** {len(knowledge_base['chunks'])}"
        )

        # New PDF = new study session
        return (
            status,
            knowledge_base,
            [],
        )

    def respond(
        message: str,
        history: list[dict[str, Any]] | None,
        knowledge_base: dict[str, Any] | None,
    ):
        history = history or []

        if not message or not message.strip():
            return "", history

        if not knowledge_base:
            response = (
                "Please upload and process your PDF "
                "before starting a study session."
            )

        else:
            try:
                response = study_agent(
                    query=message,
                    history=history,
                    knowledge_base=knowledge_base,
                    embedding_model=embedding_model,
                    client=client,
                    model_name=model_name,
                )

            except Exception as exc:
                response = (
                    f"Something went wrong: {exc}"
                )

        history = history + [
            {
                "role": "user",
                "content": message,
            },
            {
                "role": "assistant",
                "content": response,
            },
        ]

        return "", history

    with gr.Blocks(
        theme=gr.themes.Soft(),
        css=CSS,
    ) as demo:

        knowledge_base_state = (
            gr.State(None)
        )

        gr.Markdown(
            "# 📚 StudyAgent",
            elem_id="title",
        )

        gr.Markdown(
            "Upload your class notes and study "
            "with your own AI tutor.",
            elem_id="subtitle",
        )

        with gr.Row():

            with gr.Column(
                scale=1,
                min_width=300,
                elem_id="sidebar",
            ):

                gr.Markdown(
                    "### Course Material"
                )

                pdf_upload = gr.File(
                    label="Upload your notes",
                    file_types=[".pdf"],
                    type="filepath",
                )

                process_button = gr.Button(
                    "Process Notes",
                    variant="primary",
                )

                status = gr.Markdown(
                    "Upload a PDF to get started."
                )

                gr.Markdown(
                    "**Try:** lecture slides, class notes, "
                    "textbook chapters, or a study guide."
                )

            with gr.Column(scale=2):

                gr.Markdown(
                    "### Study Session"
                )

                chatbot = gr.Chatbot(
                    height=500,
                    type="messages",
                    placeholder=(
                        "<strong>StudyAgent</strong><br>"
                        "Process your notes, then ask me "
                        "anything or say <em>Quiz me!</em>"
                    ),
                )

                message = gr.Textbox(
                    placeholder=(
                        'Ask a question or say "Quiz me!"'
                    ),
                    label="Message",
                    lines=2,
                )

                with gr.Row():

                    send_button = gr.Button(
                        "Send",
                        variant="primary",
                    )

                    clear_button = gr.Button(
                        "Clear Chat"
                    )

        process_button.click(
            fn=process_pdf,
            inputs=pdf_upload,
            outputs=[
                status,
                knowledge_base_state,
                chatbot,
            ],
        )

        send_button.click(
            fn=respond,
            inputs=[
                message,
                chatbot,
                knowledge_base_state,
            ],
            outputs=[
                message,
                chatbot,
            ],
        )

        message.submit(
            fn=respond,
            inputs=[
                message,
                chatbot,
                knowledge_base_state,
            ],
            outputs=[
                message,
                chatbot,
            ],
        )

        clear_button.click(
            fn=lambda: ("", []),
            outputs=[
                message,
                chatbot,
            ],
        )

    return demo
