from app.core.test_task import add

result = add.apply_async((2, 3))
print("Waiting for result...")
print(result.get(timeout=10))
