# Regenerates all generated files in the Python examples directory.

ARTIFACTS=

ARTIFACTS += python/generated/config_pb2.py
ARTIFACTS += python/generated/config_pb2_grpc.py
ARTIFACTS += python/generated/config_pb2.pyi

ARTIFACTS += python/generated/misc_pb2.py
ARTIFACTS += python/generated/misc_pb2_grpc.py
ARTIFACTS += python/generated/misc_pb2.pyi

ARTIFACTS += python/generated/dating_server_pb2.py
ARTIFACTS += python/generated/dating_server_pb2_grpc.py
ARTIFACTS += python/generated/dating_server_pb2.pyi

ARTIFACTS += python/generated/user_pb2.py
ARTIFACTS += python/generated/user_pb2_grpc.py
ARTIFACTS += python/generated/user_pb2.pyi

.PHONY: all
all: ${ARTIFACTS}

python/generated/config_pb2.py python/generated/config_pb2_grpc.py python/generated/config_pb2.pyi: protos/config.proto
	python3 -m grpc_tools.protoc --python_out=python/generated --grpc_python_out=python/generated --pyi_out=python/generated -I protos protos/config.proto

python/generated/misc_pb2.py python/generated/misc_pb2_grpc.py python/generated/misc_pb2.pyi: protos/misc.proto
	python3 -m grpc_tools.protoc --python_out=python/generated --grpc_python_out=python/generated --pyi_out=python/generated -I protos protos/misc.proto

python/generated/dating_server_pb2.py python/generated/dating_server_pb2_grpc.py python/generated/dating_server_pb2.pyi: protos/dating_server.proto
	python3 -m grpc_tools.protoc --python_out=python/generated --grpc_python_out=python/generated --pyi_out=python/generated -I protos protos/dating_server.proto

python/generated/user_pb2.py python/generated/user_pb2_grpc.py python/generated/user_pb2.pyi: protos/user.proto
	python3 -m grpc_tools.protoc --python_out=python/generated --grpc_python_out=python/generated --pyi_out=python/generated -I protos protos/user.proto


.PHONY: clean
clean:
	rm -f ${ARTIFACTS}
