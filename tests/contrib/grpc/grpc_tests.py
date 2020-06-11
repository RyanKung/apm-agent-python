import time
from concurrent import futures
from elasticapm.contrib.grpcio import RequestHeaderValidatorInterceptor
import pytest

grpc = pytest.importorskip("grpc")  # isort:skip
from tests.contrib.grpc import helloworld_pb2
from tests.contrib.grpc.server import Greeter
from tests.contrib.grpc import helloworld_pb2
from tests.contrib.grpc import helloworld_pb2_grpc

port = 8964

class Greeter(helloworld_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message="Hello, %s!" % request.name)


@pytest.fixture()
def interceptor(elasticapm_client):
    ELASTIC_APM_CONFIG = {
        "SERVICE_NAME": "grpcapp",
        "SECRET_TOKEN": "changeme",
    }
    return RequestHeaderValidatorInterceptor(
        config=ELASTIC_APM_CONFIG,
        client=elasticapm_client
    )

@pytest.fixture()
def apm_client(interceptor):
    return interceptor.client


@pytest.fixture()
def grpc_server(request, interceptor):
    ELASTIC_APM_CONFIG = {
            "SERVICE_NAME": "grpcapp",
            "SECRET_TOKEN": "changeme",
            "ELASTIC_APM_SERVICE_NAME": "127.0.0.1"
        }
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=(
            interceptor,
        )
    )
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    request.addfinalizer(lambda : server.stop(None))


def test_server(grpc_server, apm_client):
    with grpc.insecure_channel(f"localhost:{port}") as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(helloworld_pb2.HelloRequest(name="Jack"))
    assert response.message == "Hello, Jack!"
