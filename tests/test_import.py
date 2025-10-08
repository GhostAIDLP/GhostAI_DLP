"""
Test that the ghostai package can be imported successfully.
"""

def test_import_ghostai():
    """Test that import ghostai works without errors."""
    import ghostai
    assert hasattr(ghostai, 'Pipeline')
    assert hasattr(ghostai, 'GhostAIProxy')
    assert hasattr(ghostai, 'normalize_text')

def test_pipeline_import():
    """Test that Pipeline can be imported and instantiated."""
    from ghostai.pipeline.pipeline import Pipeline
    pipeline = Pipeline()
    assert pipeline is not None

def test_proxy_import():
    """Test that GhostAIProxy can be imported and instantiated."""
    from ghostai.proxy_api.proxy import GhostAIProxy
    proxy = GhostAIProxy()
    assert proxy is not None
