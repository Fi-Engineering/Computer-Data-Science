public class Dog {
	String name;
	String breed;
	int age;
	double weight;

	public Dog(String dogName, String dogBreed) {
		name = dogName;
		breed = dogBreed;
		weight = 125;
		age = 0;
	}

	public String getBreed() {
		return breed;
	}

	public String getName() {
		return name;
	}

	public int getAge() {
		return age;
	}

	public double getWeight() {
		return weight;
	}

	public void eat() {
		weight = weight + 0.1;
	}

	public void rename(String newName) {
		name = newName;
	}

	public void hasBirthday() {
		System.out.println("happy birthday");
		age++;
	}

}
