package SpellChecker;

public class SimilarityMetricWord implements Comparable<SimilarityMetricWord> {
	double similarity = 0.0;
	String text = null;

	public SimilarityMetricWord(double sim, String txt) {
		similarity = sim;
		text = txt;
	}
	
	@Override
	public int compareTo(SimilarityMetricWord otherWord) {
		if (this.similarity > otherWord.similarity)
			return 1;
		if (this.similarity < otherWord.similarity)
			return -1;
		return 0;
	}
	
	@Override
	public String toString() {
		return text;
	}
}
