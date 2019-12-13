# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: iot.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='iot.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\tiot.proto\"\x07\n\x05\x45mpty\"/\n\x0ePatientDetails\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x66\x65\x65ling\x18\x02 \x01(\t2\x95\x01\n\x11PatientRecogniser\x12*\n\rVerifyPatient\x12\x0f.PatientDetails\x1a\x06.Empty\"\x00\x12)\n\x0cnotifyDoctor\x12\x06.Empty\x1a\x0f.PatientDetails\"\x00\x12)\n\x0c\x63learHistory\x12\x0f.PatientDetails\x1a\x06.Empty\"\x00\x62\x06proto3')
)




_EMPTY = _descriptor.Descriptor(
  name='Empty',
  full_name='Empty',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=13,
  serialized_end=20,
)


_PATIENTDETAILS = _descriptor.Descriptor(
  name='PatientDetails',
  full_name='PatientDetails',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='PatientDetails.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='feeling', full_name='PatientDetails.feeling', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=22,
  serialized_end=69,
)

DESCRIPTOR.message_types_by_name['Empty'] = _EMPTY
DESCRIPTOR.message_types_by_name['PatientDetails'] = _PATIENTDETAILS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Empty = _reflection.GeneratedProtocolMessageType('Empty', (_message.Message,), dict(
  DESCRIPTOR = _EMPTY,
  __module__ = 'iot_pb2'
  # @@protoc_insertion_point(class_scope:Empty)
  ))
_sym_db.RegisterMessage(Empty)

PatientDetails = _reflection.GeneratedProtocolMessageType('PatientDetails', (_message.Message,), dict(
  DESCRIPTOR = _PATIENTDETAILS,
  __module__ = 'iot_pb2'
  # @@protoc_insertion_point(class_scope:PatientDetails)
  ))
_sym_db.RegisterMessage(PatientDetails)



_PATIENTRECOGNISER = _descriptor.ServiceDescriptor(
  name='PatientRecogniser',
  full_name='PatientRecogniser',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=72,
  serialized_end=221,
  methods=[
  _descriptor.MethodDescriptor(
    name='VerifyPatient',
    full_name='PatientRecogniser.VerifyPatient',
    index=0,
    containing_service=None,
    input_type=_PATIENTDETAILS,
    output_type=_EMPTY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='notifyDoctor',
    full_name='PatientRecogniser.notifyDoctor',
    index=1,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_PATIENTDETAILS,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='clearHistory',
    full_name='PatientRecogniser.clearHistory',
    index=2,
    containing_service=None,
    input_type=_PATIENTDETAILS,
    output_type=_EMPTY,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_PATIENTRECOGNISER)

DESCRIPTOR.services_by_name['PatientRecogniser'] = _PATIENTRECOGNISER

# @@protoc_insertion_point(module_scope)
