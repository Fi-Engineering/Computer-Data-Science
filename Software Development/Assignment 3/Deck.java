public class Deck {

	public int usedCards;
	public Card[] deck;

	public Deck() {
		deck = new Card[52];
		int cardCount = 0; // Cards created so far
		for (int suit = 0; suit <= 3; suit++) {
			for (int value = 1; value <= 13; value++) {
				deck[cardCount] = new Card(value, suit);
				cardCount++;
			}
		}
	}

	public int cardsLeft() {
		return deck.length - usedCards;
	}

	public Card dealCard() {
		if (usedCards == deck.length)
			throw new IllegalStateException("No cards are left in the deck.");
		usedCards++;
		return deck[usedCards - 1];
	}

	public void shuffle() {
		for (int i = deck.length - 1; i > 0; i--) {
			int random = (int) (Math.random() * (i + 1));
			Card copy = deck[i]; // sets a Card named copy equal to the Card of the original deck in sequence
									// (makes a copy)
			deck[i] = deck[random]; // set card in sequence to random position in deck
			deck[random] = copy; // set random position's card to the copy we made, effectively swapping the
								// cards
		}
		usedCards = 0;
	}

}