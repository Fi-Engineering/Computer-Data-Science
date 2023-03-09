import java.util.*;

public class RandomOrderGenerator {
	
	/***
	 * Given n numbers, this method returns an array
	 * which has a random order of the numbers from 
	 * 1 to n.
	 * @param n
	 * @return
	 */
	public static int[] getRandomOrder(int n) {
		Integer[] numbers = new Integer[n];
		for (int j = 0; j < numbers.length; j++) {
			numbers[j] = j + 1;
		}
		List<Integer> numList = Arrays.asList(numbers);
		Collections.shuffle(numList);
		int[] array = numList.stream().mapToInt(i->i).toArray();	
		return array;
	}
	
	public static void main(String[] args) {
		System.out.println(Arrays.toString(RandomOrderGenerator.getRandomOrder(10)));
	}
	
}
