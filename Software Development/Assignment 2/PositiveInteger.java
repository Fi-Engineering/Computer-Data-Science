
public class PositiveInteger {

	int num;
	
	public PositiveInteger(int number) {
		num = number;
	}

	public boolean isPerfect() {
		int[] factors = new int[num];
		int factorsSum = 0;
		for (int i = 1; i < num; i++) {
			if ((num % i) == 0) {
				factors[i] = i;
				factorsSum += i;
			}
		}
		return num == factorsSum;
	}

	public boolean isAbundant() {
		int[] factors = new int[num];
		int factorsSum = 0;
		for (int i = 1; i < num; i++) {
			if ((num % i) == 0) {
				factors[i] = i;
				factorsSum += i;
			}
		}
		return factorsSum > num;
	}

	public boolean isNarcissistic() {
		StringBuilder numAsString = new StringBuilder(Integer.toString(num));
		int numDigits = numAsString.length();
		int cumulativeSum = 0;
		for (int i = 0; i < numDigits; i++) {
			cumulativeSum += Math.pow(Character.getNumericValue(numAsString.charAt(i)), numDigits);
		}
		return cumulativeSum == num;
	}

	public static void main(String[] args) {
		PositiveInteger test = new PositiveInteger(6);
		System.out.println(test.isPerfect());
		System.out.println(test.isAbundant());
		System.out.println(test.isNarcissistic());
	}
}
