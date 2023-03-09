import java.util.Scanner;

public class EasterSunday {
	public static void main(String [] args) {
		Scanner userInputScanner = new Scanner(System.in);
		System.out.println("What is the current year?");
		int currentYear = Integer.parseInt(userInputScanner.nextLine());
		userInputScanner.close();
		int a = currentYear % 19;
		int b = (int) Math.floor(currentYear / 100);
		int c = currentYear % 100;
		int  d = (int) Math.floor(b / 4);
		int  e = b % 4;
		int  f = (int) Math.floor((b + 8) / 25);
		int  g = (int) Math.floor((b - f + 1) / 3);
		int  h = (19 * a + b - d - g + 15) % 30;
		int  i = (int) Math.floor(c / 4);
		int  k = c % 4;
		int  l = (32 + 2 * e + 2 * i - h - k) % 7;
		int  m = (int) Math.floor((a + 11 * h + 22 * l) / 451);
		int  month = (int)  Math.floor((h + l - 7 * m + 114) / 31);
		int  day = ((h + l - 7 * m + 114) % 31) + 1;
		String monthAsString = "April";
		if (month == 3) monthAsString = "March";
		System.out.println("Easter Sunday for " + currentYear + " is on " + monthAsString + " " + day);
	}
}
