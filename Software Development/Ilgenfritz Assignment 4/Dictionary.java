package SpellChecker;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Scanner;

public class Dictionary {
	String filename;
	ArrayList<String> listOfWords = new ArrayList<String>();

	public Dictionary(String file) {
		File dict = new File(file);
		filename = file;

		Scanner fileParser;
		try {
			fileParser = new Scanner(dict);
			String word = null;

			while (fileParser.hasNextLine()) {
				word = fileParser.nextLine();
				listOfWords.add(word);
			}
			fileParser.close();
		} catch (FileNotFoundException e) {
			System.out.println("Dictionary not found.");
		}

	}
}
