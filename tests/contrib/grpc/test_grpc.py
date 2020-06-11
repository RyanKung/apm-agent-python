import grpc
import grpc_testing
import unittest
import time
from concurrent import futures
from elasticapm.contrib.grpcio import RequestHeaderValidatorInterceptor
from tests.contrib.grpc import helloworld_pb2
from tests.contrib.grpc.server import Greeter
from tests.contrib.grpc import helloworld_pb2
from tests.contrib.grpc import helloworld_pb2_grpc

class Greeter(helloworld_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)



class RPCGreeterServerTest(unittest.TestCase):
    server_class = Greeter
    port = 50051

    def setUp(self):
        ELASTIC_APM_CONFIG = {
            'SERVICE_NAME': 'grpcapp',
            'SECRET_TOKEN': 'changeme',
            "ELASTIC_APM_SERVICE_NAME": "127.0.0.1"
        }

        self.server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=10),
            interceptors=(
                RequestHeaderValidatorInterceptor(config=ELASTIC_APM_CONFIG),
                RequestHeaderValidatorInterceptor(config=ELASTIC_APM_CONFIG),
            )
        )
        helloworld_pb2_grpc.add_GreeterServicer_to_server(self.server_class(), self.server)
        self.server.add_insecure_port(f'[::]:{self.port}')
        self.server.start()

    def tearDown(self):
        self.server.stop(None)

    def test_server(self):
        with grpc.insecure_channel(f'localhost:{self.port}') as channel:
            stub = helloworld_pb2_grpc.GreeterStub(channel)
            response = stub.SayHello(helloworld_pb2.HelloRequest(name='Jack'))
        self.assertEqual(response.message, 'Hello, Jack!')

        with grpc.insecure_channel(f'localhost:{self.port}') as channel:
            stub = helloworld_pb2_grpc.GreeterStub(channel)
            response = stub.SayHello(helloworld_pb2.HelloRequest(name='Ryan'))
        self.assertEqual(response.message, 'Hello, Ryan!')
