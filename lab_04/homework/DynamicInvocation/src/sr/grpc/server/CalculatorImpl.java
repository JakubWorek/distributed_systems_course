package sr.grpc.server;

import com.calculator.grpc.AddRequest;
import com.calculator.grpc.AddResponse;
import com.calculator.grpc.CalculatorGrpc;
import com.calculator.grpc.SubRequest;
import com.calculator.grpc.SubResponse;
import com.calculator.grpc.MulRequest;
import com.calculator.grpc.MulResponse;
import com.calculator.grpc.DivRequest;
import com.calculator.grpc.DivResponse;
import com.calculator.grpc.SumRequest;
import com.calculator.grpc.SumResponse;
import com.calculator.grpc.PrimeNumbersResponse;
import com.calculator.grpc.PrimeNumbersRequest;
import com.calculator.grpc.PrimeNumber;
import com.calculator.grpc.PrimeNumbersCount;
import io.grpc.stub.StreamObserver;

public class CalculatorImpl extends CalculatorGrpc.CalculatorImplBase {

	@Override
	public void add(AddRequest request, StreamObserver<AddResponse> responseObserver) {
		int val = request.getAddend1() + request.getAddend2();
		AddResponse response = AddResponse.newBuilder().setSum(val).build();
		responseObserver.onNext(response);
		responseObserver.onCompleted();
	}

	@Override
	public void sub(SubRequest request, StreamObserver<SubResponse> responseObserver) {
		int val = request.getMinuend() - request.getSubtrahend();
		SubResponse response = SubResponse.newBuilder().setDifference(val).build();
		responseObserver.onNext(response);
		responseObserver.onCompleted();
	}

	@Override
	public void mul(MulRequest request, StreamObserver<MulResponse> responseObserver) {
		int val = request.getMultiplicand() * request.getMultiplier();
		MulResponse response = MulResponse.newBuilder().setProduct(val).build();
		responseObserver.onNext(response);
		responseObserver.onCompleted();
	}

	@Override
	public void div(DivRequest request, StreamObserver<DivResponse> responseObserver) {
		if (request.getDivisor() == 0) {
			responseObserver.onError(io.grpc.Status.INVALID_ARGUMENT.withDescription("Division by zero").asRuntimeException());
			return;
		}

		int val = request.getDividend() / request.getDivisor();
		DivResponse response = com.calculator.grpc.DivResponse.newBuilder().setQuotient(val).build();
		responseObserver.onNext(response);
		responseObserver.onCompleted();
	}

	@Override
	public void sum(SumRequest request, StreamObserver<SumResponse> responseObserver) {
		int sum = request.getAddendsList().stream().mapToInt(Integer::intValue).sum();
		SumResponse response = SumResponse.newBuilder().setSum(sum).build();
		responseObserver.onNext(response);
		responseObserver.onCompleted();
	}

	@Override
	public void primeNumbers(PrimeNumbersRequest request, StreamObserver<PrimeNumbersResponse> responseObserver) {
		int start = request.getStart();
		int end = request.getEnd();
		PrimeNumbersResponse.Builder responseBuilder = PrimeNumbersResponse.newBuilder();
		for (int i = start; i <= end; i++) {
			if (isPrime(i)) {
				responseBuilder.addPrimeNumbers(i);
			}
		}
		responseObserver.onNext(responseBuilder.build());
		responseObserver.onCompleted();
	}

	@Override
	public void streamPrimeNumbers(PrimeNumbersRequest request, StreamObserver<PrimeNumber> responseObserver) {
		System.out.println("streamPrimeNumbers is starting (start=" + request.getStart() + ", end=" + request.getEnd() + ")");
		for (int i = request.getStart(); i <= request.getEnd(); i++) {
			if (isPrime(i)) {
				PrimeNumber number = PrimeNumber.newBuilder().setValue(i).build();
				responseObserver.onNext(number);
				try {
					Thread.sleep(500);
				} catch (InterruptedException e) {
					Thread.currentThread().interrupt();
				}
			}
		}
		responseObserver.onCompleted();
		System.out.println("streamPrimeNumbers completed");
	}

	@Override
	public StreamObserver<PrimeNumber> countPrimeNumbers(StreamObserver<PrimeNumbersCount> responseObserver) {
		System.out.println("BEGIN countPrimeNumbers");
		return new PrimeNumbersObserver(responseObserver);
	}

	private boolean isPrime(int n) {
		if (n <= 1) {
			return false;
		}
		if (n <= 3) {
			return true;
		}
		if (n % 2 == 0 || n % 3 == 0) {
			return false;
		}
		int i = 5;
		while (i * i <= n) {
			if (n % i == 0 || n % (i + 2) == 0) {
				return false;
			}
			i += 6;
		}
		return true;
	}
}

class PrimeNumbersObserver implements StreamObserver<PrimeNumber> {
	private int count = 0;
	private final StreamObserver<PrimeNumbersCount> responseObserver;

	PrimeNumbersObserver(StreamObserver<PrimeNumbersCount> responseObserver) {
		this.responseObserver = responseObserver;
	}

	@Override
	public void onNext(PrimeNumber number) {
		System.out.println("Received number: " + number.getValue());
		if (isPrime(number.getValue())){
			count++;
		}
	}

	@Override
	public void onError(Throwable t) {
		System.out.println("Error in countPrimeNumbers: " + t.getMessage());
	}

	@Override
	public void onCompleted() {
		PrimeNumbersCount response = PrimeNumbersCount.newBuilder().setCount(count).build();
		responseObserver.onNext(response);
		responseObserver.onCompleted();
		System.out.println("END countPrimeNumbers, found " + count + " numbers");
	}

	private boolean isPrime(int n) {
		if (n <= 1) {
			return false;
		}
		if (n <= 3) {
			return true;
		}
		if (n % 2 == 0 || n % 3 == 0) {
			return false;
		}
		int i = 5;
		while (i * i <= n) {
			if (n % i == 0 || n % (i + 2) == 0) {
				return false;
			}
			i += 6;
		}
		return true;
	}
}
