"""Pytest configuration for Stockwell tests."""


def pytest_sessionfinish(session, exitstatus):
    """Clean up FFTW resources to avoid segfault at process exit."""
    try:
        from stockwell import st
        st.lib_st.st_cleanup()
    except Exception:
        pass
