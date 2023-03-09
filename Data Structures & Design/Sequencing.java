
import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Scanner;
import java.util.Set;
import java.util.TreeSet;

public class Analyzer {

	/*
	 * Implement this method in Part 1
	 */
	public static List<Sentence> readFile(String filename) {
		List<Sentence> result = new ArrayList<Sentence>();
		File n;
		Scanner reader;
		// int lineNum = 0;
		try {
			n = new File(filename);
			reader = new Scanner(n);
		} catch (Exception e) {
			System.out.println("No file found or filename is null.");
			return result;
		}
		// int i = 1;
		while (reader.hasNextLine()) {
			String line = reader.nextLine();
			// lineNum++;
			Scanner scoreScan = new Scanner(line);
			int score;
			try {
				score = scoreScan.nextInt();
				scoreScan.close();
				if (line.indexOf(Integer.toString(score) + " ") != 0)
					continue;
			} catch (Exception e) {
				continue;
			}
			String[] lineArr = line.split(score + " ");
			try {
				if (lineArr[1] == null) // can't actually get executed cuz it errors out at [1] lol
					continue;
			} catch (Exception e) { // nothing after the score
				continue;
			}
			// i--;
			result.add(new Sentence(score, lineArr[1]));
		}
		reader.close();
		return result;
	}

	/*
	 * Implement this method in Part 2
	 */
	public static Set<Word> allWords(List<Sentence> sentences) {
		HashSet<Word> result = new HashSet<Word>();
		try {
			if (sentences == null || sentences.isEmpty())
				return result;
		} catch (Exception e) {
			return result;
		}
		int lineNum = 0;
		for (Sentence sent : sentences) {
			lineNum++;
			try {
				if (sent == null)
					continue;
			} catch (Exception e) {
				continue;
			}
			Scanner sentScan = new Scanner(sent.getText());
			word: while (sentScan.hasNext()) {
				String next = sentScan.next();
				if (!Character.isLetter(next.charAt(0)))
					continue; // skip this one, not a letter
				next = next.toLowerCase().replaceAll("[^a-z]", ""); // remove all non-alpha chars
				for (Word wrd : result) {
					if (wrd.getText().equals(next)) { // took me forever to remember not to use ==... thanks java
						wrd.increaseTotal(sent.getScore());
						continue word; // increment the old word and head to the next word
					}
				}
				Word adder = new Word(next);
				adder.increaseTotal(sent.getScore()); //word constructor doesn't initialize, so I guess we have to
				if (result.add(adder) == false) {
					System.out.println(next + " erred at line " + lineNum); // should be impossible to get to
					return result;
				}
			}
			sentScan.close();
		}
		return result;
	}

	/*
	 * Implement this method in Part 3
	 */
	public static Map<String, Double> calculateScores(Set<Word> words) {
		Map<String, Double> result = new HashMap<String, Double>();
		for (Word word : words) {
			try {
				if (word == null)
					continue;
			} catch (Exception e) {
				continue;
			}
			result.put(word.getText(), word.calculateScore());
		}
		return result;
	}

	/*
	 * Implement this method in Part 4
	 */
	public static double calculateSentenceScore(Map<String, Double> wordScores, String sentence) {
		try {
			if (wordScores == null || wordScores.isEmpty() || sentence == null || sentence == "")
				return 0;
		} catch (Exception e) {
			return 0;
		}
		Scanner sentScan = new Scanner(sentence);
		double total = 0.0;
		int count = 0;
		while (sentScan.hasNext()) {
			String word = sentScan.next().toLowerCase();
			if (!Character.isLetter(word.charAt(0)))
				continue;
			word = word.replaceAll("[^a-z]", "");
			if (!wordScores.containsKey(word)) {
				count++;
				continue;
			}
			total += wordScores.get(word);
			// System.out.println(word + " : " + wordScores.get(word));
			count++;
		}
		sentScan.close();
		if (count == 0)
			return 0;
		return total / (double) count;
	}

	/*
	 * You do not need to modify this code but can use it for testing your program!
	 */
	public static void main(String[] args) {
		if (args.length == 0) {
			System.out.println("Please specify the name of the input file");
			System.exit(0);
		}
		String filename = args[0];
		System.out.print("Please enter a sentence: ");
		Scanner in = new Scanner(System.in);
		String sentence = in.nextLine();
		in.close();
		List<Sentence> sentences = Analyzer.readFile(filename);
//		for (Sentence sent : sentences) {
//			System.out.println(sent.getText());
//		}
		Set<Word> words = Analyzer.allWords(sentences);
//		for (Word word : words) {
//			System.out.println(word.getText() + ", cnt: " + word.getCount() + ", ttl: " + word.getTotal());
//		}
		Map<String, Double> wordScores = Analyzer.calculateScores(words);
		//System.out.println(wordScores);
		double score = Analyzer.calculateSentenceScore(wordScores, sentence);
		//System.out.println("The sentiment score is " + score);
	}
}
