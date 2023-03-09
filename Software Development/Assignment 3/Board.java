
public class Board {
	Slot[] gameBoard = new Slot[16];
	Slot[] discardPile = new Slot[4];

	void resetBoard() {
		for (int i = 0; i < gameBoard.length; i++) {
			gameBoard[i] = new Slot();
			gameBoard[i].text.append((i + 1) + " ");
			if ((i + 1) < 10) {
				gameBoard[i].text.append(" ");
			}
		}
	}

	void getBoardStatus() {
		for (int i = 0; i < 5; i++) {
			System.out.print(gameBoard[i] + "\t");
		}
		System.out.println("");
		for (int i = 5; i < 10; i++) {
			System.out.print(gameBoard[i] + "\t");
		}
		System.out.println("");
		System.out.print("\t");
		for (int i = 10; i < 13; i++) {
			System.out.print(gameBoard[i] + "\t");
		}
		System.out.println("");
		System.out.print("\t");
		for (int i = 13; i < 16; i++) {
			System.out.print(gameBoard[i] + "\t");
		}
		System.out.println("");
		
	}
	
	public static void main(String[] args) {
		Board myBoard = new Board();
		myBoard.resetBoard();
		myBoard.getBoardStatus();
	}
}
