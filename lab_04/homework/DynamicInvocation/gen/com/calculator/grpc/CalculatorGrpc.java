package com.calculator.grpc;

import static io.grpc.MethodDescriptor.generateFullMethodName;

/**
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.71.0)",
    comments = "Source: calculator.proto")
@io.grpc.stub.annotations.GrpcGenerated
public final class CalculatorGrpc {

  private CalculatorGrpc() {}

  public static final java.lang.String SERVICE_NAME = "calculator.Calculator";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<com.calculator.grpc.AddRequest,
      com.calculator.grpc.AddResponse> getAddMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "Add",
      requestType = com.calculator.grpc.AddRequest.class,
      responseType = com.calculator.grpc.AddResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.calculator.grpc.AddRequest,
      com.calculator.grpc.AddResponse> getAddMethod() {
    io.grpc.MethodDescriptor<com.calculator.grpc.AddRequest, com.calculator.grpc.AddResponse> getAddMethod;
    if ((getAddMethod = CalculatorGrpc.getAddMethod) == null) {
      synchronized (CalculatorGrpc.class) {
        if ((getAddMethod = CalculatorGrpc.getAddMethod) == null) {
          CalculatorGrpc.getAddMethod = getAddMethod =
              io.grpc.MethodDescriptor.<com.calculator.grpc.AddRequest, com.calculator.grpc.AddResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "Add"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.AddRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.AddResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CalculatorMethodDescriptorSupplier("Add"))
              .build();
        }
      }
    }
    return getAddMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.calculator.grpc.SubRequest,
      com.calculator.grpc.SubResponse> getSubMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "Sub",
      requestType = com.calculator.grpc.SubRequest.class,
      responseType = com.calculator.grpc.SubResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.calculator.grpc.SubRequest,
      com.calculator.grpc.SubResponse> getSubMethod() {
    io.grpc.MethodDescriptor<com.calculator.grpc.SubRequest, com.calculator.grpc.SubResponse> getSubMethod;
    if ((getSubMethod = CalculatorGrpc.getSubMethod) == null) {
      synchronized (CalculatorGrpc.class) {
        if ((getSubMethod = CalculatorGrpc.getSubMethod) == null) {
          CalculatorGrpc.getSubMethod = getSubMethod =
              io.grpc.MethodDescriptor.<com.calculator.grpc.SubRequest, com.calculator.grpc.SubResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "Sub"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.SubRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.SubResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CalculatorMethodDescriptorSupplier("Sub"))
              .build();
        }
      }
    }
    return getSubMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.calculator.grpc.MulRequest,
      com.calculator.grpc.MulResponse> getMulMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "Mul",
      requestType = com.calculator.grpc.MulRequest.class,
      responseType = com.calculator.grpc.MulResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.calculator.grpc.MulRequest,
      com.calculator.grpc.MulResponse> getMulMethod() {
    io.grpc.MethodDescriptor<com.calculator.grpc.MulRequest, com.calculator.grpc.MulResponse> getMulMethod;
    if ((getMulMethod = CalculatorGrpc.getMulMethod) == null) {
      synchronized (CalculatorGrpc.class) {
        if ((getMulMethod = CalculatorGrpc.getMulMethod) == null) {
          CalculatorGrpc.getMulMethod = getMulMethod =
              io.grpc.MethodDescriptor.<com.calculator.grpc.MulRequest, com.calculator.grpc.MulResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "Mul"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.MulRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.MulResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CalculatorMethodDescriptorSupplier("Mul"))
              .build();
        }
      }
    }
    return getMulMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.calculator.grpc.DivRequest,
      com.calculator.grpc.DivResponse> getDivMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "Div",
      requestType = com.calculator.grpc.DivRequest.class,
      responseType = com.calculator.grpc.DivResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.calculator.grpc.DivRequest,
      com.calculator.grpc.DivResponse> getDivMethod() {
    io.grpc.MethodDescriptor<com.calculator.grpc.DivRequest, com.calculator.grpc.DivResponse> getDivMethod;
    if ((getDivMethod = CalculatorGrpc.getDivMethod) == null) {
      synchronized (CalculatorGrpc.class) {
        if ((getDivMethod = CalculatorGrpc.getDivMethod) == null) {
          CalculatorGrpc.getDivMethod = getDivMethod =
              io.grpc.MethodDescriptor.<com.calculator.grpc.DivRequest, com.calculator.grpc.DivResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "Div"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.DivRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.DivResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CalculatorMethodDescriptorSupplier("Div"))
              .build();
        }
      }
    }
    return getDivMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.calculator.grpc.SumRequest,
      com.calculator.grpc.SumResponse> getSumMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "Sum",
      requestType = com.calculator.grpc.SumRequest.class,
      responseType = com.calculator.grpc.SumResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.calculator.grpc.SumRequest,
      com.calculator.grpc.SumResponse> getSumMethod() {
    io.grpc.MethodDescriptor<com.calculator.grpc.SumRequest, com.calculator.grpc.SumResponse> getSumMethod;
    if ((getSumMethod = CalculatorGrpc.getSumMethod) == null) {
      synchronized (CalculatorGrpc.class) {
        if ((getSumMethod = CalculatorGrpc.getSumMethod) == null) {
          CalculatorGrpc.getSumMethod = getSumMethod =
              io.grpc.MethodDescriptor.<com.calculator.grpc.SumRequest, com.calculator.grpc.SumResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "Sum"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.SumRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.SumResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CalculatorMethodDescriptorSupplier("Sum"))
              .build();
        }
      }
    }
    return getSumMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.calculator.grpc.PrimeNumbersRequest,
      com.calculator.grpc.PrimeNumbersResponse> getPrimeNumbersMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "PrimeNumbers",
      requestType = com.calculator.grpc.PrimeNumbersRequest.class,
      responseType = com.calculator.grpc.PrimeNumbersResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.calculator.grpc.PrimeNumbersRequest,
      com.calculator.grpc.PrimeNumbersResponse> getPrimeNumbersMethod() {
    io.grpc.MethodDescriptor<com.calculator.grpc.PrimeNumbersRequest, com.calculator.grpc.PrimeNumbersResponse> getPrimeNumbersMethod;
    if ((getPrimeNumbersMethod = CalculatorGrpc.getPrimeNumbersMethod) == null) {
      synchronized (CalculatorGrpc.class) {
        if ((getPrimeNumbersMethod = CalculatorGrpc.getPrimeNumbersMethod) == null) {
          CalculatorGrpc.getPrimeNumbersMethod = getPrimeNumbersMethod =
              io.grpc.MethodDescriptor.<com.calculator.grpc.PrimeNumbersRequest, com.calculator.grpc.PrimeNumbersResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "PrimeNumbers"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.PrimeNumbersRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.PrimeNumbersResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CalculatorMethodDescriptorSupplier("PrimeNumbers"))
              .build();
        }
      }
    }
    return getPrimeNumbersMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.calculator.grpc.PrimeNumbersRequest,
      com.calculator.grpc.PrimeNumber> getStreamPrimeNumbersMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "StreamPrimeNumbers",
      requestType = com.calculator.grpc.PrimeNumbersRequest.class,
      responseType = com.calculator.grpc.PrimeNumber.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<com.calculator.grpc.PrimeNumbersRequest,
      com.calculator.grpc.PrimeNumber> getStreamPrimeNumbersMethod() {
    io.grpc.MethodDescriptor<com.calculator.grpc.PrimeNumbersRequest, com.calculator.grpc.PrimeNumber> getStreamPrimeNumbersMethod;
    if ((getStreamPrimeNumbersMethod = CalculatorGrpc.getStreamPrimeNumbersMethod) == null) {
      synchronized (CalculatorGrpc.class) {
        if ((getStreamPrimeNumbersMethod = CalculatorGrpc.getStreamPrimeNumbersMethod) == null) {
          CalculatorGrpc.getStreamPrimeNumbersMethod = getStreamPrimeNumbersMethod =
              io.grpc.MethodDescriptor.<com.calculator.grpc.PrimeNumbersRequest, com.calculator.grpc.PrimeNumber>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "StreamPrimeNumbers"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.PrimeNumbersRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.PrimeNumber.getDefaultInstance()))
              .setSchemaDescriptor(new CalculatorMethodDescriptorSupplier("StreamPrimeNumbers"))
              .build();
        }
      }
    }
    return getStreamPrimeNumbersMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.calculator.grpc.PrimeNumber,
      com.calculator.grpc.PrimeNumbersCount> getCountPrimeNumbersMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "CountPrimeNumbers",
      requestType = com.calculator.grpc.PrimeNumber.class,
      responseType = com.calculator.grpc.PrimeNumbersCount.class,
      methodType = io.grpc.MethodDescriptor.MethodType.CLIENT_STREAMING)
  public static io.grpc.MethodDescriptor<com.calculator.grpc.PrimeNumber,
      com.calculator.grpc.PrimeNumbersCount> getCountPrimeNumbersMethod() {
    io.grpc.MethodDescriptor<com.calculator.grpc.PrimeNumber, com.calculator.grpc.PrimeNumbersCount> getCountPrimeNumbersMethod;
    if ((getCountPrimeNumbersMethod = CalculatorGrpc.getCountPrimeNumbersMethod) == null) {
      synchronized (CalculatorGrpc.class) {
        if ((getCountPrimeNumbersMethod = CalculatorGrpc.getCountPrimeNumbersMethod) == null) {
          CalculatorGrpc.getCountPrimeNumbersMethod = getCountPrimeNumbersMethod =
              io.grpc.MethodDescriptor.<com.calculator.grpc.PrimeNumber, com.calculator.grpc.PrimeNumbersCount>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.CLIENT_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "CountPrimeNumbers"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.PrimeNumber.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.calculator.grpc.PrimeNumbersCount.getDefaultInstance()))
              .setSchemaDescriptor(new CalculatorMethodDescriptorSupplier("CountPrimeNumbers"))
              .build();
        }
      }
    }
    return getCountPrimeNumbersMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static CalculatorStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<CalculatorStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<CalculatorStub>() {
        @java.lang.Override
        public CalculatorStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new CalculatorStub(channel, callOptions);
        }
      };
    return CalculatorStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports all types of calls on the service
   */
  public static CalculatorBlockingV2Stub newBlockingV2Stub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<CalculatorBlockingV2Stub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<CalculatorBlockingV2Stub>() {
        @java.lang.Override
        public CalculatorBlockingV2Stub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new CalculatorBlockingV2Stub(channel, callOptions);
        }
      };
    return CalculatorBlockingV2Stub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static CalculatorBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<CalculatorBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<CalculatorBlockingStub>() {
        @java.lang.Override
        public CalculatorBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new CalculatorBlockingStub(channel, callOptions);
        }
      };
    return CalculatorBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static CalculatorFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<CalculatorFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<CalculatorFutureStub>() {
        @java.lang.Override
        public CalculatorFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new CalculatorFutureStub(channel, callOptions);
        }
      };
    return CalculatorFutureStub.newStub(factory, channel);
  }

  /**
   */
  public interface AsyncService {

    /**
     */
    default void add(com.calculator.grpc.AddRequest request,
        io.grpc.stub.StreamObserver<com.calculator.grpc.AddResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getAddMethod(), responseObserver);
    }

    /**
     */
    default void sub(com.calculator.grpc.SubRequest request,
        io.grpc.stub.StreamObserver<com.calculator.grpc.SubResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getSubMethod(), responseObserver);
    }

    /**
     */
    default void mul(com.calculator.grpc.MulRequest request,
        io.grpc.stub.StreamObserver<com.calculator.grpc.MulResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getMulMethod(), responseObserver);
    }

    /**
     */
    default void div(com.calculator.grpc.DivRequest request,
        io.grpc.stub.StreamObserver<com.calculator.grpc.DivResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getDivMethod(), responseObserver);
    }

    /**
     */
    default void sum(com.calculator.grpc.SumRequest request,
        io.grpc.stub.StreamObserver<com.calculator.grpc.SumResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getSumMethod(), responseObserver);
    }

    /**
     */
    default void primeNumbers(com.calculator.grpc.PrimeNumbersRequest request,
        io.grpc.stub.StreamObserver<com.calculator.grpc.PrimeNumbersResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getPrimeNumbersMethod(), responseObserver);
    }

    /**
     * <pre>
     * Streaming version - server streaming
     * </pre>
     */
    default void streamPrimeNumbers(com.calculator.grpc.PrimeNumbersRequest request,
        io.grpc.stub.StreamObserver<com.calculator.grpc.PrimeNumber> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getStreamPrimeNumbersMethod(), responseObserver);
    }

    /**
     * <pre>
     * Streaming version - client streaming
     * </pre>
     */
    default io.grpc.stub.StreamObserver<com.calculator.grpc.PrimeNumber> countPrimeNumbers(
        io.grpc.stub.StreamObserver<com.calculator.grpc.PrimeNumbersCount> responseObserver) {
      return io.grpc.stub.ServerCalls.asyncUnimplementedStreamingCall(getCountPrimeNumbersMethod(), responseObserver);
    }
  }

  /**
   * Base class for the server implementation of the service Calculator.
   */
  public static abstract class CalculatorImplBase
      implements io.grpc.BindableService, AsyncService {

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return CalculatorGrpc.bindService(this);
    }
  }

  /**
   * A stub to allow clients to do asynchronous rpc calls to service Calculator.
   */
  public static final class CalculatorStub
      extends io.grpc.stub.AbstractAsyncStub<CalculatorStub> {
    private CalculatorStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected CalculatorStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new CalculatorStub(channel, callOptions);
    }

    /**
     */
    public void add(com.calculator.grpc.AddRequest request,
        io.grpc.stub.StreamObserver<com.calculator.grpc.AddResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getAddMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void sub(com.calculator.grpc.SubRequest request,
        io.grpc.stub.StreamObserver<com.calculator.grpc.SubResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getSubMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void mul(com.calculator.grpc.MulRequest request,
        io.grpc.stub.StreamObserver<com.calculator.grpc.MulResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getMulMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void div(com.calculator.grpc.DivRequest request,
        io.grpc.stub.StreamObserver<com.calculator.grpc.DivResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getDivMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void sum(com.calculator.grpc.SumRequest request,
        io.grpc.stub.StreamObserver<com.calculator.grpc.SumResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getSumMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void primeNumbers(com.calculator.grpc.PrimeNumbersRequest request,
        io.grpc.stub.StreamObserver<com.calculator.grpc.PrimeNumbersResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getPrimeNumbersMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Streaming version - server streaming
     * </pre>
     */
    public void streamPrimeNumbers(com.calculator.grpc.PrimeNumbersRequest request,
        io.grpc.stub.StreamObserver<com.calculator.grpc.PrimeNumber> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getStreamPrimeNumbersMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Streaming version - client streaming
     * </pre>
     */
    public io.grpc.stub.StreamObserver<com.calculator.grpc.PrimeNumber> countPrimeNumbers(
        io.grpc.stub.StreamObserver<com.calculator.grpc.PrimeNumbersCount> responseObserver) {
      return io.grpc.stub.ClientCalls.asyncClientStreamingCall(
          getChannel().newCall(getCountPrimeNumbersMethod(), getCallOptions()), responseObserver);
    }
  }

  /**
   * A stub to allow clients to do synchronous rpc calls to service Calculator.
   */
  public static final class CalculatorBlockingV2Stub
      extends io.grpc.stub.AbstractBlockingStub<CalculatorBlockingV2Stub> {
    private CalculatorBlockingV2Stub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected CalculatorBlockingV2Stub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new CalculatorBlockingV2Stub(channel, callOptions);
    }

    /**
     */
    public com.calculator.grpc.AddResponse add(com.calculator.grpc.AddRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getAddMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.calculator.grpc.SubResponse sub(com.calculator.grpc.SubRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getSubMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.calculator.grpc.MulResponse mul(com.calculator.grpc.MulRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getMulMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.calculator.grpc.DivResponse div(com.calculator.grpc.DivRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getDivMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.calculator.grpc.SumResponse sum(com.calculator.grpc.SumRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getSumMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.calculator.grpc.PrimeNumbersResponse primeNumbers(com.calculator.grpc.PrimeNumbersRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getPrimeNumbersMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Streaming version - server streaming
     * </pre>
     */
    @io.grpc.ExperimentalApi("https://github.com/grpc/grpc-java/issues/10918")
    public io.grpc.stub.BlockingClientCall<?, com.calculator.grpc.PrimeNumber>
        streamPrimeNumbers(com.calculator.grpc.PrimeNumbersRequest request) {
      return io.grpc.stub.ClientCalls.blockingV2ServerStreamingCall(
          getChannel(), getStreamPrimeNumbersMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Streaming version - client streaming
     * </pre>
     */
    @io.grpc.ExperimentalApi("https://github.com/grpc/grpc-java/issues/10918")
    public io.grpc.stub.BlockingClientCall<com.calculator.grpc.PrimeNumber, com.calculator.grpc.PrimeNumbersCount>
        countPrimeNumbers() {
      return io.grpc.stub.ClientCalls.blockingClientStreamingCall(
          getChannel(), getCountPrimeNumbersMethod(), getCallOptions());
    }
  }

  /**
   * A stub to allow clients to do limited synchronous rpc calls to service Calculator.
   */
  public static final class CalculatorBlockingStub
      extends io.grpc.stub.AbstractBlockingStub<CalculatorBlockingStub> {
    private CalculatorBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected CalculatorBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new CalculatorBlockingStub(channel, callOptions);
    }

    /**
     */
    public com.calculator.grpc.AddResponse add(com.calculator.grpc.AddRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getAddMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.calculator.grpc.SubResponse sub(com.calculator.grpc.SubRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getSubMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.calculator.grpc.MulResponse mul(com.calculator.grpc.MulRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getMulMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.calculator.grpc.DivResponse div(com.calculator.grpc.DivRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getDivMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.calculator.grpc.SumResponse sum(com.calculator.grpc.SumRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getSumMethod(), getCallOptions(), request);
    }

    /**
     */
    public com.calculator.grpc.PrimeNumbersResponse primeNumbers(com.calculator.grpc.PrimeNumbersRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getPrimeNumbersMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Streaming version - server streaming
     * </pre>
     */
    public java.util.Iterator<com.calculator.grpc.PrimeNumber> streamPrimeNumbers(
        com.calculator.grpc.PrimeNumbersRequest request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getStreamPrimeNumbersMethod(), getCallOptions(), request);
    }
  }

  /**
   * A stub to allow clients to do ListenableFuture-style rpc calls to service Calculator.
   */
  public static final class CalculatorFutureStub
      extends io.grpc.stub.AbstractFutureStub<CalculatorFutureStub> {
    private CalculatorFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected CalculatorFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new CalculatorFutureStub(channel, callOptions);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.calculator.grpc.AddResponse> add(
        com.calculator.grpc.AddRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getAddMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.calculator.grpc.SubResponse> sub(
        com.calculator.grpc.SubRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getSubMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.calculator.grpc.MulResponse> mul(
        com.calculator.grpc.MulRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getMulMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.calculator.grpc.DivResponse> div(
        com.calculator.grpc.DivRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getDivMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.calculator.grpc.SumResponse> sum(
        com.calculator.grpc.SumRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getSumMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.calculator.grpc.PrimeNumbersResponse> primeNumbers(
        com.calculator.grpc.PrimeNumbersRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getPrimeNumbersMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_ADD = 0;
  private static final int METHODID_SUB = 1;
  private static final int METHODID_MUL = 2;
  private static final int METHODID_DIV = 3;
  private static final int METHODID_SUM = 4;
  private static final int METHODID_PRIME_NUMBERS = 5;
  private static final int METHODID_STREAM_PRIME_NUMBERS = 6;
  private static final int METHODID_COUNT_PRIME_NUMBERS = 7;

  private static final class MethodHandlers<Req, Resp> implements
      io.grpc.stub.ServerCalls.UnaryMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ServerStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ClientStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.BidiStreamingMethod<Req, Resp> {
    private final AsyncService serviceImpl;
    private final int methodId;

    MethodHandlers(AsyncService serviceImpl, int methodId) {
      this.serviceImpl = serviceImpl;
      this.methodId = methodId;
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public void invoke(Req request, io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        case METHODID_ADD:
          serviceImpl.add((com.calculator.grpc.AddRequest) request,
              (io.grpc.stub.StreamObserver<com.calculator.grpc.AddResponse>) responseObserver);
          break;
        case METHODID_SUB:
          serviceImpl.sub((com.calculator.grpc.SubRequest) request,
              (io.grpc.stub.StreamObserver<com.calculator.grpc.SubResponse>) responseObserver);
          break;
        case METHODID_MUL:
          serviceImpl.mul((com.calculator.grpc.MulRequest) request,
              (io.grpc.stub.StreamObserver<com.calculator.grpc.MulResponse>) responseObserver);
          break;
        case METHODID_DIV:
          serviceImpl.div((com.calculator.grpc.DivRequest) request,
              (io.grpc.stub.StreamObserver<com.calculator.grpc.DivResponse>) responseObserver);
          break;
        case METHODID_SUM:
          serviceImpl.sum((com.calculator.grpc.SumRequest) request,
              (io.grpc.stub.StreamObserver<com.calculator.grpc.SumResponse>) responseObserver);
          break;
        case METHODID_PRIME_NUMBERS:
          serviceImpl.primeNumbers((com.calculator.grpc.PrimeNumbersRequest) request,
              (io.grpc.stub.StreamObserver<com.calculator.grpc.PrimeNumbersResponse>) responseObserver);
          break;
        case METHODID_STREAM_PRIME_NUMBERS:
          serviceImpl.streamPrimeNumbers((com.calculator.grpc.PrimeNumbersRequest) request,
              (io.grpc.stub.StreamObserver<com.calculator.grpc.PrimeNumber>) responseObserver);
          break;
        default:
          throw new AssertionError();
      }
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public io.grpc.stub.StreamObserver<Req> invoke(
        io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        case METHODID_COUNT_PRIME_NUMBERS:
          return (io.grpc.stub.StreamObserver<Req>) serviceImpl.countPrimeNumbers(
              (io.grpc.stub.StreamObserver<com.calculator.grpc.PrimeNumbersCount>) responseObserver);
        default:
          throw new AssertionError();
      }
    }
  }

  public static final io.grpc.ServerServiceDefinition bindService(AsyncService service) {
    return io.grpc.ServerServiceDefinition.builder(getServiceDescriptor())
        .addMethod(
          getAddMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.calculator.grpc.AddRequest,
              com.calculator.grpc.AddResponse>(
                service, METHODID_ADD)))
        .addMethod(
          getSubMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.calculator.grpc.SubRequest,
              com.calculator.grpc.SubResponse>(
                service, METHODID_SUB)))
        .addMethod(
          getMulMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.calculator.grpc.MulRequest,
              com.calculator.grpc.MulResponse>(
                service, METHODID_MUL)))
        .addMethod(
          getDivMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.calculator.grpc.DivRequest,
              com.calculator.grpc.DivResponse>(
                service, METHODID_DIV)))
        .addMethod(
          getSumMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.calculator.grpc.SumRequest,
              com.calculator.grpc.SumResponse>(
                service, METHODID_SUM)))
        .addMethod(
          getPrimeNumbersMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.calculator.grpc.PrimeNumbersRequest,
              com.calculator.grpc.PrimeNumbersResponse>(
                service, METHODID_PRIME_NUMBERS)))
        .addMethod(
          getStreamPrimeNumbersMethod(),
          io.grpc.stub.ServerCalls.asyncServerStreamingCall(
            new MethodHandlers<
              com.calculator.grpc.PrimeNumbersRequest,
              com.calculator.grpc.PrimeNumber>(
                service, METHODID_STREAM_PRIME_NUMBERS)))
        .addMethod(
          getCountPrimeNumbersMethod(),
          io.grpc.stub.ServerCalls.asyncClientStreamingCall(
            new MethodHandlers<
              com.calculator.grpc.PrimeNumber,
              com.calculator.grpc.PrimeNumbersCount>(
                service, METHODID_COUNT_PRIME_NUMBERS)))
        .build();
  }

  private static abstract class CalculatorBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    CalculatorBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return com.calculator.grpc.CalculatorOuterClass.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("Calculator");
    }
  }

  private static final class CalculatorFileDescriptorSupplier
      extends CalculatorBaseDescriptorSupplier {
    CalculatorFileDescriptorSupplier() {}
  }

  private static final class CalculatorMethodDescriptorSupplier
      extends CalculatorBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final java.lang.String methodName;

    CalculatorMethodDescriptorSupplier(java.lang.String methodName) {
      this.methodName = methodName;
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.MethodDescriptor getMethodDescriptor() {
      return getServiceDescriptor().findMethodByName(methodName);
    }
  }

  private static volatile io.grpc.ServiceDescriptor serviceDescriptor;

  public static io.grpc.ServiceDescriptor getServiceDescriptor() {
    io.grpc.ServiceDescriptor result = serviceDescriptor;
    if (result == null) {
      synchronized (CalculatorGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new CalculatorFileDescriptorSupplier())
              .addMethod(getAddMethod())
              .addMethod(getSubMethod())
              .addMethod(getMulMethod())
              .addMethod(getDivMethod())
              .addMethod(getSumMethod())
              .addMethod(getPrimeNumbersMethod())
              .addMethod(getStreamPrimeNumbersMethod())
              .addMethod(getCountPrimeNumbersMethod())
              .build();
        }
      }
    }
    return result;
  }
}
