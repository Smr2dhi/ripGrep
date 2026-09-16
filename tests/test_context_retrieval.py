from app.context_retrieval import get_context


def test_get_context():

    grep_result = """
auth.txt:1:User authentication is handled through the login system.
auth.txt:3:The verify_token method checks the authentication token.
"""

    context = get_context(
        grep_result
    )

    assert "authentication" in context
    assert "verify_token" in context
    assert "auth.txt" in context