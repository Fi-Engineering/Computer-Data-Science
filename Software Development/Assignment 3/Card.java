
public class Card {
	public final static int SPADES = 0;
	public final static int HEARTS = 1;
	public final static int DIAMONDS = 2;
	public final static int CLUBS = 3;

	public final static int JACK = 11;
	public final static int QUEEN = 12;
	public final static int KING = 13;
	public final static int ACE = 1;

	public int suit;
	public int rank;
	public int value; //blackjack value

	public Card(int rankCard, int suitCard) {
		rank = rankCard;
		suit = suitCard;
		if (rank >= 10) {
			value = 10;
		}
		else {
			value = rank;
		}
	}

	public int getSuit() {
		return suit;
	}

	public int getRank() {
		return rank;
	}

	public int getBlackjackValue() {
		return value;
	}
}
