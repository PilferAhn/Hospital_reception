# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import iot_pb2 as iot__pb2


class PatientRecogniserStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.VerifyPatient = channel.unary_unary(
        '/PatientRecogniser/VerifyPatient',
        request_serializer=iot__pb2.PatientDetails.SerializeToString,
        response_deserializer=iot__pb2.Empty.FromString,
        )
    self.notifyDoctor = channel.unary_unary(
        '/PatientRecogniser/notifyDoctor',
        request_serializer=iot__pb2.Empty.SerializeToString,
        response_deserializer=iot__pb2.PatientDetails.FromString,
        )
    self.clearHistory = channel.unary_unary(
        '/PatientRecogniser/clearHistory',
        request_serializer=iot__pb2.PatientDetails.SerializeToString,
        response_deserializer=iot__pb2.Empty.FromString,
        )


class PatientRecogniserServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def VerifyPatient(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def notifyDoctor(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def clearHistory(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_PatientRecogniserServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'VerifyPatient': grpc.unary_unary_rpc_method_handler(
          servicer.VerifyPatient,
          request_deserializer=iot__pb2.PatientDetails.FromString,
          response_serializer=iot__pb2.Empty.SerializeToString,
      ),
      'notifyDoctor': grpc.unary_unary_rpc_method_handler(
          servicer.notifyDoctor,
          request_deserializer=iot__pb2.Empty.FromString,
          response_serializer=iot__pb2.PatientDetails.SerializeToString,
      ),
      'clearHistory': grpc.unary_unary_rpc_method_handler(
          servicer.clearHistory,
          request_deserializer=iot__pb2.PatientDetails.FromString,
          response_serializer=iot__pb2.Empty.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'PatientRecogniser', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))