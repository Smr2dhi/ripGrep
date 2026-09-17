from backend.context_retrieval import get_context


def test_get_context_with_matching_lines(tmp_path, monkeypatch):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    auth_file = documents_dir / "auth.txt"

    auth_file.write_text(
        "User Authentication\n"
        "Users log in with username and password.\n"
        "The server generates a JWT token.\n"
        "The verify_token function checks the token.\n"
        "Expired tokens are rejected.\n"
        "Valid tokens allow access.\n"
        "Authentication middleware protects endpoints.\n",
        encoding="utf-8"
    )

    monkeypatch.setattr(
        "app.context_retrieval.DOCUMENTS_DIR",
        str(documents_dir)
    )

    grep_result = (
        "auth.txt:4:The verify_token function checks the token."
    )

    result = get_context(
        grep_result,
        context_lines=2
    )

    assert "auth.txt:2:Users log in with username and password." in result
    assert "auth.txt:3:The server generates a JWT token." in result
    assert "auth.txt:4:The verify_token function checks the token." in result
    assert "auth.txt:5:Expired tokens are rejected." in result
    assert "auth.txt:6:Valid tokens allow access." in result


def test_get_context_with_no_grep_result():
    result = get_context("")

    assert result == "NO matching information found."


def test_get_context_with_none():
    result = get_context(None)

    assert result == "NO matching information found."


def test_get_context_ignores_invalid_grep_lines(tmp_path, monkeypatch):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    auth_file = documents_dir / "auth.txt"

    auth_file.write_text(
        "Authentication\n"
        "JWT token is generated after login.\n"
        "Token is verified.\n",
        encoding="utf-8"
    )

    monkeypatch.setattr(
        "app.context_retrieval.DOCUMENTS_DIR",
        str(documents_dir)
    )

    grep_result = (
        "invalid line\n"
        "auth.txt:abc:Invalid line number\n"
        "auth.txt:2:JWT token is generated after login."
    )

    result = get_context(
        grep_result,
        context_lines=0
    )

    assert "auth.txt:2:JWT token is generated after login." in result
    assert "invalid line" not in result


def test_get_context_removes_duplicate_line_numbers(tmp_path, monkeypatch):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    auth_file = documents_dir / "auth.txt"

    auth_file.write_text(
        "Authentication\n"
        "JWT token is generated.\n"
        "Token is verified.\n",
        encoding="utf-8"
    )

    monkeypatch.setattr(
        "app.context_retrieval.DOCUMENTS_DIR",
        str(documents_dir)
    )

    grep_result = (
        "auth.txt:2:JWT token is generated.\n"
        "auth.txt:2:JWT token is generated.\n"
        "auth.txt:2:JWT token is generated."
    )

    result = get_context(
        grep_result,
        context_lines=0
    )

    assert result.count("auth.txt:2:JWT token is generated.") == 1


def test_get_context_reads_multiple_files(tmp_path, monkeypatch):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    auth_file = documents_dir / "auth.txt"
    login_file = documents_dir / "login.txt"

    auth_file.write_text(
        "Authentication system\n"
        "JWT token is used.\n",
        encoding="utf-8"
    )

    login_file.write_text(
        "Login system\n"
        "Users provide username and password.\n",
        encoding="utf-8"
    )

    monkeypatch.setattr(
        "app.context_retrieval.DOCUMENTS_DIR",
        str(documents_dir)
    )

    grep_result = (
        "auth.txt:2:JWT token is used.\n"
        "login.txt:2:Users provide username and password."
    )

    result = get_context(
        grep_result,
        context_lines=0
    )

    assert "auth.txt:2:JWT token is used." in result
    assert "login.txt:2:Users provide username and password." in result


def test_get_context_handles_missing_file(tmp_path, monkeypatch):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    monkeypatch.setattr(
        "app.context_retrieval.DOCUMENTS_DIR",
        str(documents_dir)
    )

    grep_result = (
        "missing.txt:2:Some information"
    )

    result = get_context(
        grep_result,
        context_lines=0
    )

    assert result == "NO matching information found."


def test_get_context_respects_max_chars(tmp_path, monkeypatch):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    auth_file = documents_dir / "auth.txt"

    auth_file.write_text(
        "Authentication\n"
        "JWT token information is available here.\n"
        "Users must provide valid credentials.\n"
        "The authentication middleware verifies requests.\n"
        "Expired tokens are rejected.\n"
        "Protected endpoints require authentication.\n",
        encoding="utf-8"
    )

    monkeypatch.setattr(
        "app.context_retrieval.DOCUMENTS_DIR",
        str(documents_dir)
    )

    grep_result = (
        "auth.txt:2:JWT token information is available here."
    )

    result = get_context(
        grep_result,
        context_lines=5,
        max_chars=100
    )

    assert len(result) <= 100


