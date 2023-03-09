public class BadBlackjack {
	public static void main(String[] args) {
		BadDeck deck = new BadDeck();
		deck.shuffle();
		deck.getTopCard().display();
	}

}
