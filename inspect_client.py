
import valclient
import inspect

print("Methods in valclient.Client:")
for name, method in inspect.getmembers(valclient.Client, predicate=inspect.isfunction):
    print(name)