def test_get_context_with_separate_match_ranges(tmp_path, monkeypatch):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    auth_file = documents_dir / "auth.txt"

    lines = [
        "Line 1\n",
        "Authentication starts here.\n",
        "Line 3\n",
        "Line 4\n",
        "Line 5\n",
        "Line 6\n",
        "Line 7\n",
        "Line 8\n",
        "Line 9\n",
        "Line 10\n",
        "Line 11\n",
        "Line 12\n",
        "Line 13\n",
        "Line 14\n",
        "Line 15\n",
        "Line 16\n",
        "Line 17\n",
        "Line 18\n",
        "Line 19\n",
        "Token validation happens here.\n",
    ]

    auth_file.write_text(
        "".join(lines),
        encoding="utf-8"
    )

    monkeypatch.setattr(
        "app.context_retrieval.DOCUMENTS_DIR",
        str(documents_dir)
    )

    grep_result = (
        "auth.txt:2:Authentication starts here.\n"
        "auth.txt:20:Token validation happens here."
    )

    result = get_context(
        grep_result,
        context_lines=1
    )

    assert "auth.txt:1:Line 1" in result
    assert "auth.txt:2:Authentication starts here." in result
    assert "auth.txt:3:Line 3" in result

    assert "auth.txt:19:Line 19" in result
    assert "auth.txt:20:Token validation happens here." in result


def test_get_context_does_not_go_before_first_line(tmp_path, monkeypatch):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    auth_file = documents_dir / "auth.txt"

    auth_file.write_text(
        "Authentication\n"
        "JWT token is used.\n"
        "Token is verified.\n",
        encoding="utf-8"
    )

    monkeypatch.setattr(
        "app.context_retrieval.DOCUMENTS_DIR",
        str(documents_dir)
    )

    grep_result = (
        "auth.txt:1:Authentication"
    )

    result = get_context(
        grep_result,
        context_lines=5
    )

    assert "auth.txt:1:Authentication" in result
    assert "auth.txt:2:JWT token is used." in result
    assert "auth.txt:3:Token is verified." in result


def test_get_context_does_not_go_after_last_line(tmp_path, monkeypatch):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    auth_file = documents_dir / "auth.txt"

    auth_file.write_text(
        "Authentication\n"
        "JWT token is used.\n"
        "Token is verified.\n",
        encoding="utf-8"
    )

    monkeypatch.setattr(
        "app.context_retrieval.DOCUMENTS_DIR",
        str(documents_dir)
    )

    grep_result = (
        "auth.txt:3:Token is verified."
    )

    result = get_context(
        grep_result,
        context_lines=5
    )

    assert "auth.txt:1:Authentication" in result
    assert "auth.txt:2:JWT token is used." in result
    assert "auth.txt:3:Token is verified." in result



    """
    Result:-
    ========================== test session starts ===========================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\pc\Desktop\ripGrep\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\pc\Desktop\ripGrep
plugins: anyio-4.15.1
collected 11 items                                                        

tests/test_context_retrieval.py::test_get_context_with_matching_lines PASSED [  9%]
tests/test_context_retrieval.py::test_get_context_with_no_grep_result PASSED [ 18%]
tests/test_context_retrieval.py::test_get_context_with_none PASSED  [ 27%]
tests/test_context_retrieval.py::test_get_context_ignores_invalid_grep_lines PASSED [ 36%]
tests/test_context_retrieval.py::test_get_context_removes_duplicate_line_numbers PASSED [ 45%]
tests/test_context_retrieval.py::test_get_context_reads_multiple_files PASSED [ 54%]
tests/test_context_retrieval.py::test_get_context_handles_missing_file PASSED [ 63%]
tests/test_context_retrieval.py::test_get_context_respects_max_chars PASSED [ 72%]
tests/test_context_retrieval.py::test_get_context_with_separate_match_ranges PASSED [ 81%]
tests/test_context_retrieval.py::test_get_context_does_not_go_before_first_line PASSED [ 90%]
tests/test_context_retrieval.py::test_get_context_does_not_go_after_last_line PASSED [100%]

=========================== 11 passed in 0.22s ===========================

(.venv) C:\Users\pc\Desktop\ripGrep>





    """