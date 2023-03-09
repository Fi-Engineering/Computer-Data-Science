
public class CoatExperimentSimulator {
	// variables
	int numberOfPeople;

	// constructors
	CoatExperimentSimulator(int numPpl) {
		numberOfPeople = numPpl;
	}

	// methods
	public int numPplWhoGotTheirCoat(int[] permutation) {
		int numPpl = 0;

		for (int i = 0; i < permutation.length; i++) {
			if (i == permutation[i]) {
				numPpl++;
			}
		}

		return numPpl;
	}

	public int[] simulateCoatExperiment(int iterations) {
		int[] result = new int[iterations]; // array declaration. the number in [] is the length of the array.
		
		for (int i = 0; i < iterations; i++) {
			int[] randomArrangement = RandomOrderGenerator.getRandomOrder(numberOfPeople);
			result[i] = numPplWhoGotTheirCoat(randomArrangement);
		}
		
		return result;
	}

	public double answerToQuestionA(int[] results) { // results given to us by simulateCoatExperiment
		double numZeroSuccess = 0; // counter for number of zeros in all trials

		for (int i = 0; i < results.length; i++) { // loop through the array
			if (results[i] == 0) { // if there's a zero,
				numZeroSuccess++; // take note of it.
			}
		}
		
		return numZeroSuccess / results.length; // return probability
	}

	public double answerToQuestionB(int[] results) {
		double cumulativeSum = 0; // counter for cumulative sum in all trials

		for (int i = 0; i < results.length; i++) { // loop through the array
			cumulativeSum = cumulativeSum + results[i]; // set cumulative Sum equal to itself plus the value at
														// results[i]
		}

		return cumulativeSum / results.length; // return probability
	}

	public static void main(String[] args) {
		// variables
		int[] results;
		double probabilityOfZeroes;
		double averageCoatsRetrvd;
		double estimate;

		// simulation
		CoatExperimentSimulator mySimulator = new CoatExperimentSimulator(25); // create a CoatExperimentSimulator with
																				// 25 people. This is where you will be
																				// using the constructor.
		results = mySimulator.simulateCoatExperiment(100000); // run the simulation 100000 times
		probabilityOfZeroes = mySimulator.answerToQuestionA(results);
		System.out.println(probabilityOfZeroes); // print the probability of not getting your coat
		averageCoatsRetrvd = mySimulator.answerToQuestionB(results);
		System.out.println(averageCoatsRetrvd); // print the average number of people who get their coats back.
		estimate = 1 / probabilityOfZeroes; // prob0s (x) = 1/e, x = 1/e, ex = 1, e = 1/x
		System.out.println(estimate); /*
										 * print the estimate of the value of e that you got from this procedure.
										 * Remember that the probability for 0 people getting their coats back is 1/e as
										 * the number of people gets sufficiently large (100000 is a reasonable
										 * threshold for large).
										 */
	}
}
