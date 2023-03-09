package SpellChecker;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.Map.Entry;
import java.util.TreeMap;
import java.util.TreeSet;

public class WordRecommender {
	String filename;
	Dictionary dict;

	public WordRecommender(String fileName) {
		filename = fileName;
		dict = new Dictionary(filename);
	}

	public double getSimilarityMetric(String word1, String word2) {
		double leftSimilarity = 0.0;
		int biggerWord;
		if (word2.length() > word1.length()) {
			biggerWord = word2.length();
		} else {
			biggerWord = word1.length();
		}
		// biggerWord = word2.length() > word1.length() ? word2.length() :
		// word1.length();

		try {
			for (int i = 0; i < biggerWord; i++) {
				if (word1.charAt(i) == word2.charAt(i)) {
					leftSimilarity++;
				}
			}
		} catch (Exception e) {
		}

		double rightSimilarity = 0.0;
		StringBuilder word1Reversed = new StringBuilder(word1);
		StringBuilder word2Reversed = new StringBuilder(word2);
		word1Reversed.reverse();
		word2Reversed.reverse();
		try {
			for (int i = 0; i < biggerWord; i++) {
				if (word1Reversed.charAt(i) == word2Reversed.charAt(i)) {
					rightSimilarity++;
				}
			}
		} catch (Exception e) {
		}

		return (leftSimilarity + rightSimilarity) / 2;
	}

	public ArrayList<String> getWordSuggestions(String word, int n, double commonPercent, int topN) {
		ArrayList<String> suggestions = new ArrayList<String>();
		for (int i = 0; i < dict.listOfWords.size(); i++) {
			String dictWord = dict.listOfWords.get(i);
			if (((word.length() - n) <= dictWord.length()) && (dictWord.length() <= (word.length() + n))) {
				// word - n <= dictword <= word + n
				// first criteria met

				// second criteria:
				HashSet<String> lettersDictWord = new HashSet<String>(dictWord.length());
				HashSet<String> lettersWord = new HashSet<String>(word.length());

				for (int j = 0; j < dictWord.length(); j++) {
					lettersDictWord.add(dictWord.substring(j, j + 1)); // add 1st/2nd/3rd... characters to set
				}
				for (int k = 0; k < word.length(); k++) {
					lettersWord.add(word.substring(k, k + 1)); // add 1st/2nd/3rd... characters to set
				}

				HashSet<String> intersection = new HashSet<String>(lettersWord); // copy
				intersection.retainAll(lettersDictWord);
				HashSet<String> union = new HashSet<String>(lettersWord);
				union.addAll(lettersDictWord);

				double percent = 0.0;
				try {
					percent = (double) intersection.size() / (double) union.size();
				} catch (Exception e) { // catches trying to divide by zero, which means they aren't similar at all
					percent = 0;
				}
				if (percent >= commonPercent) {
					// second criteria met
					suggestions.add(dictWord);
				}
			}
		}

		ArrayList<SimilarityMetricWord> topNWords = new ArrayList<SimilarityMetricWord>();
		for (int i = 0; i < suggestions.size(); i++) {
			topNWords.add(new SimilarityMetricWord(getSimilarityMetric(word, suggestions.get(i)), suggestions.get(i)));
		}
		suggestions.clear(); // actual words now represented in topNWords, so fix suggestions instead of
								// making new

		SimilarityMetricWord[] topNWordsArray = new SimilarityMetricWord[topNWords.size()];
		for (int i = 0; i < topNWords.size(); i++) {
			topNWordsArray[i] = topNWords.get(i);
		}
		Arrays.sort(topNWordsArray, Collections.reverseOrder());

		try {
			for (int i = 0; i < topN; i++) {
				suggestions.add(topNWordsArray[i].toString());
			}
		} catch (Exception e) {
			; // nothing to do since this accounts for "if there are fewer than topN words"
		}
		return suggestions;
	}

	public ArrayList<String> getWordsWithCommonLetters(String word, ArrayList<String> listOfWords, int n) { // remove static later
		ArrayList<String> result = new ArrayList<String>();
		for (int i = 0; i < listOfWords.size(); i++) {
			String dictWord = listOfWords.get(i);
			HashSet<String> lettersDictWord = new HashSet<String>(dictWord.length());
			HashSet<String> lettersWord = new HashSet<String>(word.length());
			for (int j = 0; j < dictWord.length(); j++) {
				lettersDictWord.add(dictWord.substring(j, j + 1)); // add 1st/2nd/3rd... characters to set
			}
			for (int k = 0; k < word.length(); k++) {
				lettersWord.add(word.substring(k, k + 1));
			}
			HashSet<String> intersection = new HashSet<String>(lettersWord); // copy
			intersection.retainAll(lettersDictWord);
			if (intersection.size() >= n) {
				result.add(dictWord);
			}
		}
		return result;
	}

	public static String prettyPrint(ArrayList<String> list) {
		String output = "";
		for (int i = 0; i < list.size(); i++) {
			if (i == (list.size() - 1)) {
				return output + Integer.toString(i + 1) + ". " + list.get(i);
			}
			output += Integer.toString(i + 1) + ". " + list.get(i) + "\n";
		}
		return output;
	}
	
	//public static void main(String[] args) {
		//ArrayList<String> wordList = new ArrayList<String>(Arrays.asList("ban", "bang", "mange", "gang", "cling", "loo"));
	//System.out.println(prettyPrint(getWordsWithCommonLetters("cloong", wordList, 2)));
	//	System.out.println();
	//	System.out.print(prettyPrint(getWordsWithCommonLetters("cloong", wordList, 3)));
	//}
}
