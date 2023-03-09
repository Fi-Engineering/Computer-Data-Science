public class Card {
	private String suit;
	private String value;
	
	public Card(String v, String s) {
		suit = s;
		value = v;
	}
	
	public void display() {
		System.out.println(value + "  " + suit);
	}
}
