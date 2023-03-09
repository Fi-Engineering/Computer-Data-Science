package SpellChecker;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Scanner;

import com.sun.istack.internal.Nullable;

public class RunSpellChecker {

	// returns what the user input. if there are expected values, it spits an error
	// until it gets one of them.
	public static String getChoice(ArrayList<String> expVals) {
		Scanner userInput = new Scanner(System.in);
		if (expVals.size() == 0) {
			return userInput.next();
		}
		while (true) {
			String inp = userInput.next();
			if (expVals.contains(inp))
				return inp;
			System.out.println("Invalid input. Please try again.");
		}
	}

	public static String check(File spellCheck) {
		WordRecommender wr = new WordRecommender("engDictionary.txt");
		Scanner fileScan;
		String output = "";
		try {
			fileScan = new Scanner(spellCheck);
			while (fileScan.hasNext()) {
				String word = fileScan.next();
				while (wr.dict.listOfWords.contains(word)) {
					output += " " + word;
					if (fileScan.hasNext())
						word = fileScan.next();
					else {
						fileScan.close();
						return output.trim();
					}
				}

				ArrayList<String> suggestions = new ArrayList<String>();
				suggestions = wr.getWordSuggestions(word, 1, 0.75, 3);

				if (suggestions.size() > 0) {
					System.out.println("'" + word + "' is misspelled.");
					System.out.println("The following suggestions are available:");
					System.out.println(wr.prettyPrint(suggestions));
					System.out.println("Press 'r' for replace, 'a' for accept as is, 't' for type in manually.");
					String chc = getChoice(new ArrayList<String>(Arrays.asList("r", "a", "t")));
					switch (chc) {
					case "r":
						System.out.println("Your word will now be replaced with one of the suggestions.");
						System.out.println(
								"Enter the number corresponding to the word that you want to use for replacement.");
						ArrayList<String> numSuggestionsAsStringArr = new ArrayList<String>();
						// conv suggestions size to str arr containing every number up to that
						for (int i = 1; i <= suggestions.size(); i++) {
							numSuggestionsAsStringArr.add(Integer.toString(i));
						}
						int num = Integer.parseInt(getChoice(numSuggestionsAsStringArr)); // expect only one of these
						output += " " + suggestions.get(num - 1);
						break;
					case "a":
						output += " " + word;
						break;
					case "t":
						System.out.println(
								"Please type the word that will be used as the replacement in the output file.");
						String manualEntry = getChoice(new ArrayList<String>()); // no particular value expctd
						output += " " + manualEntry;
						break;
					}
				} else {
					System.out.println("'" + word + "' is misspelled.");
					System.out.println("There are 0 suggestions in our dictionary for this word.");
					System.out.println("Press 'a' for accept as is, 't' for type in manually.");
					String chc = getChoice(new ArrayList<String>(Arrays.asList("a", "t")));
					switch (chc) {
					case "a":
						output += " " + word;
						break;
					case "t":
						System.out.println(
								"Please type the word that will be used as the replacement in the output file.");
						String manualEntry = getChoice(new ArrayList<String>()); // no particular value expctd
						output += " " + manualEntry;
						break;
					}
				}
			}
			fileScan.close();
		} catch (FileNotFoundException e) {
			System.out.println("No file found.");
			return "";
		}
		return output.trim();
	}

	public static void main(String[] args) {
		String fileName = "";
		File spellCheck = null;
		
		while (true) {
			System.out.println("Please enter a file to spell check.");
			fileName = getChoice(new ArrayList<String>());
			spellCheck = new File(fileName);
			if (!spellCheck.exists())
				System.out.println("File does not exist. Try again.");
			else
				break;
		}
		
		String newFileText = check(spellCheck);
		File newFile = null;
		if (fileName.indexOf(".") != -1) {
			String[] nm = fileName.split("\\.");
			newFile = new File(nm[0] + "_chk." + nm[1]);
		} else {
			newFile = new File(fileName + "_chk");
		}
		
		PrintWriter writer;
		try {
			writer = new PrintWriter(newFile);
			writer.print(newFileText);
			writer.close();
		} catch (FileNotFoundException e) {
			System.out.println("Couldn't print to file.");
			e.printStackTrace();
		}
		System.out.println("Successfully output spell-checked file to '" + newFile.getAbsolutePath() + "'");
	}
}
