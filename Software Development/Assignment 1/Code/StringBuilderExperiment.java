
public class StringBuilderExperiment {
	
	public static void main(String [] args) {
		StringBuilder sb = new StringBuilder("Alex Ilgenfritz");
		StringBuilder reversedSb = new StringBuilder(sb);
		System.out.println(sb);
		sb.deleteCharAt(0);
		sb.deleteCharAt(2);
		sb.delete(3,5);
		sb.deleteCharAt(2);
		sb.delete(3,sb.length());
		System.out.println(sb);
		System.out.println(reversedSb.toString() + reversedSb.reverse());
	}

}