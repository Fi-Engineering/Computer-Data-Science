
public class Slot {
	Card cardHeld;
	StringBuilder text = new StringBuilder(3); //String representation of the Card
	
	public Slot(Card cardToHold) {
		cardHeld = cardToHold;
		
		switch (cardHeld.rank) {
		case Card.ACE:
			text.append("A ");
			break;
		case 2:
			text.append("2 ");
			break;
		case 3:
			text.append("3 ");
			break;
		case 4:
			text.append("4 ");
			break;
		case 5:
			text.append("5 ");
			break;
		case 6:
			text.append("6 ");
			break;
		case 7:
			text.append("7 ");
			break;
		case 8:
			text.append("8 ");
			break;
		case 9:
			text.append("9 ");
			break;
		case 10:
			text.append("10");
			break;
		case Card.JACK:
			text.append("J ");
			break;
		case Card.QUEEN:
			text.append("Q ");
			break;
		case Card.KING:
			text.append("K ");
			break;
		}
		
		switch (cardHeld.suit) {
		case Card.SPADES:
			text.append('S');
			break;
		case Card.HEARTS:
			text.append('H');
			break;
		case Card.DIAMONDS:
			text.append('D');
			break;
		case Card.CLUBS:
			text.append('C');
			break;
		}
	}
	
	public Slot() {
		cardHeld = null;
	}
	
	public String toString() {
		return text.toString();
	}
}
