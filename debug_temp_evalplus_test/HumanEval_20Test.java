import org.junit.Test;
import static org.junit.Assert.*;
import java.util.*;
import java.math.*;

public class HumanEval_20Test{
	@Test
	public void test_0() {
		List<Double> numbers = List.of(1.0, 2.0, 3.9, 4.0, 5.0, 2.2);
		Tuple expected = new Tuple<>(3.9, 4.0);
		assertEquals(expected.x, HumanEval_20.findClosestElements(numbers).x);
		assertEquals(expected.y, HumanEval_20.findClosestElements(numbers).y);
	}

	@Test
	public void test_1() {
		List<Double> numbers = List.of(1.0, 2.0, 5.9, 4.0, 5.0);
		Tuple expected = new Tuple<>(5.0, 5.9);
		assertEquals(expected.x, HumanEval_20.findClosestElements(numbers).x);
		assertEquals(expected.y, HumanEval_20.findClosestElements(numbers).y);
	}

	@Test
	public void test_2() {
		List<Double> numbers = List.of(1.0, 2.0, 3.0, 4.0, 5.0, 2.2);
		Tuple expected = new Tuple<>(2.0, 2.2);
		assertEquals(expected.x, HumanEval_20.findClosestElements(numbers).x);
		assertEquals(expected.y, HumanEval_20.findClosestElements(numbers).y);
	}

	@Test
	public void test_3() {
		List<Double> numbers = List.of(1.0, 2.0, 3.0, 4.0, 5.0, 2.0);
		Tuple expected = new Tuple<>(2.0, 2.0);
		assertEquals(expected.x, HumanEval_20.findClosestElements(numbers).x);
		assertEquals(expected.y, HumanEval_20.findClosestElements(numbers).y);
	}

	@Test
	public void test_4() {
		List<Double> numbers = List.of(1.1, 2.2, 3.1, 4.1, 5.1);
		Tuple expected = new Tuple<>(2.2, 3.1);
		assertEquals(expected.x, HumanEval_20.findClosestElements(numbers).x);
		assertEquals(expected.y, HumanEval_20.findClosestElements(numbers).y);
	}

	@Test
	public void test_5() {
		List<Double> numbers = List.of(1.5, 2.5, 3.5, 4.5);
		Tuple expected = new Tuple<>(1.5, 2.5);
		assertEquals(expected.x, HumanEval_20.findClosestElements(numbers).x);
		assertEquals(expected.y, HumanEval_20.findClosestElements(numbers).y);
	}

	@Test
	public void test_6() {
		List<Double> numbers = List.of(0.5, 0.9, 1.2, 1.8, 2.5, 2.9, 3.1);
		Tuple expected = new Tuple<>(2.9, 3.1);
		assertEquals(expected.x, HumanEval_20.findClosestElements(numbers).x);
		assertEquals(expected.y, HumanEval_20.findClosestElements(numbers).y);
	}

	@Test
	public void test_7() {
		List<Double> numbers = List.of(1.1963194756636508, 2.0, 2.1, 2.2, 2.3, 2.4, 2.424000205756431, 2.5, 3.4);
		Tuple expected = new Tuple<>(2.4, 2.424000205756431);
		assertEquals(expected.x, HumanEval_20.findClosestElements(numbers).x);
		assertEquals(expected.y, HumanEval_20.findClosestElements(numbers).y);
	}

	@Test
	public void test_8() {
		List<Double> numbers = List.of(2.0, 2.0, 4.0, 4.5, 6.0, 8.44265458853031, 10.0, 10.0, 10.0, 12.0, 14.0, 16.0, 16.0, 18.0, 20.0, 20.0);
		Tuple expected = new Tuple<>(2.0, 2.0);
		assertEquals(expected.x, HumanEval_20.findClosestElements(numbers).x);
		assertEquals(expected.y, HumanEval_20.findClosestElements(numbers).y);
	}

	@Test
	public void test_9() {
		List<Double> numbers = List.of(2.0, 2.1, 2.1);
		Tuple expected = new Tuple<>(2.1, 2.1);
		assertEquals(expected.x, HumanEval_20.findClosestElements(numbers).x);
		assertEquals(expected.y, HumanEval_20.findClosestElements(numbers).y);
	}

	@Test
	public void test_10() {
		List<Double> numbers = List.of(-3.0,  53.0);
		Tuple expected = new Tuple<>(-3, 53);
		assertEquals(expected.x, HumanEval_20.findClosestElements(numbers).x);
		assertEquals(expected.y, HumanEval_20.findClosestElements(numbers).y);
	}

	@Test
	public void test_11() {
		List<Double> numbers = List.of(-20.0, -10.0, -7.0, -5.5, -1.0, 0.0, 3.14159, 8.0, 12.345, 30.0);
		Tuple expected = new Tuple<>(-1.0, 0.0);
		assertEquals(expected.x, HumanEval_20.findClosestElements(numbers).x);
		assertEquals(expected.y, HumanEval_20.findClosestElements(numbers).y);
	}
}
