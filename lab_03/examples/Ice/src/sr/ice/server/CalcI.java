package sr.ice.server;

import Demo.A;
import Demo.Calc;
import com.zeroc.Ice.Current;

import java.util.Objects;

public class CalcI implements Calc {
	private static final long serialVersionUID = -2448962912780867770L;
	long counter = 0;

	@Override
	public long add(int a, int b, Current __current) {
		if (Objects.equals(__current.id.name, "calc33")) {
			try {
				Thread.sleep(2000);
			} catch (InterruptedException ex) {
				Thread.currentThread().interrupt();
			}
		}

		if (a > 1000 || b > 1000) {
			try {
				Thread.sleep(6000);
			} catch (InterruptedException ex) {
				Thread.currentThread().interrupt();
			}
		}

		if (__current.ctx.values().size() > 0) {
			System.out.println("There are some properties in the context");
		}

		return a + b;
	}

	@Override
	public long subtract(int a, int b, Current __current) {
		if (__current.ctx.values().size() > 0) {
			System.out.println("There are some properties in the context");
		}

		return a - b;
	}

	@Override
	public /*synchronized*/ void op(A a1, short b1, Current current) {
		System.out.println("OP" + (++counter));
		try {
			Thread.sleep(500);
		} catch (java.lang.InterruptedException ex) {
			Thread.currentThread().interrupt();
		}
	}

	@Override
	public long avg(long[] a, Current __current) {
		long sum = 0;
		for (long l : a) {
			sum += l;
		}
		return sum / a.length;
	}
}