from app.conversation import ConversationMemory


def test_conversation_memory(tmp_path):

    memory = ConversationMemory(
        max_history=2
    )

    memory.memory_dir = str(tmp_path)
    memory.memory_file = str(
        tmp_path / "conversation.json"
    )

    memory.add_conversation(
        "How is authentication handled?",
        "Authentication is handled through the login system."
    )

    result = memory.get_memory()

    assert "How is authentication handled?" in result
    assert "login system" in result