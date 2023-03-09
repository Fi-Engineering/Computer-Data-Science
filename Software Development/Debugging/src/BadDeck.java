import java.util.ArrayList;
import java.util.HashMap;
import java.util.Random;

public class BadDeck {
	private ArrayList<Card> cards = new ArrayList<Card>();

	public BadDeck() {
		HashMap<Integer, String> cardMapping = new HashMap<Integer, String>();
		
		cardMapping.put(1, "Ace");
		cardMapping.put(11, "Jack");
		cardMapping.put(12, "Queen");
		cardMapping.put(13, "King");
		
		Card c = null;
		
		for (int i = 1; i <= 13; i++) {
			for (int j = 0; j < 4; j++) {
				String rank = "" + i;
				if (cardMapping.containsKey(i)) {
					rank = cardMapping.get(i);
				}
						
				if (j % 4 == 1) {
					c = new Card(rank, "Clubs");
				}
				if (j % 4 == 2) {
					c = new Card(rank, "Spades");
				}
				if (j % 4 == 3) {
					c = new Card(rank, "Hearts");
				}
				if (j % 4 == 0) {
					c = new Card(rank, "Diamonds");
				}
				cards.add(c);
			}
			
		}
	}

	public Card getTopCard() {
		return cards.get(0);
	}

	public void shuffle() {
		Random random = new Random();
		for (int i = 0; i < 52; i++) {
			int j = random.nextInt(52);
			cards.set(i, cards.get(j));
		}
	}
}
