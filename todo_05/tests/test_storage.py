def test_storage_module_importable():
    # Skeleton test: ensure storage module can be imported
    from src.services import storage
    assert hasattr(storage, 'insert_task')
